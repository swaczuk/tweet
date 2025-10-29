"""
Log Processor - Sistema de procesamiento de logs y carga a BigQuery

Procesa logs mensuales de servidor, extrae estadísticas de hits de bots
por URL y región, y carga los datos a BigQuery.
"""

__version__ = "1.0.0"

from .zip_extractor import ZipExtractor
from .log_parser import LogParser, LogEntry
from .data_aggregator import DataAggregator, URLStats
from .bigquery_uploader import BigQueryUploader
from .process_logs import LogProcessor

__all__ = [
    "ZipExtractor",
    "LogParser",
    "LogEntry",
    "DataAggregator",
    "URLStats",
    "BigQueryUploader",
    "LogProcessor",
]
