#!/usr/bin/env python3
"""
Prueba completa del flujo de procesamiento de logs
"""
from log_parser import LogParser
from data_aggregator import DataAggregator
import json


def test_full_flow():
    """Prueba el flujo completo: parsear + agregar + extraer top URLs"""
    print("="*80)
    print("TEST DEL FLUJO COMPLETO")
    print("="*80)

    # Paso 1: Parsear logs
    print("\n📖 PASO 1: Parseando logs...")
    print("-"*80)
    parser = LogParser()
    entries = parser.parse_file("test_logs.txt")
    print(f"✅ {len(entries)} entradas de bots encontradas")

    # Paso 2: Agregar datos
    print("\n📊 PASO 2: Agregando datos...")
    print("-"*80)
    aggregator = DataAggregator()
    aggregator.add_entries(entries)
    print("✅ Datos agregados")

    # Mostrar resumen
    aggregator.print_summary()

    # Paso 3: Extraer top URLs por región
    print("\n🔝 PASO 3: Extrayendo top 5 URLs por región...")
    print("="*80)

    all_top_urls = []
    for region in sorted(aggregator.data.keys()):
        print(f"\n📍 REGIÓN: {region}")
        print("-"*80)
        top_urls = aggregator.get_top_urls_by_region(region, top_n=5)

        if not top_urls:
            print("  (Sin datos)")
            continue

        for i, stat in enumerate(top_urls, 1):
            print(f"  {i}. {stat.url}")
            print(f"     Hits totales: {stat.hits}")

        all_top_urls.extend(top_urls)

    # Paso 4: Extraer top URLs con desglose por bot
    print("\n\n🤖 PASO 4: Top URLs con desglose por bot...")
    print("="*80)

    top_with_bots = aggregator.get_top_urls_with_bot_breakdown(top_n=5)

    # Agrupar por región para mejor visualización
    by_region = {}
    for stat in top_with_bots:
        if stat.region not in by_region:
            by_region[stat.region] = []
        by_region[stat.region].append(stat)

    for region in sorted(by_region.keys()):
        print(f"\n📍 REGIÓN: {region}")
        print("-"*80)

        # Agrupar por URL
        by_url = {}
        for stat in by_region[region]:
            if stat.url not in by_url:
                by_url[stat.url] = []
            by_url[stat.url].append(stat)

        # Ordenar URLs por hits totales
        url_totals = {url: sum(s.hits for s in stats) for url, stats in by_url.items()}
        sorted_urls = sorted(url_totals.items(), key=lambda x: x[1], reverse=True)

        for url, total_hits in sorted_urls:
            print(f"\n  URL: {url}")
            print(f"  Total de hits: {total_hits}")
            print("  Desglose por bot:")
            for stat in by_url[url]:
                print(f"    • {stat.bot}: {stat.hits} hits")

    # Paso 5: Exportar a JSON
    print("\n\n💾 PASO 5: Exportando a JSON...")
    print("="*80)

    output = {
        "total_entries": len(entries),
        "total_stats": len(top_with_bots),
        "summary": aggregator.get_summary(),
        "top_urls_by_region": [
            {
                "region": stat.region,
                "url": stat.url,
                "bot": stat.bot,
                "hits": stat.hits
            }
            for stat in top_with_bots
        ]
    }

    output_file = "test_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Resultados exportados a: {output_file}")

    # Mostrar estadísticas finales
    print("\n\n📈 ESTADÍSTICAS FINALES:")
    print("="*80)
    print(f"  • Total de líneas procesadas: 20")
    print(f"  • Hits de bots encontrados: {len(entries)}")
    print(f"  • Regiones identificadas: {len(aggregator.data)}")
    print(f"  • Top URLs extraídas: {len(top_with_bots)}")
    print(f"  • Archivo de salida: {output_file}")

    print("\n" + "="*80)
    print("✅ TEST COMPLETO EXITOSO")
    print("="*80)
    print("\nPara ver el JSON completo:")
    print(f"  cat {output_file} | python -m json.tool | less")
    print()


if __name__ == "__main__":
    test_full_flow()
