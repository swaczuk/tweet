#!/usr/bin/env python3
"""
Script de prueba para validar el parser de logs
"""
import sys
from log_parser import LogParser


def test_parser():
    """Prueba el parser con el archivo de logs de prueba"""
    print("="*80)
    print("TEST DEL PARSER DE LOGS")
    print("="*80)

    # Crear parser
    parser = LogParser()

    # Archivo de prueba
    test_file = "test_logs.txt"

    print(f"\nParseando archivo: {test_file}")
    print("-"*80)

    # Parsear archivo
    entries = parser.parse_file(test_file)

    print(f"\n✅ Total de entradas de bots encontradas: {len(entries)}")

    if not entries:
        print("\n❌ No se encontraron entradas de bots. Verifica el formato del log.")
        return

    # Mostrar las primeras 5 entradas
    print("\n" + "="*80)
    print("PRIMERAS 5 ENTRADAS PARSEADAS:")
    print("="*80)
    for i, entry in enumerate(entries[:5], 1):
        print(f"\nEntrada {i}:")
        print(f"  IP: {entry.ip}")
        print(f"  Fecha: {entry.date}")
        print(f"  Timestamp: {entry.timestamp}")
        print(f"  Bot: {entry.bot_name}")
        print(f"  Región: {entry.region}")
        print(f"  URL: {entry.url}")
        print(f"  Status: {entry.status_code}")

    # Estadísticas por bot
    print("\n" + "="*80)
    print("ESTADÍSTICAS POR BOT:")
    print("="*80)
    bot_counts = {}
    for entry in entries:
        bot_counts[entry.bot_name] = bot_counts.get(entry.bot_name, 0) + 1

    for bot, count in sorted(bot_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {bot}: {count} hits")

    # Estadísticas por región
    print("\n" + "="*80)
    print("ESTADÍSTICAS POR REGIÓN:")
    print("="*80)
    region_counts = {}
    for entry in entries:
        region_counts[entry.region] = region_counts.get(entry.region, 0) + 1

    for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {region}: {count} hits")

    # Estadísticas por fecha
    print("\n" + "="*80)
    print("ESTADÍSTICAS POR FECHA:")
    print("="*80)
    date_counts = {}
    for entry in entries:
        date_counts[entry.date] = date_counts.get(entry.date, 0) + 1

    for date, count in sorted(date_counts.items()):
        print(f"  {date}: {count} hits")

    # Mostrar combinaciones bot + región
    print("\n" + "="*80)
    print("HITS POR REGIÓN Y BOT:")
    print("="*80)
    region_bot_counts = {}
    for entry in entries:
        key = f"{entry.region} - {entry.bot_name}"
        region_bot_counts[key] = region_bot_counts.get(key, 0) + 1

    for key, count in sorted(region_bot_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {key}: {count} hits")

    print("\n" + "="*80)
    print("✅ TEST COMPLETADO EXITOSAMENTE")
    print("="*80)


def test_single_line():
    """Prueba el parser con líneas individuales"""
    print("\n" + "="*80)
    print("TEST DE LÍNEAS INDIVIDUALES")
    print("="*80)

    parser = LogParser()

    # Líneas de prueba
    test_lines = [
        '10.201.52.5 - - 25/09/2025 08:05:31 PM "GET https://www.ajg.com/uk/small-business-insurance/ HTTP/1.1" 200 100 100  "" "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot"',
        '10.201.52.6 - - 25/09/2025 08:10:15 PM "GET https://www.ajg.com/au/insurance/business HTTP/1.1" 200 150 200  "" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"',
        '10.201.52.7 - - 26/09/2025 10:00:00 AM "GET https://www.rpsins.com/services HTTP/1.1" 200 120 180  "" "Mozilla/5.0 (compatible; GPTBot/1.0; +https://openai.com/gptbot)"',
    ]

    for i, line in enumerate(test_lines, 1):
        print(f"\nLínea {i}:")
        print(f"  Input: {line[:80]}...")

        entry = parser.parse_line(line)
        if entry:
            print(f"  ✅ Parseada correctamente")
            print(f"     Bot: {entry.bot_name}")
            print(f"     Región: {entry.region}")
            print(f"     Fecha: {entry.date}")
            print(f"     URL: {entry.url[:60]}...")
        else:
            print(f"  ❌ No se pudo parsear")


if __name__ == "__main__":
    test_parser()
    test_single_line()
