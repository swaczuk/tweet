#!/usr/bin/env python3
"""
Script para inspeccionar el contenido de un ZIP y ver formato real de los logs.
"""
import zipfile
import sys
import os
from pathlib import Path

def inspect_zip(zip_path: str, num_lines: int = 20):
    """Inspecciona archivos dentro del ZIP"""

    print(f"Inspeccionando: {zip_path}")
    print("="*80)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Listar todos los archivos
        all_files = zf.namelist()
        txt_files = [f for f in all_files if f.endswith('.txt')]

        print(f"\nTotal de archivos en ZIP: {len(all_files)}")
        print(f"Archivos .txt encontrados: {len(txt_files)}")

        if not txt_files:
            print("\n⚠️  No se encontraron archivos .txt")
            return

        # Mostrar lista de archivos .txt
        print(f"\n{'='*80}")
        print("ARCHIVOS .TXT EN EL ZIP:")
        print(f"{'='*80}")
        for i, txt_file in enumerate(txt_files, 1):
            file_info = zf.getinfo(txt_file)
            size_kb = file_info.file_size / 1024
            print(f"{i}. {txt_file}")
            print(f"   Tamaño: {size_kb:.1f} KB")

        # Analizar el primer archivo .txt no vacío
        print(f"\n{'='*80}")
        print(f"CONTENIDO DEL PRIMER ARCHIVO NO VACÍO (primeras {num_lines} líneas):")
        print(f"{'='*80}")

        for txt_file in txt_files:
            with zf.open(txt_file) as f:
                lines = []
                try:
                    content = f.read().decode('utf-8', errors='ignore')
                    lines = content.split('\n')
                except:
                    continue

                if len(lines) > 0 and any(line.strip() for line in lines):
                    print(f"\nArchivo: {txt_file}")
                    print(f"Total de líneas: {len(lines)}")
                    print(f"\nPrimeras {num_lines} líneas:")
                    print("-"*80)

                    for i, line in enumerate(lines[:num_lines], 1):
                        if line.strip():
                            print(f"{i:3d}| {line[:200]}")  # Mostrar primeros 200 caracteres

                    # Analizar formato
                    print(f"\n{'='*80}")
                    print("ANÁLISIS DE FORMATO:")
                    print(f"{'='*80}")

                    non_empty_lines = [l for l in lines if l.strip()]
                    if non_empty_lines:
                        first_line = non_empty_lines[0]
                        print(f"\nPrimera línea completa:")
                        print(first_line)

                        print(f"\nCaracterísticas:")
                        print(f"  - Longitud: {len(first_line)} caracteres")
                        print(f"  - Contiene comillas dobles: {'Sí' if '\"' in first_line else 'No'}")
                        print(f"  - Número de comillas: {first_line.count('\"')}")
                        print(f"  - Comienza con IP: {'Sí' if first_line.split()[0].replace('.', '').isdigit() else 'No'}")
                        print(f"  - Contiene 'GET' o 'POST': {'Sí' if 'GET' in first_line or 'POST' in first_line else 'No'}")

                        # Buscar User-Agent común
                        if '"' in first_line:
                            parts = first_line.split('"')
                            print(f"\n  - Partes entre comillas: {len(parts)}")
                            for i, part in enumerate(parts):
                                if part.strip():
                                    print(f"    Parte {i}: {part[:100]}")

                    break  # Solo mostrar el primer archivo con contenido

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
            with zf.open(txt_file) as f:
                try:
                    content = f.read().decode('utf-8', errors='ignore')
                    lines = content.split('\n')

                    bot_lines = []
                    for line in lines[:1000]:  # Primeras 1000 líneas
                        for keyword in bot_keywords:
                            if keyword in line:
                                bot_lines.append((keyword, line[:200]))
                                break

                    if bot_lines:
                        print(f"\n{txt_file}:")
                        print(f"  Encontradas {len(bot_lines)} líneas con bots")
                        print(f"  Ejemplos:")
                        for keyword, line in bot_lines[:3]:
                            print(f"    [{keyword}] {line}")
                except:
                    continue


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
