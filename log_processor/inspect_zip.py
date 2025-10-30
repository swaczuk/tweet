#!/usr/bin/env python3
"""
Script para inspeccionar el contenido de un ZIP y ver formato real de los logs.
"""
import zipfile
import sys
import os
import tempfile
import shutil
from pathlib import Path

def extract_nested_zips(zip_path: str, extract_dir: str):
    """Extrae ZIPs recursivamente y devuelve lista de archivos .txt"""
    txt_files = []

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_dir)

        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)

                if file.endswith('.zip'):
                    # Extraer ZIP anidado recursivamente
                    nested_dir = os.path.join(root, file + '_extracted')
                    os.makedirs(nested_dir, exist_ok=True)
                    txt_files.extend(extract_nested_zips(file_path, nested_dir))
                elif file.endswith('.txt'):
                    txt_files.append(file_path)

    return txt_files

def inspect_zip(zip_path: str, num_lines: int = 20):
    """Inspecciona archivos dentro del ZIP"""

    print(f"Inspeccionando: {zip_path}")
    print("="*80)

    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp(prefix='inspect_zip_')

    try:
        # Extraer ZIPs anidados
        print("\nExtrayendo ZIPs anidados...")
        txt_files = extract_nested_zips(zip_path, temp_dir)

        print(f"\nArchivos .txt encontrados: {len(txt_files)}")

        if not txt_files:
            print("\n⚠️  No se encontraron archivos .txt")
            return

        # Mostrar lista de archivos .txt
        print(f"\n{'='*80}")
        print("ARCHIVOS .TXT ENCONTRADOS:")
        print(f"{'='*80}")
        for i, txt_file in enumerate(txt_files, 1):
            size_kb = os.path.getsize(txt_file) / 1024
            print(f"{i}. {os.path.basename(txt_file)}")
            print(f"   Tamaño: {size_kb:.1f} KB")
            print(f"   Ruta: {txt_file}")

        # Analizar el primer archivo .txt no vacío
        print(f"\n{'='*80}")
        print(f"CONTENIDO DEL PRIMER ARCHIVO NO VACÍO (primeras {num_lines} líneas):")
        print(f"{'='*80}")

        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                if len(lines) > 0 and any(line.strip() for line in lines):
                    print(f"\nArchivo: {os.path.basename(txt_file)}")
                    print(f"Total de líneas: {len(lines)}")
                    print(f"\nPrimeras {num_lines} líneas:")
                    print("-"*80)

                    for i, line in enumerate(lines[:num_lines], 1):
                        if line.strip():
                            print(f"{i:3d}| {line[:200].rstrip()}")  # Mostrar primeros 200 caracteres

                    # Analizar formato
                    print(f"\n{'='*80}")
                    print("ANÁLISIS DE FORMATO:")
                    print(f"{'='*80}")

                    non_empty_lines = [l for l in lines if l.strip()]
                    if non_empty_lines:
                        first_line = non_empty_lines[0].strip()
                        print(f"\nPrimera línea completa:")
                        print(first_line)

                        print(f"\nCaracterísticas:")
                        print(f"  - Longitud: {len(first_line)} caracteres")
                        has_quotes = '"' in first_line
                        print(f"  - Contiene comillas dobles: {'Sí' if has_quotes else 'No'}")
                        quote_count = first_line.count('"')
                        print(f"  - Número de comillas: {quote_count}")
                        is_ip = first_line.split()[0].replace('.', '').isdigit() if first_line.split() else False
                        print(f"  - Comienza con IP: {'Sí' if is_ip else 'No'}")
                        has_method = 'GET' in first_line or 'POST' in first_line
                        print(f"  - Contiene 'GET' o 'POST': {'Sí' if has_method else 'No'}")

                        # Buscar User-Agent común
                        if '"' in first_line:
                            parts = first_line.split('"')
                            print(f"\n  - Partes entre comillas: {len(parts)}")
                            for i, part in enumerate(parts):
                                if part.strip():
                                    print(f"    Parte {i}: {part[:100]}")

                    break  # Solo mostrar el primer archivo con contenido
            except Exception as e:
                continue

        # Buscar patterns de bots en todo el archivo
        print(f"\n{'='*80}")
        print("BÚSQUEDA DE BOTS:")
        print(f"{'='*80}")

        bot_keywords = [
            'Googlebot', 'bingbot', 'GPTBot', 'ChatGPT',
            'Claude', 'Perplexity', 'bot', 'Bot', 'crawler',
            'spider', 'Pingdom', 'Incapsula'
        ]

        for txt_file in txt_files[:5]:  # Solo primeros 5 archivos
            try:
                with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                bot_lines = []
                for line in lines[:1000]:  # Primeras 1000 líneas
                    for keyword in bot_keywords:
                        if keyword in line:
                            bot_lines.append((keyword, line[:200].rstrip()))
                            break

                if bot_lines:
                    print(f"\n{os.path.basename(txt_file)}:")
                    print(f"  Encontradas {len(bot_lines)} líneas con bots")
                    print(f"  Ejemplos:")
                    for keyword, line in bot_lines[:3]:
                        print(f"    [{keyword}] {line}")
            except:
                continue

    finally:
        # Limpiar directorio temporal
        print(f"\n{'='*80}")
        print(f"Limpiando archivos temporales...")
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python inspect_zip.py <archivo.zip> [num_lineas]")
        print("\nEjemplo:")
        print("  python inspect_zip.py September2025.zip")
        print("  python inspect_zip.py September2025.zip 50")
        sys.exit(1)

    zip_path = sys.argv[1]
    num_lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    if not os.path.exists(zip_path):
        print(f"❌ Error: Archivo no encontrado: {zip_path}")
        sys.exit(1)

    inspect_zip(zip_path, num_lines)
