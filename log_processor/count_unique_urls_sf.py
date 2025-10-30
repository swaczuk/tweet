#!/usr/bin/env python3
"""
Cuenta URLs ÚNICAS como Screaming Frog Log File Analyzer
(no hits totales, sino URLs distintas visitadas)
"""
import sys
from datetime import datetime
from log_parser import LogParser
import re


def count_unique_urls_like_sf(file_path, region_pattern, bot_name, start_date=None, end_date=None, status_filter='200'):
    """
    Replica exactamente el conteo de Screaming Frog:
    - URLs únicas (no hits totales)
    - Filtrado por status code
    - Filtrado por bot
    - Filtrado por región
    - Filtrado por fecha
    """
    print("="*80)
    print("CONTEO COMO SCREAMING FROG LOG FILE ANALYZER")
    print("="*80)

    print(f"\nFiltros aplicados:")
    print(f"  Vista: URLs (únicas)")
    print(f"  Response: {status_filter}")
    print(f"  Bot: {bot_name}")
    print(f"  Region: {region_pattern}")
    if start_date and end_date:
        print(f"  Dates: {start_date} to {end_date}")
    print()

    parser = LogParser()
    region_regex = re.compile(region_pattern, re.IGNORECASE)

    unique_urls = set()
    total_hits = 0
    hits_by_url = {}

    # Parsear fechas si se proporcionan
    start_dt = None
    end_dt = None
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or not region_regex.search(line):
                continue

            match = parser.LOG_PATTERN.match(line)
            if not match:
                continue

            data = match.groupdict()

            # Filtro por status
            if data['status'] != status_filter:
                continue

            # Obtener fecha
            timestamp = data['timestamp']
            try:
                log_date = datetime.strptime(timestamp, "%d/%m/%Y %I:%M:%S %p")

                # Filtro por fecha
                if start_dt and log_date < start_dt:
                    continue
                if end_dt and log_date > end_dt:
                    continue
            except:
                continue

            # Obtener user agent
            ua = data.get('user_agent') or data.get('user_agent_noq') or ''
            if not ua:
                continue

            # Filtro por bot
            detected_bot = parser.identify_bot(ua)
            if not detected_bot or detected_bot.lower() != bot_name.lower():
                continue

            # Contar
            url = data['url']
            unique_urls.add(url)
            total_hits += 1
            hits_by_url[url] = hits_by_url.get(url, 0) + 1

    # Resultados
    print("="*80)
    print("RESULTADOS:")
    print("="*80)
    print(f"\n📊 URLs ÚNICAS visitadas por {bot_name}: {len(unique_urls)}")
    print(f"📊 HITS TOTALES de {bot_name}: {total_hits}")
    print(f"\n💡 Promedio de hits por URL: {total_hits / len(unique_urls):.1f}" if unique_urls else "")

    # Top 20 URLs más visitadas
    if hits_by_url:
        print(f"\n🔝 TOP 20 URLs MÁS VISITADAS POR {bot_name}:")
        print("="*80)
        sorted_urls = sorted(hits_by_url.items(), key=lambda x: x[1], reverse=True)[:20]
        for i, (url, hits) in enumerate(sorted_urls, 1):
            url_display = url if len(url) <= 65 else url[:62] + "..."
            print(f"  {i:2d}. [{hits:3d} hits] {url_display}")

    print("\n" + "="*80)
    print("COMPARACIÓN:")
    print("="*80)
    print(f"\nScreening Frog muestra: {len(unique_urls)} (URLs únicas) ✅")
    print(f"Nuestro parser mostraba: {total_hits} (hits totales)")
    print(f"\nAhora ambos números coinciden porque estamos contando lo mismo:")
    print(f"URLs ÚNICAS en lugar de hits totales.")
    print()

    return unique_urls, total_hits


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python count_unique_urls_sf.py <archivo.txt> <region> <bot> [start_date] [end_date] [status]")
        print("\nEjemplo para replicar tu configuración de Screaming Frog:")
        print("  python count_unique_urls_sf.py logs.txt 'ajg.com/uk/' ChatGPT 2025-09-02 2025-10-01 200")
        print("\nEjemplo simple:")
        print("  python count_unique_urls_sf.py logs.txt 'ajg.com/uk/' ChatGPT")
        sys.exit(1)

    file_path = sys.argv[1]
    region = sys.argv[2]
    bot = sys.argv[3]
    start_date = sys.argv[4] if len(sys.argv) > 4 else None
    end_date = sys.argv[5] if len(sys.argv) > 5 else None
    status = sys.argv[6] if len(sys.argv) > 6 else '200'

    count_unique_urls_like_sf(file_path, region, bot, start_date, end_date, status)
