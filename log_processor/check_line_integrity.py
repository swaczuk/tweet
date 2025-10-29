#!/usr/bin/env python3
"""
Script para verificar si las líneas están cortadas en el archivo.
También intenta reconstruir líneas multi-línea.
"""
import sys
import re


def analyze_line_integrity(file_path):
    """Analiza si las líneas están completas o truncadas"""
    print("="*80)
    print("ANÁLISIS DE INTEGRIDAD DE LÍNEAS")
    print("="*80)

    complete_lines = 0
    incomplete_lines = 0
    empty_ua_lines = 0

    incomplete_samples = []

    # Patrón simple para detectar si una línea está completa
    # Una línea completa debe terminar con comillas después del user agent
    complete_pattern = re.compile(r'"[^"]*"\s*$')

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            if not line:
                continue

            # Verificar si la línea termina apropiadamente
            if complete_pattern.search(line):
                complete_lines += 1
            elif line.endswith('""'):
                # Línea con user agent vacío (válida)
                empty_ua_lines += 1
                complete_lines += 1
            else:
                # Línea parece incompleta/truncada
                incomplete_lines += 1
                if len(incomplete_samples) < 10:
                    incomplete_samples.append((line_num, line))

    total = complete_lines + incomplete_lines

    print(f"\n📊 ESTADÍSTICAS:")
    print("-"*80)
    print(f"  Líneas completas:    {complete_lines:,} ({complete_lines/total*100:.1f}%)")
    print(f"    └─ Con UA vacío:   {empty_ua_lines:,}")
    print(f"  Líneas incompletas:  {incomplete_lines:,} ({incomplete_lines/total*100:.1f}%)")
    print(f"  Total:               {total:,}")

    if incomplete_samples:
        print(f"\n❌ EJEMPLOS DE LÍNEAS INCOMPLETAS/TRUNCADAS:")
        print("-"*80)
        for line_num, line in incomplete_samples:
            print(f"\nLínea {line_num}:")
            # Mostrar el final de la línea
            print(f"  Termina con: ...{line[-80:]}")

            # Ver si tiene comillas al final
            if '"' in line[-50:]:
                print(f"  ⚠️  Tiene comillas pero formato inusual")
            else:
                print(f"  ⚠️  No termina con comillas - probablemente truncada")

    return incomplete_lines / total if total > 0 else 0


def count_multiline_entries(file_path):
    """Intenta detectar si hay entradas que ocupan múltiples líneas"""
    print("\n" + "="*80)
    print("ANÁLISIS DE ENTRADAS MULTI-LÍNEA")
    print("="*80)

    lines = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # Buscar líneas que no empiezan con IP (probable continuación)
    continuation_lines = 0
    continuation_samples = []

    ip_pattern = re.compile(r'^\d+\.\d+\.\d+\.\d+')

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        if not ip_pattern.match(line):
            continuation_lines += 1
            if len(continuation_samples) < 5:
                continuation_samples.append((i, line))

    print(f"\nLíneas que NO empiezan con IP: {continuation_lines}")

    if continuation_samples:
        print(f"\nEjemplos de posibles líneas de continuación:")
        print("-"*80)
        for line_num, line in continuation_samples:
            print(f"Línea {line_num}: {line[:100]}")

    return continuation_lines


def try_multiline_parsing(file_path):
    """Intenta leer el archivo juntando líneas cortadas"""
    print("\n" + "="*80)
    print("INTENTANDO RECONSTRUIR LÍNEAS MULTI-LÍNEA")
    print("="*80)

    reconstructed = []
    current_line = ""
    line_count = 0

    # Patrón para detectar inicio de línea válida
    start_pattern = re.compile(r'^\d+\.\d+\.\d+\.\d+ - - \d{2}/\d{2}/\d{4}')

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.rstrip('\n\r')

            if start_pattern.match(line):
                # Nueva entrada de log
                if current_line:
                    reconstructed.append(current_line)
                current_line = line
                line_count += 1
            else:
                # Continuación de la línea anterior
                current_line += " " + line

        # Agregar la última línea
        if current_line:
            reconstructed.append(current_line)

    print(f"\nLíneas originales en archivo: {line_count}")
    print(f"Líneas después de reconstrucción: {len(reconstructed)}")
    print(f"Diferencia: {line_count - len(reconstructed)}")

    if line_count != len(reconstructed):
        print(f"\n⚠️  Se detectaron {line_count - len(reconstructed)} líneas que eran continuaciones")
        print(f"   El archivo tiene entradas multi-línea que necesitan ser reconstruidas")

        # Mostrar ejemplo
        print(f"\nEjemplo de línea reconstruida:")
        print("-"*80)
        for recon_line in reconstructed[:3]:
            if len(recon_line) > 200:  # Línea larga, probablemente reconstruida
                print(f"Longitud: {len(recon_line)} caracteres")
                print(f"Inicio: {recon_line[:100]}...")
                print(f"Final: ...{recon_line[-100:]}")
                print()
                break

    return reconstructed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python check_line_integrity.py <archivo_log.txt>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Análisis 1: Verificar integridad de líneas
    incomplete_ratio = analyze_line_integrity(file_path)

    # Análisis 2: Detectar líneas de continuación
    continuation_count = count_multiline_entries(file_path)

    # Análisis 3: Intentar reconstruir
    reconstructed = try_multiline_parsing(file_path)

    print("\n" + "="*80)
    print("CONCLUSIÓN")
    print("="*80)

    if incomplete_ratio > 0.5:
        print("❌ MÁS DEL 50% de líneas están incompletas/truncadas")
        print("   Esto explica por qué el parsing está fallando")
        print("\nPosibles causas:")
        print("  1. El archivo fue exportado/procesado incorrectamente")
        print("  2. Las líneas originalmente tienen saltos de línea en medio")
        print("  3. El archivo fue truncado al exportar")

        if continuation_count > 0:
            print(f"\n✅ SOLUCIÓN: Usar el parser multi-línea")
            print(f"   Encontramos {continuation_count} líneas de continuación")
            print(f"   El parser necesita juntar estas líneas antes de procesar")
    else:
        print("✅ La mayoría de líneas están completas")
        print("   El problema NO es el formato del archivo")
        print("   Revisar patrones de bots o user agents")

    print()
