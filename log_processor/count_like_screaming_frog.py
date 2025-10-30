#!/usr/bin/env python3
"""
Replica diferentes formas de contar que usa Screaming Frog Log File Analyzer
"""
import sys
from log_parser import LogParser


def count_like_screaming_frog(file_path, region_pattern='ajg.com/uk/'):
    """
    Cuenta de diferentes maneras para ver cuál coincide con Screaming Frog
    """
    print("="*80)
    print(f"REPLICANDO CONTEOS DE SCREAMING FROG PARA: {region_pattern}")
    print("="*80)

    parser = LogParser()
    import re
    region_regex = re.compile(region_pattern, re.IGNORECASE)

    # Diferentes contadores
    total_requests = 0
    status_200_all = 0
    status_200_with_ua = 0
    status_200_bots = 0
    status_200_humans = 0
    unique_urls = set()
    unique_urls_200 = set()
    status_codes = {}

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or not region_regex.search(line):
                continue

            total_requests += 1

            match = parser.LOG_PATTERN.match(line)
            if not match:
                continue

            data = match.groupdict()
            status = data['status']
            url = data['url']
            ua = data.get('user_agent') or data.get('user_agent_noq') or ''

            # Contar por status code
            status_codes[status] = status_codes.get(status, 0) + 1

            # URLs únicas
            unique_urls.add(url)

            # Solo status 200
            if status == '200':
                status_200_all += 1
                unique_urls_200.add(url)

                # Status 200 con UA
                if ua and ua.strip():
                    status_200_with_ua += 1

                    # Es bot?
                    if parser.identify_bot(ua):
                        status_200_bots += 1
                    else:
                        status_200_humans += 1

    print(f"\n📊 DIFERENTES FORMAS DE CONTAR (como Screaming Frog):")
    print("="*80)

    print(f"\n1️⃣  TOTAL REQUESTS (sin filtros):")
    print(f"    {total_requests:,} requests")

    print(f"\n2️⃣  UNIQUE URLs (todas, sin filtrar):")
    print(f"    {len(unique_urls):,} URLs únicas")

    print(f"\n3️⃣  STATUS 200 ONLY (exitosos):")
    print(f"    {status_200_all:,} requests")

    print(f"\n4️⃣  STATUS 200 + WITH USER AGENT:")
    print(f"    {status_200_with_ua:,} requests")

    print(f"\n5️⃣  STATUS 200 + UNIQUE URLs:")
    print(f"    {len(unique_urls_200):,} URLs únicas")

    print(f"\n6️⃣  STATUS 200 + BOTS ONLY:")
    print(f"    {status_200_bots:,} requests")

    print(f"\n7️⃣  STATUS 200 + HUMANS ONLY:")
    print(f"    {status_200_humans:,} requests")

    print(f"\n📋 DESGLOSE POR STATUS CODE:")
    print("="*80)
    for status, count in sorted(status_codes.items(), key=lambda x: x[1], reverse=True):
        print(f"    {status}: {count:,} requests")

    print(f"\n" + "="*80)
    print(f"🎯 COMPARACIÓN CON SCREAMING FROG:")
    print("="*80)
    print(f"\nSi Screaming Frog muestra 446, podría ser:")

    matches = []
    sf_value = 446  # El valor que ve el usuario

    if abs(total_requests - sf_value) < 10:
        matches.append(f"  ✅ Total requests ({total_requests})")
    if abs(len(unique_urls) - sf_value) < 10:
        matches.append(f"  ✅ Unique URLs ({len(unique_urls)})")
    if abs(status_200_all - sf_value) < 10:
        matches.append(f"  ✅ Status 200 only ({status_200_all})")
    if abs(status_200_with_ua - sf_value) < 10:
        matches.append(f"  ✅ Status 200 + User Agent ({status_200_with_ua})")
    if abs(len(unique_urls_200) - sf_value) < 10:
        matches.append(f"  ✅ Status 200 unique URLs ({len(unique_urls_200)})")
    if abs(status_200_bots - sf_value) < 10:
        matches.append(f"  ✅ Status 200 + Bots only ({status_200_bots})")
    if abs(status_200_humans - sf_value) < 10:
        matches.append(f"  ✅ Status 200 + Humans only ({status_200_humans})")

    if matches:
        print("\n" + "\n".join(matches))
    else:
        print(f"\n  ❓ Ninguno de estos valores coincide exactamente con 446")
        print(f"     Screaming Frog puede tener filtros adicionales activos")

    print(f"\n💡 Para saber exactamente qué cuenta Screaming Frog:")
    print(f"   1. Ve a Configuration → Log File → muéstrame qué filtros están activos")
    print(f"   2. Dime qué columna/campo muestra '446'")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python count_like_screaming_frog.py <archivo_log.txt> [patron_region]")
        sys.exit(1)

    file_path = sys.argv[1]
    region_pattern = sys.argv[2] if len(sys.argv) > 2 else 'ajg.com/uk/'

    count_like_screaming_frog(file_path, region_pattern)
