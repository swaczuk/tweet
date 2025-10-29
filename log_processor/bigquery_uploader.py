"""
Módulo para subir datos a BigQuery.
"""
from typing import List, Optional
from datetime import datetime
import logging

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    logging.warning("google-cloud-bigquery no está instalado. Instalar con: pip install google-cloud-bigquery")

from data_aggregator import URLStats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BigQueryUploader:
    """Sube datos de URLs a BigQuery"""

    # Schema de la tabla
    SCHEMA = [
        bigquery.SchemaField("month", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("region", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("url", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("bot", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("hits", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("upload_timestamp", "TIMESTAMP", mode="REQUIRED"),
    ] if BIGQUERY_AVAILABLE else []

    def __init__(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
        credentials_path: Optional[str] = None
    ):
        """
        Args:
            project_id: ID del proyecto de GCP
            dataset_id: ID del dataset en BigQuery
            table_id: ID de la tabla
            credentials_path: Ruta al archivo de credenciales JSON (opcional)
                             Si no se proporciona, usa las credenciales por defecto
        """
        if not BIGQUERY_AVAILABLE:
            raise ImportError(
                "google-cloud-bigquery no está instalado. "
                "Instalar con: pip install google-cloud-bigquery"
            )

        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id

        # Inicializar cliente
        if credentials_path:
            from google.oauth2 import service_account
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = bigquery.Client(
                credentials=credentials,
                project=project_id
            )
        else:
            self.client = bigquery.Client(project=project_id)

        self.table_ref = f"{project_id}.{dataset_id}.{table_id}"
        logger.info(f"BigQuery client inicializado para tabla: {self.table_ref}")

    def create_table_if_not_exists(self) -> bool:
        """
        Crea la tabla si no existe.

        Returns:
            True si la tabla fue creada, False si ya existía
        """
        try:
            self.client.get_table(self.table_ref)
            logger.info(f"La tabla {self.table_ref} ya existe")
            return False
        except NotFound:
            table = bigquery.Table(self.table_ref, schema=self.SCHEMA)
            table = self.client.create_table(table)
            logger.info(f"Tabla {self.table_ref} creada exitosamente")
            return True

    def upload_stats(
        self,
        stats: List[URLStats],
        month: str,
        batch_size: int = 1000
    ) -> int:
        """
        Sube estadísticas de URLs a BigQuery.

        Args:
            stats: Lista de URLStats
            month: Fecha del mes en formato 'YYYY-MM-DD' o 'YYYY-MM-01'
            batch_size: Tamaño del batch para inserciones

        Returns:
            Número de filas insertadas
        """
        if not stats:
            logger.warning("No hay estadísticas para subir")
            return 0

        # Asegurar que la tabla existe
        self.create_table_if_not_exists()

        # Preparar datos
        rows_to_insert = []
        upload_timestamp = datetime.utcnow().isoformat()

        for stat in stats:
            rows_to_insert.append({
                "month": month,
                "region": stat.region,
                "url": stat.url,
                "bot": stat.bot,
                "hits": stat.hits,
                "upload_timestamp": upload_timestamp,
            })

        # Insertar en batches
        total_inserted = 0
        for i in range(0, len(rows_to_insert), batch_size):
            batch = rows_to_insert[i:i + batch_size]
            errors = self.client.insert_rows_json(self.table_ref, batch)

            if errors:
                logger.error(f"Errores al insertar batch {i//batch_size + 1}: {errors}")
            else:
                total_inserted += len(batch)
                logger.info(
                    f"Batch {i//batch_size + 1} insertado: "
                    f"{len(batch)} filas ({total_inserted}/{len(rows_to_insert)})"
                )

        logger.info(f"Total de filas insertadas: {total_inserted}")
        return total_inserted

    def delete_month_data(self, month: str, region: Optional[str] = None):
        """
        Elimina datos de un mes específico (útil para re-procesar).

        Args:
            month: Fecha del mes en formato 'YYYY-MM-DD' o 'YYYY-MM-01'
            region: Si se proporciona, solo elimina datos de esa región
        """
        if region:
            query = f"""
                DELETE FROM `{self.table_ref}`
                WHERE month = '{month}' AND region = '{region}'
            """
            logger.info(f"Eliminando datos de {month} para región {region}")
        else:
            query = f"""
                DELETE FROM `{self.table_ref}`
                WHERE month = '{month}'
            """
            logger.info(f"Eliminando todos los datos de {month}")

        query_job = self.client.query(query)
        query_job.result()  # Wait for completion
        logger.info(f"Datos eliminados exitosamente")

    def query_stats(
        self,
        month: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Consulta estadísticas de la tabla.

        Args:
            month: Filtrar por mes (opcional)
            region: Filtrar por región (opcional)
            limit: Límite de resultados

        Returns:
            Lista de diccionarios con resultados
        """
        query = f"SELECT * FROM `{self.table_ref}`"
        conditions = []

        if month:
            conditions.append(f"month = '{month}'")
        if region:
            conditions.append(f"region = '{region}'")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += f" ORDER BY hits DESC LIMIT {limit}"

        logger.info(f"Ejecutando query: {query}")
        query_job = self.client.query(query)
        results = query_job.result()

        return [dict(row) for row in results]


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    from data_aggregator import URLStats

    if len(sys.argv) < 4:
        print("Uso: python bigquery_uploader.py <project_id> <dataset_id> <table_id> [credentials_path]")
        sys.exit(1)

    project_id = sys.argv[1]
    dataset_id = sys.argv[2]
    table_id = sys.argv[3]
    credentials_path = sys.argv[4] if len(sys.argv) > 4 else None

    # Crear uploader
    uploader = BigQueryUploader(
        project_id=project_id,
        dataset_id=dataset_id,
        table_id=table_id,
        credentials_path=credentials_path
    )

    # Crear tabla si no existe
    uploader.create_table_if_not_exists()

    # Ejemplo de datos de prueba
    test_stats = [
        URLStats(
            url="https://www.ajg.com/au/test-page",
            region="AU",
            bot="Googlebot",
            hits=150
        ),
        URLStats(
            url="https://www.ajg.com/uk/test-page",
            region="UK",
            bot="GPTBot",
            hits=75
        ),
    ]

    # Subir datos de prueba
    month = datetime.now().strftime("%Y-%m-01")
    uploader.upload_stats(test_stats, month)

    # Consultar datos
    results = uploader.query_stats(limit=10)
    print("\nÚltimos 10 registros:")
    for row in results:
        print(f"  {row}")
