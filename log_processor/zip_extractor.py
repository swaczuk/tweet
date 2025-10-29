"""
Módulo para extraer archivos ZIP recursivamente.
Maneja ZIPs dentro de ZIPs y carpetas dentro de ZIPs.
"""
import zipfile
import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Generator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZipExtractor:
    """Extrae archivos ZIP recursivamente y encuentra todos los archivos .txt"""

    def __init__(self, temp_dir: str = None):
        """
        Args:
            temp_dir: Directorio temporal para extraer archivos.
                     Si es None, se crea uno automáticamente.
        """
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="log_processor_")
        self.extracted_files: List[str] = []

    def extract_recursive(self, zip_path: str, extract_to: str = None) -> List[str]:
        """
        Extrae un archivo ZIP recursivamente.

        Args:
            zip_path: Ruta al archivo ZIP
            extract_to: Directorio donde extraer. Si es None, usa self.temp_dir

        Returns:
            Lista de rutas a todos los archivos .txt encontrados
        """
        if extract_to is None:
            extract_to = self.temp_dir

        logger.info(f"Extrayendo {zip_path} a {extract_to}")

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        except zipfile.BadZipFile:
            logger.error(f"Archivo ZIP corrupto: {zip_path}")
            return []

        # Buscar archivos .txt y .zip en el directorio extraído
        txt_files = []
        for root, dirs, files in os.walk(extract_to):
            for file in files:
                file_path = os.path.join(root, file)

                if file.lower().endswith('.txt'):
                    txt_files.append(file_path)
                    logger.info(f"Archivo .txt encontrado: {file_path}")

                elif file.lower().endswith('.zip'):
                    # ZIP dentro de ZIP - extraer recursivamente
                    logger.info(f"ZIP anidado encontrado: {file_path}")
                    nested_extract_dir = os.path.join(
                        self.temp_dir,
                        f"nested_{Path(file).stem}"
                    )
                    os.makedirs(nested_extract_dir, exist_ok=True)
                    nested_files = self.extract_recursive(file_path, nested_extract_dir)
                    txt_files.extend(nested_files)

        self.extracted_files.extend(txt_files)
        return txt_files

    def process_zip(self, zip_path: str) -> List[str]:
        """
        Procesa un archivo ZIP y devuelve todas las rutas de archivos .txt

        Args:
            zip_path: Ruta al archivo ZIP principal

        Returns:
            Lista de rutas a todos los archivos .txt encontrados
        """
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Archivo ZIP no encontrado: {zip_path}")

        if not zipfile.is_zipfile(zip_path):
            raise ValueError(f"El archivo no es un ZIP válido: {zip_path}")

        logger.info(f"Iniciando procesamiento de {zip_path}")
        txt_files = self.extract_recursive(zip_path)
        logger.info(f"Total de archivos .txt encontrados: {len(txt_files)}")

        return txt_files

    def cleanup(self):
        """Limpia el directorio temporal"""
        if os.path.exists(self.temp_dir):
            logger.info(f"Limpiando directorio temporal: {self.temp_dir}")
            shutil.rmtree(self.temp_dir)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


if __name__ == "__main__":
    # Ejemplo de uso
    import sys

    if len(sys.argv) < 2:
        print("Uso: python zip_extractor.py <ruta_al_zip>")
        sys.exit(1)

    zip_path = sys.argv[1]

    with ZipExtractor() as extractor:
        txt_files = extractor.process_zip(zip_path)
        print(f"\nArchivos .txt encontrados ({len(txt_files)}):")
        for txt_file in txt_files:
            print(f"  - {txt_file}")
