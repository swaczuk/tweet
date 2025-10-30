"""
Módulo para agregar datos de logs y extraer las top URLs por región y bot.
"""
from collections import defaultdict
from typing import List, Dict, Tuple
from dataclasses import dataclass
import logging

from simple_parser import SimpleLogEntry as LogEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class URLStats:
    """Estadísticas de una URL"""
    url: str
    region: str
    bot: str
    hits: int


class DataAggregator:
    """Agrega hits por URL, región y bot"""

    def __init__(self):
        # Estructura: {region: {bot: {url: count}}}
        self.data: Dict[str, Dict[str, Dict[str, int]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(int))
        )

    def add_entry(self, entry: LogEntry):
        """
        Agrega una entrada de log a las estadísticas.

        Args:
            entry: LogEntry parseada
        """
        self.data[entry.region][entry.bot_name][entry.url] += 1

    def add_entries(self, entries: List[LogEntry]):
        """
        Agrega múltiples entradas de log.

        Args:
            entries: Lista de LogEntry
        """
        for entry in entries:
            self.add_entry(entry)
        logger.info(f"Agregadas {len(entries)} entradas")

    def get_top_urls_by_region(
        self,
        region: str,
        top_n: int = 50
    ) -> List[URLStats]:
        """
        Obtiene las top N URLs para una región específica, sumando todos los bots.

        Args:
            region: Código de región
            top_n: Número de URLs a devolver

        Returns:
            Lista de URLStats ordenadas por hits (mayor a menor)
        """
        if region not in self.data:
            return []

        # Agregar hits de todos los bots para cada URL
        url_totals = defaultdict(int)
        for bot, urls in self.data[region].items():
            for url, count in urls.items():
                url_totals[url] += count

        # Ordenar y obtener top N
        top_urls = sorted(url_totals.items(), key=lambda x: x[1], reverse=True)[:top_n]

        # Convertir a URLStats (region y bot se agregan después)
        return [
            URLStats(url=url, region=region, bot="ALL", hits=hits)
            for url, hits in top_urls
        ]

    def get_top_urls_by_region_and_bot(
        self,
        region: str,
        bot: str,
        top_n: int = 50
    ) -> List[URLStats]:
        """
        Obtiene las top N URLs para una región y bot específicos.

        Args:
            region: Código de región
            bot: Nombre del bot
            top_n: Número de URLs a devolver

        Returns:
            Lista de URLStats ordenadas por hits (mayor a menor)
        """
        if region not in self.data or bot not in self.data[region]:
            return []

        urls = self.data[region][bot]
        top_urls = sorted(urls.items(), key=lambda x: x[1], reverse=True)[:top_n]

        return [
            URLStats(url=url, region=region, bot=bot, hits=hits)
            for url, hits in top_urls
        ]

    def get_all_top_urls_by_region(
        self,
        top_n: int = 50,
        split_by_bot: bool = False
    ) -> List[URLStats]:
        """
        Obtiene las top N URLs para todas las regiones.

        Args:
            top_n: Número de URLs por región
            split_by_bot: Si True, devuelve resultados separados por bot.
                         Si False, suma todos los bots por URL.

        Returns:
            Lista de URLStats
        """
        results = []

        for region in self.data.keys():
            if split_by_bot:
                # Obtener top URLs para cada combinación de región y bot
                for bot in self.data[region].keys():
                    top_urls = self.get_top_urls_by_region_and_bot(region, bot, top_n)
                    results.extend(top_urls)
            else:
                # Obtener top URLs por región (todos los bots combinados)
                top_urls = self.get_top_urls_by_region(region, top_n)
                results.extend(top_urls)

        logger.info(f"Extraídas {len(results)} estadísticas de URLs")
        return results

    def get_top_urls_with_bot_breakdown(
        self,
        top_n: int = 50
    ) -> List[URLStats]:
        """
        Obtiene las top N URLs por región, pero incluye el desglose por bot.

        Para cada región:
        1. Encuentra las top N URLs (sumando todos los bots)
        2. Para cada una de esas URLs, crea una entrada por cada bot que la visitó

        Args:
            top_n: Número de URLs por región

        Returns:
            Lista de URLStats con desglose por bot
        """
        results = []

        for region in self.data.keys():
            # Primero obtener las top URLs de la región
            top_urls_in_region = self.get_top_urls_by_region(region, top_n)
            top_url_set = {stat.url for stat in top_urls_in_region}

            # Para cada URL top, agregar una entrada por cada bot
            for url in top_url_set:
                for bot in self.data[region].keys():
                    if url in self.data[region][bot]:
                        hits = self.data[region][bot][url]
                        results.append(
                            URLStats(url=url, region=region, bot=bot, hits=hits)
                        )

        logger.info(f"Extraídas {len(results)} estadísticas con desglose por bot")
        return results

    def get_summary(self) -> Dict:
        """
        Obtiene un resumen de las estadísticas.

        Returns:
            Diccionario con resumen de datos
        """
        summary = {
            "total_regions": len(self.data),
            "regions": {}
        }

        for region, bots in self.data.items():
            total_hits = 0
            total_urls = set()
            bot_counts = {}

            for bot, urls in bots.items():
                bot_hits = sum(urls.values())
                bot_counts[bot] = {
                    "hits": bot_hits,
                    "unique_urls": len(urls)
                }
                total_hits += bot_hits
                total_urls.update(urls.keys())

            summary["regions"][region] = {
                "total_hits": total_hits,
                "unique_urls": len(total_urls),
                "bots": bot_counts
            }

        return summary

    def print_summary(self):
        """Imprime un resumen de las estadísticas"""
        summary = self.get_summary()

        print(f"\n{'='*80}")
        print(f"RESUMEN DE DATOS")
        print(f"{'='*80}")
        print(f"Total de regiones: {summary['total_regions']}")

        for region, stats in summary["regions"].items():
            print(f"\n{'-'*80}")
            print(f"Región: {region}")
            print(f"  Total de hits: {stats['total_hits']:,}")
            print(f"  URLs únicas: {stats['unique_urls']:,}")
            print(f"  Bots:")
            for bot, bot_stats in sorted(
                stats["bots"].items(),
                key=lambda x: x[1]["hits"],
                reverse=True
            ):
                print(f"    {bot}: {bot_stats['hits']:,} hits, {bot_stats['unique_urls']:,} URLs")


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    from simple_parser import SimpleLogParser

    if len(sys.argv) < 2:
        print("Uso: python data_aggregator.py <ruta_al_log>")
        sys.exit(1)

    log_file = sys.argv[1]

    # Parsear log
    parser = SimpleLogParser()
    entries = parser.parse_file(log_file)

    # Agregar datos
    aggregator = DataAggregator()
    aggregator.add_entries(entries)

    # Mostrar resumen
    aggregator.print_summary()

    # Mostrar top 10 URLs por región
    print(f"\n{'='*80}")
    print("TOP 10 URLs POR REGIÓN (todos los bots combinados)")
    print(f"{'='*80}")

    for region in aggregator.data.keys():
        print(f"\n{region}:")
        top_urls = aggregator.get_top_urls_by_region(region, top_n=10)
        for i, stat in enumerate(top_urls, 1):
            print(f"  {i}. {stat.url} - {stat.hits:,} hits")
