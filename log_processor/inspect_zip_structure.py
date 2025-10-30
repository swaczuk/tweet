#!/usr/bin/env python3
"""
Script para ver la estructura completa de un ZIP con todos sus niveles
"""
import zipfile
import sys
import os
import tempfile
import shutil
from pathlib import Path

def show_zip_structure(zip_path: str, indent: str = ""):
    """Muestra estructura de un ZIP recursivamente"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for item in zf.namelist():
                size = zf.getinfo(item).file_size / 1024
                print(f"{indent}{item} ({size:.1f} KB)")
    except Exception as e:
        print(f"{indent}Error leyendo ZIP: {e}")

def count_all_files(zip_path: str, temp_base: str, level: int = 0):
    """Cuenta todos los archivos recursivamente"""
    txt_count = 0
    zip_count = 0

    indent = "  " * level

    try:
        # Crear directorio temporal para este nivel
        temp_dir = os.path.join(temp_base, f"level_{level}")
        os.makedirs(temp_dir, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            print(f"{indent}📦 {os.path.basename(zip_path)}")

            # Extraer todo
            zf.extractall(temp_dir)

            # Buscar archivos
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, temp_dir)

                    if file.endswith('.txt'):
                        size = os.path.getsize(file_path) / 1024
                        print(f"{indent}  📄 {rel_path} ({size:.1f} KB)")
                        txt_count += 1
                    elif file.endswith('.zip'):
                        print(f"{indent}  📦 {rel_path} (ZIP anidado)")
                        zip_count += 1
                        # Procesar ZIP anidado recursivamente
                        sub_txt, sub_zip = count_all_files(file_path, temp_base, level + 1)
                        txt_count += sub_txt
                        zip_count += sub_zip

            print(f"{indent}  → {txt_count} archivos .txt en este nivel")

    except Exception as e:
        print(f"{indent}Error procesando {zip_path}: {e}")

    return txt_count, zip_count

def main():
    if len(sys.argv) < 2:
        print("Uso: python inspect_zip_structure.py <archivo.zip>")
        sys.exit(1)

    zip_path = sys.argv[1]

    if not os.path.exists(zip_path):
        print(f"❌ Error: Archivo no encontrado: {zip_path}")
        sys.exit(1)

    print("="*80)
    print(f"ESTRUCTURA DEL ZIP: {zip_path}")
    print("="*80)

    # Mostrar estructura sin extraer
    print("\n1. CONTENIDO DEL ZIP PRINCIPAL:")
    print("-"*80)
    show_zip_structure(zip_path)

    # Contar archivos extrayendo todo recursivamente
    print("\n" + "="*80)
    print("2. EXTRACCIÓN RECURSIVA COMPLETA:")
    print("="*80 + "\n")

    temp_base = tempfile.mkdtemp(prefix='inspect_structure_')

    try:
        total_txt, total_zip = count_all_files(zip_path, temp_base)

        print("\n" + "="*80)
        print("RESUMEN:")
        print("="*80)
        print(f"Total de archivos .txt encontrados: {total_txt}")
        print(f"Total de archivos .zip anidados: {total_zip}")

    finally:
        print("\nLimpiando archivos temporales...")
        shutil.rmtree(temp_base, ignore_errors=True)

if __name__ == "__main__":
    main()
