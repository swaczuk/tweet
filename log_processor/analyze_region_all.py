#!/usr/bin/env python3
"""
Análisis específico de requests a una región (ej: UK)
Compara con herramientas como Screaming Frog que cuentan TODO el tráfico
"""
import sys
import re
from log_parser import LogParser


def analyze_region_all_traffic(file_path, region_pattern):
    """
    Analiza TODOS los requests a una región, no solo bots

    Args:
        file_path: Ruta al archivo de log
        region_pattern: Patrón para identificar la región (ej: 'ajg.com/uk/')
    """
    print("="*80)
    print(f"ANÁLISIS COMPLETO DE TRÁFICO PARA: {region_pattern}")
    print("="*80)

    parser = LogParser()

    total_requests = 0
    bot_requests = 0
    human_requests = 0
    empty_ua_requests = 0
    no_match_requests = 0

    bots_found = {}
    human_browsers = {}
    urls_found = set()

    # Compilar patrón de región
    region_regex = re.compile(region_pattern, re.IGNORECASE)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Verificar si la línea contiene la región
            if not region_regex.search(line):
                continue

            total_requests += 1

            # Intentar parsear la línea
            match = parser.LOG_PATTERN.match(line)
            if not match:
                no_match_requests += 1
                continue

            data = match.groupdict()
            url = data['url']
            urls_found.add(url)

            # Obtener user agent
            user_agent = data.get('user_agent') or data.get('user_agent_noq') or ''

            if not user_agent or user_agent.strip() == '':
                empty_ua_requests += 1
                continue

            # Verificar si es bot
            bot_name = parser.identify_bot(user_agent)
            if bot_name:
                bot_requests += 1
                bots_found[bot_name] = bots_found.get(bot_name, 0) + 1
            else:
                human_requests += 1
                # Extraer navegador (simplificado)
                if 'Chrome' in user_agent:
                    browser = 'Chrome'
                elif 'Safari' in user_agent and 'Chrome' not in user_agent:
                    browser = 'Safari'
                elif 'Firefox' in user_agent:
                    browser = 'Firefox'
                elif 'Edge' in user_agent:
                    browser = 'Edge'
                else:
                    browser = 'Other'
                human_browsers[browser] = human_browsers.get(browser, 0) + 1

    # Mostrar resultados
    print(f"\n📊 RESUMEN:")
    print("-"*80)
    print(f"  Total de requests:        {total_requests:,}")
    print(f"    └─ Requests de BOTS:    {bot_requests:,} ({bot_requests/total_requests*100:.1f}%)")
    print(f"    └─ Requests de HUMANOS: {human_requests:,} ({human_requests/total_requests*100:.1f}%)")
    print(f"    └─ Sin User Agent:      {empty_ua_requests:,} ({empty_ua_requests/total_requests*100:.1f}%)")
    print(f"    └─ No parseados:        {no_match_requests:,}")
    print(f"  URLs únicas visitadas:    {len(urls_found):,}")

    print(f"\n🤖 DESGLOSE POR BOT:")
    print("-"*80)
    if bots_found:
        for bot, count in sorted(bots_found.items(), key=lambda x: x[1], reverse=True):
            print(f"  {bot:25s}: {count:4d} requests")
    else:
        print("  (No se detectaron bots)")

    print(f"\n👤 DESGLOSE POR NAVEGADOR (Tráfico Humano):")
    print("-"*80)
    if human_browsers:
        for browser, count in sorted(human_browsers.items(), key=lambda x: x[1], reverse=True):
            print(f"  {browser:25s}: {count:4d} requests")
    else:
        print("  (No se detectó tráfico humano)")

    print(f"\n📝 COMPARACIÓN CON SCREAMING FROG:")
    print("-"*80)
    print(f"  Screaming Frog cuenta:    TODO el tráfico (bots + humanos + sin UA)")
    print(f"  Nuestro parser cuenta:    Solo bots")
    print(f"\n  Total en este análisis:   {total_requests:,} requests")
    print(f"  Solo bots:                {bot_requests:,} requests")
    print(f"\n  Si Screaming Frog muestra {total_requests:,}, eso coincide con nuestro análisis ✅")

    # Mostrar top 10 URLs
    print(f"\n🔝 TOP 10 URLs MÁS VISITADAS EN ESTA REGIÓN:")
    print("-"*80)

    # Contar requests por URL
    url_counts = {}
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if not region_regex.search(line):
                continue
            match = parser.LOG_PATTERN.match(line.strip())
            if match:
                url = match.groupdict()['url']
                url_counts[url] = url_counts.get(url, 0) + 1

    for i, (url, count) in enumerate(sorted(url_counts.items(), key=lambda x: x[1], reverse=True)[:10], 1):
        url_display = url if len(url) <= 60 else url[:57] + "..."
        print(f"  {i:2d}. [{count:3d}] {url_display}")

    print("\n" + "="*80)
    return total_requests, bot_requests


def compare_with_grep(file_path, region_pattern):
    """Verificación manual con grep"""
    print("\n" + "="*80)
    print("VERIFICACIÓN MANUAL (equivalente a grep)")
    print("="*80)

    import subprocess

    print(f"\nContando manualmente líneas que contienen '{region_pattern}'...")

    try:
        # Contar con grep
        result = subprocess.run(
            ['grep', '-c', region_pattern, file_path],
            capture_output=True,
            text=True
        )
        grep_count = int(result.stdout.strip()) if result.returncode == 0 else 0
        print(f"  Total (grep -c):          {grep_count:,}")

        # Contar bots con grep
        result = subprocess.run(
            f'grep "{region_pattern}" "{file_path}" | grep -i "bot\\|crawler\\|spider" | wc -l',
            shell=True,
            capture_output=True,
            text=True
        )
        bot_count = int(result.stdout.strip())
        print(f"  Con 'bot' en UA (grep):   {bot_count:,}")

    except Exception as e:
        print(f"  (grep no disponible o error: {e})")

    print("\n" + "="*80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python analyze_region_all.py <archivo_log.txt> [patron_region]")
        print("\nEjemplos:")
        print("  python analyze_region_all.py logs.txt 'ajg.com/uk/'")
        print("  python analyze_region_all.py logs.txt 'ajg.com/au/'")
        print("  python analyze_region_all.py logs.txt 'rpsins.com'")
        sys.exit(1)

    file_path = sys.argv[1]
    region_pattern = sys.argv[2] if len(sys.argv) > 2 else 'ajg.com/uk/'

    total, bots = analyze_region_all_traffic(file_path, region_pattern)
    compare_with_grep(file_path, region_pattern)

    print("\n💡 CONCLUSIÓN:")
    print("="*80)
    print(f"Si Screaming Frog muestra ~{total} requests para esta región,")
    print(f"y nosotros detectamos {bots} bots, ambos números son CORRECTOS.")
    print(f"\nScreening Frog cuenta: TODO el tráfico")
    print(f"Nuestro parser cuenta: Solo bots")
    print("\nPara que nuestro parser cuente TODO el tráfico como Screaming Frog,")
    print("necesitaríamos modificar el código para NO filtrar por bots.")
    print()
