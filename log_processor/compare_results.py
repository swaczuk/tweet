#!/usr/bin/env python3
"""
Script para comparar resultados detallados y identificar discrepancias.
Útil para comparar con otras herramientas.
"""
import sys
from log_parser import LogParser
from collections import defaultdict


def detailed_analysis(file_path):
    """Análisis detallado por bot y región"""
    print("="*80)
    print("ANÁLISIS DETALLADO POR BOT Y REGIÓN")
    print("="*80)

    parser = LogParser()
    entries = parser.parse_file(file_path)

    if not entries:
        print("❌ No se encontraron entradas de bots")
        return

    # Análisis por región y bot
    region_bot_urls = defaultdict(lambda: defaultdict(set))
    region_bot_hits = defaultdict(lambda: defaultdict(int))

    for entry in entries:
        region_bot_urls[entry.region][entry.bot_name].add(entry.url)
        region_bot_hits[entry.region][entry.bot_name] += 1

    # Mostrar resultados
    print(f"\n📊 Total de hits de bots: {len(entries):,}")
    print("="*80)

    for region in sorted(region_bot_urls.keys()):
        print(f"\n🌍 REGIÓN: {region}")
        print("-"*80)

        region_total = sum(region_bot_hits[region].values())
        print(f"Total de hits en región: {region_total:,}")

        for bot in sorted(region_bot_hits[region].keys(), key=lambda b: region_bot_hits[region][b], reverse=True):
            hits = region_bot_hits[region][bot]
            unique_urls = len(region_bot_urls[region][bot])
            print(f"\n  🤖 {bot}:")
            print(f"     Total de hits: {hits:,}")
            print(f"     URLs únicas: {unique_urls:,}")

            # Mostrar top 5 URLs más visitadas de este bot en esta región
            url_counts = defaultdict(int)
            for entry in entries:
                if entry.region == region and entry.bot_name == bot:
                    url_counts[entry.url] += 1

            top_urls = sorted(url_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            if top_urls:
                print(f"     Top 5 URLs:")
                for i, (url, count) in enumerate(top_urls, 1):
                    url_short = url if len(url) <= 60 else url[:57] + "..."
                    print(f"       {i}. [{count:3d}] {url_short}")

    # Resumen por bot (todas las regiones)
    print("\n" + "="*80)
    print("📊 RESUMEN GLOBAL POR BOT")
    print("="*80)

    bot_totals = defaultdict(int)
    bot_urls = defaultdict(set)
    for entry in entries:
        bot_totals[entry.bot_name] += 1
        bot_urls[entry.bot_name].add(entry.url)

    for bot in sorted(bot_totals.keys(), key=lambda b: bot_totals[b], reverse=True):
        print(f"\n🤖 {bot}:")
        print(f"   Total de hits: {bot_totals[bot]:,}")
        print(f"   URLs únicas: {len(bot_urls[bot]):,}")
        print(f"   Regiones:")
        for region in sorted(region_bot_hits.keys()):
            if bot in region_bot_hits[region]:
                hits = region_bot_hits[region][bot]
                print(f"     • {region}: {hits:,} hits")

    # Análisis de URLs específicas
    print("\n" + "="*80)
    print("🔍 ANÁLISIS DE URLS ESPECÍFICAS")
    print("="*80)

    # Buscar URLs de UK específicamente
    uk_entries = [e for e in entries if 'UK' in e.region]
    if uk_entries:
        print(f"\n📍 URLs de UK (incluyendo GB-UK):")
        print(f"   Total de hits: {len(uk_entries):,}")

        uk_by_bot = defaultdict(int)
        for entry in uk_entries:
            uk_by_bot[entry.bot_name] += 1

        print(f"   Por bot:")
        for bot, count in sorted(uk_by_bot.items(), key=lambda x: x[1], reverse=True):
            print(f"     • {bot}: {count:,} hits")

    # Buscar específicamente ChatGPT en UK
    chatgpt_uk = [e for e in entries if e.bot_name == 'ChatGPT' and 'UK' in e.region]
    if chatgpt_uk:
        print(f"\n🤖 ChatGPT en UK específicamente:")
        print(f"   Total de hits: {len(chatgpt_uk):,}")

        url_counts = defaultdict(int)
        for entry in chatgpt_uk:
            url_counts[entry.url] += 1

        print(f"   URLs únicas: {len(url_counts):,}")
        print(f"   Top 10 URLs:")
        for i, (url, count) in enumerate(sorted(url_counts.items(), key=lambda x: x[1], reverse=True)[:10], 1):
            url_short = url if len(url) <= 60 else url[:57] + "..."
            print(f"     {i:2d}. [{count:3d}] {url_short}")

    print("\n" + "="*80)


def check_user_agents(file_path):
    """Busca todos los user agents únicos en el archivo"""
    print("\n" + "="*80)
    print("🔍 ANÁLISIS DE USER AGENTS")
    print("="*80)

    user_agents = defaultdict(int)
    bot_user_agents = defaultdict(int)
    total_lines = 0

    import re
    # Regex simple solo para extraer user agent
    ua_pattern = re.compile(r'"([^"]*)"[^"]*$')

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            total_lines += 1
            line = line.strip()
            if not line:
                continue

            match = ua_pattern.search(line)
            if match:
                ua = match.group(1)
                user_agents[ua] += 1

                # Buscar posibles bots
                ua_lower = ua.lower()
                if any(bot_term in ua_lower for bot_term in ['bot', 'crawler', 'spider', 'gpt', 'claude', 'perplexity', 'crawl']):
                    bot_user_agents[ua] += 1

    print(f"\nTotal de líneas: {total_lines:,}")
    print(f"User Agents únicos: {len(user_agents):,}")
    print(f"User Agents que parecen bots: {len(bot_user_agents):,}")

    print(f"\n📊 TOP 20 USER AGENTS (por frecuencia):")
    print("-"*80)
    for i, (ua, count) in enumerate(sorted(user_agents.items(), key=lambda x: x[1], reverse=True)[:20], 1):
        ua_short = ua if len(ua) <= 70 else ua[:67] + "..."
        is_bot = "🤖" if any(bot_term in ua.lower() for bot_term in ['bot', 'crawler', 'spider', 'gpt', 'claude', 'perplexity']) else "  "
        print(f"{i:2d}. {is_bot} [{count:5d}] {ua_short}")

    # Buscar específicamente variaciones de ChatGPT
    print(f"\n🔍 BUSCANDO VARIACIONES DE CHATGPT:")
    print("-"*80)
    chatgpt_variants = [ua for ua in user_agents.keys() if 'gpt' in ua.lower() or 'chatgpt' in ua.lower() or 'openai' in ua.lower()]
    if chatgpt_variants:
        for ua in chatgpt_variants:
            print(f"  [{user_agents[ua]:5d}] {ua}")
    else:
        print("  No se encontraron variaciones de ChatGPT")

    print("\n" + "="*80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python compare_results.py <archivo_log.txt>")
        sys.exit(1)

    file_path = sys.argv[1]

    detailed_analysis(file_path)
    check_user_agents(file_path)

    print("\n💡 Para comparar con otra herramienta:")
    print("-"*80)
    print("  1. Busca en los números de arriba el bot y región específicos")
    print("  2. Compara con los números de tu otra herramienta")
    print("  3. Si hay discrepancia grande, ejecuta debug_parser.py para ver líneas no parseadas")
    print()
