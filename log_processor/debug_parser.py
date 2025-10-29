#!/usr/bin/env python3
"""
Script de debugging para identificar problemas en el parsing de logs.
Muestra líneas que no se parsean y por qué.
"""
import sys
import re
from log_parser import LogParser


def analyze_log_file(file_path):
    """Analiza un archivo de log en detalle"""
    print("="*80)
    print("ANÁLISIS DETALLADO DEL LOG")
    print("="*80)

    parser = LogParser()

    total_lines = 0
    parsed_lines = 0
    bot_lines = 0
    non_bot_lines = 0
    failed_lines = 0

    failed_samples = []
    non_bot_samples = []
    bot_samples = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1
            line = line.strip()

            if not line:
                continue

            # Intentar parsear
            entry = parser.parse_line(line)

            if entry:
                # Línea parseada exitosamente
                parsed_lines += 1
                if entry.bot_name:
                    bot_lines += 1
                    if len(bot_samples) < 5:
                        bot_samples.append((line_num, line, entry))
                else:
                    non_bot_lines += 1
                    if len(non_bot_samples) < 5:
                        non_bot_samples.append((line_num, line))
            else:
                # Línea NO parseada
                failed_lines += 1
                if len(failed_samples) < 10:
                    failed_samples.append((line_num, line))

    # Mostrar resultados
    print(f"\n📊 ESTADÍSTICAS:")
    print("-"*80)
    print(f"  Total de líneas:          {total_lines:,}")
    print(f"  Líneas parseadas:         {parsed_lines:,} ({parsed_lines/total_lines*100:.1f}%)")
    print(f"    └─ Bots detectados:     {bot_lines:,} ({bot_lines/total_lines*100:.1f}%)")
    print(f"    └─ No bots (ignoradas): {non_bot_lines:,} ({non_bot_lines/total_lines*100:.1f}%)")
    print(f"  ❌ Líneas NO parseadas:   {failed_lines:,} ({failed_lines/total_lines*100:.1f}%)")

    # Mostrar muestras de líneas de bots
    if bot_samples:
        print(f"\n✅ EJEMPLOS DE LÍNEAS DE BOTS PARSEADAS:")
        print("-"*80)
        for line_num, line, entry in bot_samples:
            print(f"\nLínea {line_num}:")
            print(f"  Bot: {entry.bot_name}")
            print(f"  Región: {entry.region}")
            print(f"  URL: {entry.url[:60]}...")
            print(f"  Raw: {line[:100]}...")

    # Mostrar muestras de líneas que NO parsearon
    if failed_samples:
        print(f"\n❌ EJEMPLOS DE LÍNEAS QUE NO SE PARSEARON:")
        print("-"*80)
        for line_num, line in failed_samples:
            print(f"\nLínea {line_num}:")
            print(f"  {line[:150]}")

            # Intentar identificar por qué falló
            print("  Análisis:")
            if not re.search(r'\d+\.\d+\.\d+\.\d+', line):
                print("    ⚠️  No se encontró una IP válida")
            if not re.search(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} (?:AM|PM)', line):
                print("    ⚠️  No se encontró timestamp en formato DD/MM/YYYY HH:MM:SS AM/PM")
            if not re.search(r'"GET|POST|HEAD|PUT|DELETE', line):
                print("    ⚠️  No se encontró método HTTP")
            if not re.search(r'HTTP/\d\.\d', line):
                print("    ⚠️  No se encontró versión HTTP")
            if not re.search(r'" \d{3} ', line):
                print("    ⚠️  No se encontró código de status")

    # Análisis de user agents
    if failed_samples:
        print(f"\n🔍 BUSCANDO PATRONES EN LÍNEAS FALLIDAS:")
        print("-"*80)

        # Buscar user agents manualmente
        for line_num, line in failed_samples[:3]:
            # Intentar extraer user agent manualmente
            match = re.search(r'"([^"]*)"[^"]*$', line)
            if match:
                user_agent = match.group(1)
                print(f"\nLínea {line_num} - User Agent encontrado:")
                print(f"  {user_agent}")
            else:
                print(f"\nLínea {line_num} - No se pudo extraer User Agent")

    # Advertencias
    if failed_lines > total_lines * 0.1:
        print(f"\n⚠️  ADVERTENCIA: Más del 10% de líneas no se parsearon!")
        print(f"   Esto indica que el regex necesita ajustes.")

    if bot_lines < parsed_lines * 0.05:
        print(f"\n⚠️  ADVERTENCIA: Muy pocos bots detectados (<5% de líneas parseadas)")
        print(f"   Verifica los patrones de bots o que el archivo contenga tráfico de bots.")

    print("\n" + "="*80)

    return {
        'total_lines': total_lines,
        'parsed_lines': parsed_lines,
        'bot_lines': bot_lines,
        'failed_lines': failed_lines,
        'failed_samples': failed_samples
    }


def test_regex_variations(file_path):
    """Prueba variaciones del regex para ver cuál captura más líneas"""
    print("\n" + "="*80)
    print("PROBANDO VARIACIONES DEL REGEX")
    print("="*80)

    # Regex original
    regex_original = re.compile(
        r'(?P<ip>[\d\.]+) - - '
        r'(?P<timestamp>\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} (?:AM|PM)) '
        r'"(?P<method>\w+) (?P<url>\S+) HTTP/[^"]+" '
        r'(?P<status>\d+) (?P<size1>\d+) (?P<size2>\d+)\s+'
        r'"[^"]*" "(?P<user_agent>[^"]*)"'
    )

    # Regex más flexible (permite espacios variables)
    regex_flexible = re.compile(
        r'(?P<ip>[\d\.]+)\s+-\s+-\s+'
        r'(?P<timestamp>\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\s+(?:AM|PM))\s+'
        r'"(?P<method>\w+)\s+(?P<url>\S+)\s+HTTP/[^"]+"\s+'
        r'(?P<status>\d+)\s+(?P<size1>\d+)\s+(?P<size2>\d+)\s+'
        r'"[^"]*"\s+"(?P<user_agent>[^"]*)"'
    )

    # Regex ultra flexible
    regex_ultra = re.compile(
        r'(?P<ip>[\d\.]+)\s+-\s+-\s+'
        r'(?P<timestamp>\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+(?:AM|PM))\s+'
        r'"(?P<method>\w+)\s+(?P<url>\S+)\s+HTTP/[^"]+"\s+'
        r'(?P<status>\d+)\s+(?P<size1>[\d-]+)\s+(?P<size2>[\d-]+)\s*'
        r'"[^"]*"\s+"(?P<user_agent>[^"]*)"'
    )

    regexes = [
        ("Original", regex_original),
        ("Flexible", regex_flexible),
        ("Ultra Flexible", regex_ultra)
    ]

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [line.strip() for line in f if line.strip()]

    print(f"\nTotal de líneas no vacías: {len(lines)}")
    print("-"*80)

    for name, regex in regexes:
        matches = sum(1 for line in lines if regex.match(line))
        percentage = matches / len(lines) * 100
        print(f"{name:20s}: {matches:5d} líneas ({percentage:5.1f}%)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python debug_parser.py <archivo_log.txt>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Análisis principal
    results = analyze_log_file(file_path)

    # Probar variaciones del regex
    if results['failed_lines'] > 0:
        test_regex_variations(file_path)

    print("\n💡 RECOMENDACIONES:")
    print("-"*80)
    if results['failed_lines'] > results['total_lines'] * 0.1:
        print("  1. El regex necesita ajustes - muchas líneas no se parsean")
        print("  2. Revisa los ejemplos de líneas fallidas arriba")
        print("  3. Compara con las líneas exitosas para ver las diferencias")

    if results['bot_lines'] < results['parsed_lines'] * 0.05:
        print("  1. Pocos bots detectados - verifica los patrones de User-Agent")
        print("  2. Revisa la lista de bots en log_parser.py")
        print("  3. Usa --custom-bots para agregar patrones específicos")

    print()
