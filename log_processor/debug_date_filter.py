#!/usr/bin/env python3
"""
Debug del filtro de fechas para ver qué está pasando
"""
import sys
from datetime import datetime
from log_parser import LogParser
import re


def debug_date_filtering(file_path, region_pattern, bot_name, start_date_str, end_date_str):
    """
    Analiza por qué el filtro de fechas puede no estar funcionando
    """
    print("="*80)
    print("DEBUG DEL FILTRO DE FECHAS")
    print("="*80)

    parser = LogParser()
    region_regex = re.compile(region_pattern, re.IGNORECASE)

    # Parsear fechas objetivo
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")

    print(f"\nFiltro de fechas:")
    print(f"  Start: {start_dt} ({start_date_str})")
    print(f"  End:   {end_dt} ({end_date_str})")

    # Contadores
    total_chatgpt_uk = 0
    total_chatgpt_uk_200 = 0
    urls_before_range = set()
    urls_in_range = set()
    urls_after_range = set()

    date_parse_errors = 0
    dates_found = set()

    print(f"\nAnalizando archivo...")

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or not region_regex.search(line):
                continue

            match = parser.LOG_PATTERN.match(line)
            if not match:
                continue

            data = match.groupdict()

            # Verificar bot
            ua = data.get('user_agent') or data.get('user_agent_noq') or ''
            if not ua:
                continue

            detected_bot = parser.identify_bot(ua)
            if not detected_bot or detected_bot.lower() != bot_name.lower():
                continue

            total_chatgpt_uk += 1

            if data['status'] == '200':
                total_chatgpt_uk_200 += 1

            # Parsear fecha
            timestamp = data['timestamp']
            try:
                # Formato: "09/09/2025 03:02:19 AM"
                log_date = datetime.strptime(timestamp, "%d/%m/%Y %I:%M:%S %p")
                dates_found.add(log_date.strftime("%Y-%m-%d"))

                url = data['url']

                if log_date < start_dt:
                    urls_before_range.add(url)
                elif log_date > end_dt:
                    urls_after_range.add(url)
                else:
                    urls_in_range.add(url)

            except Exception as e:
                date_parse_errors += 1
                if date_parse_errors <= 3:
                    print(f"  Error parseando fecha línea {line_num}: {timestamp} - {e}")

    # Resultados
    print("\n" + "="*80)
    print("RESULTADOS DEL DEBUG:")
    print("="*80)

    print(f"\n📊 Total de requests de {bot_name} en UK (sin filtro de fecha):")
    print(f"  Total: {total_chatgpt_uk}")
    print(f"  Con status 200: {total_chatgpt_uk_200}")

    print(f"\n📅 Fechas encontradas en los logs:")
    sorted_dates = sorted(dates_found)
    if sorted_dates:
        print(f"  Primera fecha: {sorted_dates[0]}")
        print(f"  Última fecha: {sorted_dates[-1]}")
        print(f"  Total de días: {len(sorted_dates)}")
        if len(sorted_dates) <= 10:
            print(f"  Fechas: {', '.join(sorted_dates)}")
    else:
        print("  ⚠️  No se encontraron fechas válidas")

    print(f"\n📊 URLs por rango de fecha:")
    print(f"  Antes de {start_date_str}: {len(urls_before_range)} URLs únicas")
    print(f"  Dentro del rango: {len(urls_in_range)} URLs únicas")
    print(f"  Después de {end_date_str}: {len(urls_after_range)} URLs únicas")

    print(f"\n⚠️  Errores al parsear fechas: {date_parse_errors}")

    print("\n" + "="*80)
    print("ANÁLISIS:")
    print("="*80)

    if len(urls_in_range) == 0 and (len(urls_before_range) > 0 or len(urls_after_range) > 0):
        print("\n❌ PROBLEMA: Todas las URLs están FUERA del rango de fechas")
        print(f"   El rango {start_date_str} a {end_date_str} no contiene datos")
        print(f"   Las fechas reales en el log son: {sorted_dates[0]} a {sorted_dates[-1]}")
    elif len(urls_in_range) < len(urls_before_range) + len(urls_after_range):
        print("\n⚠️  ADVERTENCIA: Muchas URLs están fuera del rango de fechas")
        print(f"   Verifica que el rango de fechas sea correcto")
    else:
        print(f"\n✅ El filtro de fechas parece estar funcionando")
        print(f"   {len(urls_in_range)} URLs en el rango")

    # Mostrar algunas URLs para debug
    if urls_in_range:
        print(f"\n📝 Primeras 5 URLs dentro del rango:")
        for url in list(urls_in_range)[:5]:
            print(f"  - {url[:70]}...")

    print()


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python debug_date_filter.py <archivo.txt> <region> <bot> <start_date> <end_date>")
        print("\nEjemplo:")
        print("  python debug_date_filter.py logs.txt 'ajg.com/uk/' ChatGPT 2025-09-02 2025-10-01")
        sys.exit(1)

    file_path = sys.argv[1]
    region = sys.argv[2]
    bot = sys.argv[3]
    start_date = sys.argv[4]
    end_date = sys.argv[5]

    debug_date_filtering(file_path, region, bot, start_date, end_date)
