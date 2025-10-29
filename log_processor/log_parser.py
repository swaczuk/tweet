"""
Módulo para parsear archivos de log y extraer información de bots.
Soporta formatos de log comunes (Apache, Nginx).
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """Representa una entrada de log parseada"""
    ip: str
    timestamp: str
    method: str
    url: str
    status_code: str
    user_agent: str
    region: Optional[str] = None
    bot_name: Optional[str] = None
    date: Optional[str] = None  # Fecha en formato YYYY-MM-DD


class LogParser:
    """Parser para archivos de log de servidor"""

    # Expresión regular para el formato de log personalizado
    # Formato: IP - - DD/MM/YYYY HH:MM:SS AM/PM "METHOD URL HTTP/1.1" status num1 num2 "" "user-agent"
    # Ejemplo: 10.201.52.5 - - 25/09/2025 08:05:31 PM "GET https://www.ajg.com/uk/... HTTP/1.1" 200 100 100  "" "Mozilla/5.0..."
    LOG_PATTERN = re.compile(
        r'(?P<ip>[\d\.]+) - - '
        r'(?P<timestamp>\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} (?:AM|PM)) '
        r'"(?P<method>\w+) (?P<url>\S+) HTTP/[^"]+" '
        r'(?P<status>\d+) (?P<size1>\d+) (?P<size2>\d+)\s+'
        r'"[^"]*" "(?P<user_agent>[^"]*)"'
    )

    # Lista de bots conocidos con patrones para detectarlos en User-Agent
    BOT_PATTERNS = {
        'Googlebot': r'Googlebot',
        'Google-Extended': r'Google-Extended',  # ChatGPT en Google
        'GPTBot': r'GPTBot',  # OpenAI ChatGPT
        'ChatGPT-User': r'ChatGPT-User',
        'Claude-Web': r'Claude-Web',  # Anthropic Claude
        'ClaudeBot': r'ClaudeBot',
        'anthropic-ai': r'anthropic-ai',
        'Google-InspectionTool': r'Google-InspectionTool',
        'Bingbot': r'bingbot',
        'Slurp': r'Yahoo! Slurp',  # Yahoo
        'DuckDuckBot': r'DuckDuckBot',
        'Baiduspider': r'Baiduspider',
        'YandexBot': r'YandexBot',
        'PerplexityBot': r'PerplexityBot',
        'Applebot': r'Applebot',
        'facebookexternalhit': r'facebookexternalhit',
        'LinkedInBot': r'LinkedInBot',
        'Twitterbot': r'Twitterbot',
        'Slackbot': r'Slackbot',
        'Discordbot': r'Discordbot',
        'TelegramBot': r'TelegramBot',
        'WhatsApp': r'WhatsApp',
        'ia_archiver': r'ia_archiver',  # Internet Archive
        'archive.org_bot': r'archive\.org_bot',
        'PetalBot': r'PetalBot',
        'Bytespider': r'Bytespider',
        'SemrushBot': r'SemrushBot',
        'AhrefsBot': r'AhrefsBot',
        'DotBot': r'DotBot',
        'MJ12bot': r'MJ12bot',
        'BLEXBot': r'BLEXBot',
        'DataForSeoBot': r'DataForSeoBot',
        'rogerbot': r'rogerbot',
        'Screaming Frog': r'Screaming Frog',
        'sitebulb': r'sitebulb',
        'Google-Safety': r'Google-Safety',
        'ImagesiftBot': r'ImagesiftBot',
    }

    # Configuración de regiones basadas en URL
    # El orden es importante: las regiones más específicas deben ir primero
    REGION_PATTERNS = {
        'AJG-UK': r'ajg\.com/uk/',
        'AJG-AU': r'ajg\.com/au/',
        'AJG-CA-FR': r'ajg\.com/ca-fr/',
        'AJG-CA': r'ajg\.com/ca/',
        'GB-AU': r'gallagherbassett\.com/au/',
        'GB-UK': r'gallagherbassett\.com/uk/',
        'GB': r'gallagherbassett\.com',
        'RPS': r'rpsins\.com',
        'ARTEX': r'artexrisk\.com',
        'AJG-MAIN': r'ajg\.com',  # Sitio principal (debe ir al final)
    }

    def __init__(self, custom_bots: Dict[str, str] = None):
        """
        Args:
            custom_bots: Diccionario adicional de bots personalizados
                        {nombre: patrón_regex}
        """
        if custom_bots:
            self.bot_patterns = {**self.BOT_PATTERNS, **custom_bots}
        else:
            self.bot_patterns = self.BOT_PATTERNS

        # Compilar patrones de bots
        self.compiled_bot_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.bot_patterns.items()
        }

        # Compilar patrones de regiones
        self.compiled_region_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.REGION_PATTERNS.items()
        }

    def identify_bot(self, user_agent: str) -> Optional[str]:
        """
        Identifica si el user agent corresponde a un bot conocido.

        Args:
            user_agent: String del user agent

        Returns:
            Nombre del bot o None si no es un bot conocido
        """
        for bot_name, pattern in self.compiled_bot_patterns.items():
            if pattern.search(user_agent):
                return bot_name
        return None

    def identify_region(self, url: str) -> str:
        """
        Identifica la región basándose en la URL.

        Args:
            url: URL completa o path

        Returns:
            Código de región o 'UNKNOWN'
        """
        # Verificar todos los patrones en orden (los más específicos primero)
        # El orden está definido en REGION_PATTERNS
        for region, pattern in self.compiled_region_patterns.items():
            if pattern.search(url):
                return region

        return 'UNKNOWN'

    def parse_date(self, timestamp: str) -> Optional[str]:
        """
        Parsea el timestamp y extrae la fecha en formato YYYY-MM-DD.

        Args:
            timestamp: Timestamp en formato "DD/MM/YYYY HH:MM:SS AM/PM"

        Returns:
            Fecha en formato "YYYY-MM-DD" o None si no se puede parsear
        """
        try:
            from datetime import datetime
            # Timestamp formato: "25/09/2025 08:05:31 PM"
            dt = datetime.strptime(timestamp, "%d/%m/%Y %I:%M:%S %p")
            return dt.strftime("%Y-%m-%d")
        except Exception as e:
            logger.warning(f"No se pudo parsear timestamp '{timestamp}': {e}")
            return None

    def parse_line(self, line: str) -> Optional[LogEntry]:
        """
        Parsea una línea de log.

        Args:
            line: Línea de log en formato personalizado

        Returns:
            LogEntry o None si no se puede parsear
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None

        data = match.groupdict()
        user_agent = data['user_agent']
        url = data['url']
        timestamp = data['timestamp']

        bot_name = self.identify_bot(user_agent)
        if not bot_name:
            # No es un bot, ignorar
            return None

        region = self.identify_region(url)
        date = self.parse_date(timestamp)

        return LogEntry(
            ip=data['ip'],
            timestamp=timestamp,
            method=data['method'],
            url=url,
            status_code=data['status'],
            user_agent=user_agent,
            region=region,
            bot_name=bot_name,
            date=date
        )

    def parse_file(self, file_path: str) -> List[LogEntry]:
        """
        Parsea un archivo completo de logs.

        Args:
            file_path: Ruta al archivo de log

        Returns:
            Lista de LogEntry para entradas de bots
        """
        entries = []
        line_count = 0
        bot_count = 0

        logger.info(f"Parseando archivo: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line_count += 1
                    entry = self.parse_line(line.strip())
                    if entry:
                        entries.append(entry)
                        bot_count += 1

                    # Log progreso cada 100k líneas
                    if line_count % 100000 == 0:
                        logger.info(f"  Procesadas {line_count} líneas, {bot_count} hits de bots")

        except Exception as e:
            logger.error(f"Error parseando archivo {file_path}: {e}")

        logger.info(f"  Total: {line_count} líneas, {bot_count} hits de bots")
        return entries


if __name__ == "__main__":
    # Ejemplo de uso
    import sys

    if len(sys.argv) < 2:
        print("Uso: python log_parser.py <ruta_al_log>")
        sys.exit(1)

    log_file = sys.argv[1]
    parser = LogParser()
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
