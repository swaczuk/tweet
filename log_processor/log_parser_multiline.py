"""
Parser de logs que maneja entradas multi-línea.
Usa este parser si check_line_integrity.py detecta líneas cortadas.
"""
import re
from typing import List
from log_parser import LogParser, LogEntry
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultilineLogParser(LogParser):
    """Parser que maneja entradas de log que ocupan múltiples líneas"""

    def parse_file(self, file_path: str) -> List[LogEntry]:
        """
        Parsea un archivo completo de logs, manejando entradas multi-línea.

        Args:
            file_path: Ruta al archivo de log

        Returns:
            Lista de LogEntry para entradas de bots
        """
        entries = []
        line_count = 0
        bot_count = 0
        reconstructed_count = 0

        logger.info(f"Parseando archivo (modo multi-línea): {file_path}")

        # Patrón para detectar inicio de nueva entrada
        start_pattern = re.compile(r'^\d+\.\d+\.\d+\.\d+ - - \d{2}/\d{2}/\d{4}')

        current_line = ""

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for raw_line in f:
                    line_count += 1
                    raw_line = raw_line.rstrip('\n\r')

                    if start_pattern.match(raw_line):
                        # Nueva entrada de log - procesar la anterior si existe
                        if current_line:
                            entry = self.parse_line(current_line)
                            if entry:
                                entries.append(entry)
                                bot_count += 1

                        current_line = raw_line
                    else:
                        # Continuación de la línea anterior
                        if current_line:
                            current_line += " " + raw_line
                            reconstructed_count += 1

                    # Log progreso cada 100k líneas
                    if line_count % 100000 == 0:
                        logger.info(
                            f"  Procesadas {line_count} líneas, "
                            f"{reconstructed_count} continuaciones, "
                            f"{bot_count} hits de bots"
                        )

                # Procesar la última línea
                if current_line:
                    entry = self.parse_line(current_line)
                    if entry:
                        entries.append(entry)
                        bot_count += 1

        except Exception as e:
            logger.error(f"Error parseando archivo {file_path}: {e}")

        logger.info(
            f"  Total: {line_count} líneas leídas, "
            f"{reconstructed_count} líneas de continuación, "
            f"{bot_count} hits de bots"
        )

        return entries


if __name__ == "__main__":
    # Ejemplo de uso
    import sys

    if len(sys.argv) < 2:
        print("Uso: python log_parser_multiline.py <ruta_al_log>")
        sys.exit(1)

    log_file = sys.argv[1]
    parser = MultilineLogParser()
    entries = parser.parse_file(log_file)

    print(f"\nTotal de hits de bots: {len(entries)}")

    # Mostrar resumen por bot
    bot_counts = {}
    for entry in entries:
        bot_counts[entry.bot_name] = bot_counts.get(entry.bot_name, 0) + 1

    print("\nResumen por bot:")
    for bot, count in sorted(bot_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {bot}: {count}")

    # Mostrar resumen por región
    region_counts = {}
    for entry in entries:
        region_counts[entry.region] = region_counts.get(entry.region, 0) + 1

    print("\nResumen por región:")
    for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {region}: {count}")
