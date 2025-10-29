#!/usr/bin/env python3
"""
Ejemplos de uso del Log Processor
"""
from log_processor import (
    LogProcessor,
    ZipExtractor,
    LogParser,
    DataAggregator
)


def example_1_basic_processing():
    """Ejemplo 1: Procesamiento básico sin BigQuery"""
    print("\n" + "="*80)
    print("EJEMPLO 1: Procesamiento básico (sin BigQuery)")
    print("="*80)

    # Crear procesador (sin subir a BigQuery)
    processor = LogProcessor(
        project_id="dummy",  # No se usa si no subimos
        dataset_id="dummy",
        table_id="dummy",
        top_n=10  # Top 10 para el ejemplo
    )

    # Procesar ZIP
    try:
        processor.run(
            zip_path="logs_ejemplo.zip",
            month="2024-01-01",
            upload=False,  # No subir a BigQuery
            output_json="ejemplo_resultado.json"
        )
        print("\n✅ Procesamiento completado. Ver ejemplo_resultado.json")
    except FileNotFoundError:
        print("\n⚠️  Archivo logs_ejemplo.zip no encontrado.")
        print("   Crea un ZIP con archivos .txt de logs para probar.")


def example_2_manual_processing():
    """Ejemplo 2: Uso manual de cada módulo"""
    print("\n" + "="*80)
    print("EJEMPLO 2: Uso manual de módulos")
    print("="*80)

    # Paso 1: Extraer ZIP
    print("\n1. Extrayendo archivos del ZIP...")
    try:
        with ZipExtractor() as extractor:
            txt_files = extractor.process_zip("logs_ejemplo.zip")
            print(f"   ✅ {len(txt_files)} archivos .txt extraídos")

            # Paso 2: Parsear logs
            print("\n2. Parseando logs...")
            parser = LogParser()
            all_entries = []

            for txt_file in txt_files:
                entries = parser.parse_file(txt_file)
                all_entries.extend(entries)

            print(f"   ✅ {len(all_entries)} entradas de bots encontradas")

            # Paso 3: Agregar datos
            print("\n3. Agregando datos...")
            aggregator = DataAggregator()
            aggregator.add_entries(all_entries)
            aggregator.print_summary()

            # Paso 4: Obtener top URLs
            print("\n4. Extrayendo top 5 URLs por región...")
            for region in aggregator.data.keys():
                print(f"\n   {region}:")
                top_urls = aggregator.get_top_urls_by_region(region, top_n=5)
                for i, stat in enumerate(top_urls, 1):
                    print(f"      {i}. {stat.url} ({stat.hits} hits)")

    except FileNotFoundError:
        print("\n⚠️  Archivo logs_ejemplo.zip no encontrado.")


def example_3_custom_bots():
    """Ejemplo 3: Usar bots personalizados"""
    print("\n" + "="*80)
    print("EJEMPLO 3: Bots personalizados")
    print("="*80)

    # Definir bots personalizados
    custom_bots = {
        "MiBot": r"MiBot",
        "OtroCrawler": r"OtroCrawler\/\d+",
    }

    # Crear parser con bots personalizados
    parser = LogParser(custom_bots=custom_bots)

    print("\nBots detectados:")
    for bot_name in parser.bot_patterns.keys():
        print(f"  - {bot_name}")


def example_4_analyze_single_log():
    """Ejemplo 4: Analizar un solo archivo de log"""
    print("\n" + "="*80)
    print("EJEMPLO 4: Analizar un solo archivo de log")
    print("="*80)

    import sys

    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        log_file = "ejemplo_log.txt"

    try:
        parser = LogParser()
        entries = parser.parse_file(log_file)

        print(f"\n📊 Resultados para {log_file}:")
        print(f"   Total de hits de bots: {len(entries)}")

        # Agrupar por bot
        bot_counts = {}
        for entry in entries:
            bot_counts[entry.bot_name] = bot_counts.get(entry.bot_name, 0) + 1

        print("\n   Por bot:")
        for bot, count in sorted(bot_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"      {bot}: {count}")

        # Agrupar por región
        region_counts = {}
        for entry in entries:
            region_counts[entry.region] = region_counts.get(entry.region, 0) + 1

        print("\n   Por región:")
        for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"      {region}: {count}")

    except FileNotFoundError:
        print(f"\n⚠️  Archivo {log_file} no encontrado.")


def example_5_export_to_json():
    """Ejemplo 5: Exportar resultados a JSON"""
    print("\n" + "="*80)
    print("EJEMPLO 5: Exportar a JSON")
    print("="*80)

    try:
        # Crear un log de ejemplo en memoria
        sample_log = """192.168.1.1 - - [01/Jan/2024:12:00:00 +0000] "GET /au/page1 HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (compatible; Googlebot/2.1)"
192.168.1.2 - - [01/Jan/2024:12:01:00 +0000] "GET /au/page1 HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (compatible; Googlebot/2.1)"
192.168.1.3 - - [01/Jan/2024:12:02:00 +0000] "GET /uk/page2 HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (compatible; GPTBot/1.0)"
192.168.1.4 - - [01/Jan/2024:12:03:00 +0000] "GET https://www.rpsins.com/page3 HTTP/1.1" 200 1234 "-" "ClaudeBot"
"""

        # Guardar log de ejemplo
        with open("/tmp/ejemplo_log.txt", "w") as f:
            f.write(sample_log)

        # Procesar
        parser = LogParser()
        entries = parser.parse_file("/tmp/ejemplo_log.txt")

        aggregator = DataAggregator()
        aggregator.add_entries(entries)

        # Exportar
        import json
        stats = aggregator.get_top_urls_with_bot_breakdown(top_n=50)

        output = {
            "total_stats": len(stats),
            "stats": [
                {
                    "url": stat.url,
                    "region": stat.region,
                    "bot": stat.bot,
                    "hits": stat.hits
                }
                for stat in stats
            ]
        }

        output_file = "ejemplo_export.json"
        with open(output_file, "w") as f:
            json.dump(output, f, indent=2)

        print(f"\n✅ Datos exportados a {output_file}")
        print(f"   Total de estadísticas: {len(stats)}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Ejecuta todos los ejemplos"""
    print("\n" + "="*80)
    print("LOG PROCESSOR - EJEMPLOS DE USO")
    print("="*80)

    # Ejecutar ejemplos
    example_3_custom_bots()
    example_5_export_to_json()

    print("\n" + "="*80)
    print("Para ejecutar otros ejemplos:")
    print("  - example_1_basic_processing() - Procesamiento básico")
    print("  - example_2_manual_processing() - Uso manual de módulos")
    print("  - example_4_analyze_single_log() - Analizar un solo log")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
