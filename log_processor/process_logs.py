#!/usr/bin/env python3
"""
Script principal para procesar logs mensuales y subir a BigQuery.

Este script:
1. Extrae archivos ZIP recursivamente
2. Parsea logs del servidor para detectar hits de bots
3. Agrega datos por URL, región y bot
4. Extrae las top 50 URLs por región
5. Sube los datos a BigQuery

Uso:
    python process_logs.py <zip_file> --month 2024-01-01 [opciones]
"""
import argparse
import sys
import os
from datetime import datetime
from pathlib import Path
import logging
import json

# Importar módulos del proyecto
from zip_extractor import ZipExtractor
from log_parser import LogParser
from data_aggregator import DataAggregator
from bigquery_uploader import BigQueryUploader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LogProcessor:
    """Procesa logs mensuales y los sube a BigQuery"""

    def __init__(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
        credentials_path: str = None,
        top_n: int = 50,
        custom_bots: dict = None
    ):
        """
        Args:
            project_id: ID del proyecto de GCP
            dataset_id: ID del dataset en BigQuery
            table_id: ID de la tabla
            credentials_path: Ruta al archivo de credenciales JSON
            top_n: Número de URLs top a extraer por región
            custom_bots: Diccionario de bots personalizados {nombre: patrón_regex}
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.credentials_path = credentials_path
        self.top_n = top_n

        self.parser = LogParser(custom_bots=custom_bots)
        self.aggregator = DataAggregator()

    def process_zip(self, zip_path: str) -> int:
        """
        Procesa un archivo ZIP y extrae los logs.

        Args:
            zip_path: Ruta al archivo ZIP

        Returns:
            Número de entradas de bots procesadas
        """
        logger.info(f"Iniciando procesamiento de {zip_path}")

        with ZipExtractor() as extractor:
            # Extraer todos los archivos .txt
            txt_files = extractor.process_zip(zip_path)
            logger.info(f"Archivos .txt extraídos: {len(txt_files)}")

            if not txt_files:
                logger.warning("No se encontraron archivos .txt en el ZIP")
                return 0

            # Parsear cada archivo de log
            total_entries = 0
            for txt_file in txt_files:
                entries = self.parser.parse_file(txt_file)
                self.aggregator.add_entries(entries)
                total_entries += len(entries)

            logger.info(f"Total de entradas de bots procesadas: {total_entries}")
            return total_entries

    def upload_to_bigquery(self, month: str, replace: bool = False) -> int:
        """
        Sube los datos agregados a BigQuery.

        Args:
            month: Fecha del mes en formato 'YYYY-MM-01'
            replace: Si True, elimina datos existentes del mes antes de subir

        Returns:
            Número de filas insertadas
        """
        logger.info("Extrayendo top URLs por región")

        # Extraer top URLs con desglose por bot
        stats = self.aggregator.get_top_urls_with_bot_breakdown(top_n=self.top_n)

        if not stats:
            logger.warning("No hay estadísticas para subir")
            return 0

        logger.info(f"Total de estadísticas a subir: {len(stats)}")

        # Crear uploader
        uploader = BigQueryUploader(
            project_id=self.project_id,
            dataset_id=self.dataset_id,
            table_id=self.table_id,
            credentials_path=self.credentials_path
        )

        # Eliminar datos existentes si se solicita
        if replace:
            logger.info("Eliminando datos existentes del mes")
            uploader.delete_month_data(month)

        # Subir datos
        rows_inserted = uploader.upload_stats(stats, month)
        logger.info(f"Proceso completado. Filas insertadas: {rows_inserted}")

        return rows_inserted

    def save_to_json(self, output_file: str):
        """
        Guarda las estadísticas en un archivo JSON.

        Args:
            output_file: Ruta al archivo de salida
        """
        stats = self.aggregator.get_top_urls_with_bot_breakdown(top_n=self.top_n)

        data = {
            "total_stats": len(stats),
            "summary": self.aggregator.get_summary(),
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

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Estadísticas guardadas en {output_file}")

    def run(
        self,
        zip_path: str,
        month: str,
        upload: bool = True,
        replace: bool = False,
        output_json: str = None
    ):
        """
        Ejecuta el proceso completo.

        Args:
            zip_path: Ruta al archivo ZIP con logs
            month: Mes en formato 'YYYY-MM-01'
            upload: Si True, sube a BigQuery
            replace: Si True, reemplaza datos existentes del mes
            output_json: Si se proporciona, guarda estadísticas en JSON
        """
        logger.info("="*80)
        logger.info("INICIANDO PROCESAMIENTO DE LOGS")
        logger.info("="*80)

        # Procesar ZIP
        total_entries = self.process_zip(zip_path)

        if total_entries == 0:
            logger.error("No se encontraron entradas de bots. Abortando.")
            return

        # Mostrar resumen
        self.aggregator.print_summary()

        # Guardar JSON si se solicita
        if output_json:
            self.save_to_json(output_json)

        # Subir a BigQuery si se solicita
        if upload:
            self.upload_to_bigquery(month, replace=replace)

        logger.info("="*80)
        logger.info("PROCESAMIENTO COMPLETADO")
        logger.info("="*80)


def parse_args():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Procesa logs mensuales y sube estadísticas a BigQuery"
    )

    # Argumentos requeridos
    parser.add_argument(
        "zip_file",
        help="Ruta al archivo ZIP con logs del mes"
    )
    parser.add_argument(
        "--month",
        required=True,
        help="Mes de los logs en formato YYYY-MM-01 (ej: 2024-01-01)"
    )

    # Configuración de BigQuery
    parser.add_argument(
        "--project-id",
        required=True,
        help="ID del proyecto de GCP"
    )
    parser.add_argument(
        "--dataset-id",
        required=True,
        help="ID del dataset en BigQuery"
    )
    parser.add_argument(
        "--table-id",
        default="bot_hits_by_url",
        help="ID de la tabla en BigQuery (default: bot_hits_by_url)"
    )
    parser.add_argument(
        "--credentials",
        help="Ruta al archivo de credenciales JSON de GCP"
    )

    # Opciones de procesamiento
    parser.add_argument(
        "--top-n",
        type=int,
        default=50,
        help="Número de URLs top a extraer por región (default: 50)"
    )
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="No subir a BigQuery, solo procesar"
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Reemplazar datos existentes del mes en BigQuery"
    )
    parser.add_argument(
        "--output-json",
        help="Guardar estadísticas en archivo JSON"
    )

    # Configuración personalizada
    parser.add_argument(
        "--custom-bots",
        help="Archivo JSON con bots personalizados: {\"nombre\": \"patrón_regex\"}"
    )

    return parser.parse_args()


def main():
    """Función principal"""
    args = parse_args()

    # Validar archivo ZIP
    if not os.path.exists(args.zip_file):
        logger.error(f"Archivo ZIP no encontrado: {args.zip_file}")
        sys.exit(1)

    # Validar formato de fecha
    try:
        datetime.strptime(args.month, "%Y-%m-%d")
    except ValueError:
        logger.error(f"Formato de fecha inválido: {args.month}. Use YYYY-MM-DD")
        sys.exit(1)

    # Cargar bots personalizados si se proporcionan
    custom_bots = None
    if args.custom_bots:
        if not os.path.exists(args.custom_bots):
            logger.error(f"Archivo de bots personalizados no encontrado: {args.custom_bots}")
            sys.exit(1)
        with open(args.custom_bots, 'r') as f:
            custom_bots = json.load(f)
        logger.info(f"Bots personalizados cargados: {list(custom_bots.keys())}")

    # Crear procesador
    processor = LogProcessor(
        project_id=args.project_id,
        dataset_id=args.dataset_id,
        table_id=args.table_id,
        credentials_path=args.credentials,
        top_n=args.top_n,
        custom_bots=custom_bots
    )

    # Ejecutar procesamiento
    try:
        processor.run(
            zip_path=args.zip_file,
            month=args.month,
            upload=not args.no_upload,
            replace=args.replace,
            output_json=args.output_json
        )
    except Exception as e:
        logger.error(f"Error durante el procesamiento: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
