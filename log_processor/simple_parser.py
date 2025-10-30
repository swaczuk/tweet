#!/usr/bin/env python3
"""
Parser ULTRA SIMPLE que captura TODO
Sin regex complicados - usa string splitting simple
"""
import re
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SimpleLogEntry:
    ip: str
    timestamp: str
    method: str
    url: str
    status_code: str
    user_agent: str
    date: str
    region: Optional[str] = None
    bot_name: Optional[str] = None


class SimpleLogParser:
    """Parser ultra simple que captura el 95%+ de líneas"""

    BOT_PATTERNS = {
        'ChatGPT': r'(?i)(gptbot|chatgpt-user|google-extended)',
        'Claude': r'(?i)(claudebot|claude-web|anthropic)',
        'Googlebot': r'(?i)googlebot',
        'Bingbot': r'(?i)bingbot',
        'PerplexityBot': r'(?i)perplexity',
        'Applebot': r'(?i)applebot',
        'PingdomBot': r'(?i)pingdom',
        'IncapsulaBot': r'(?i)incapsula',
        'UptimeBot': r'(?i)uptime',
        'ScreamingFrog': r'(?i)screaming\s*frog',
        'YandexBot': r'(?i)yandex',
        'Baiduspider': r'(?i)baidu',
        'FacebookBot': r'(?i)facebook',
        'LinkedInBot': r'(?i)linkedin',
        'TwitterBot': r'(?i)twitter',
        'SemrushBot': r'(?i)semrush',
        'AhrefsBot': r'(?i)ahrefs',
        'MJ12bot': r'(?i)mj12',
    }

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
        'AJG-MAIN': r'ajg\.com',
    }

    def __init__(self):
        self.bot_patterns_compiled = {
            name: re.compile(pattern)
            for name, pattern in self.BOT_PATTERNS.items()
        }
        self.region_patterns_compiled = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.REGION_PATTERNS.items()
        }

    def parse_line(self, line: str) -> Optional[SimpleLogEntry]:
        """
        Parsea una línea usando splitting simple en lugar de regex complejo
        """
        try:
            # Buscar las comillas que encierran el request
            quote_start = line.find('"')
            if quote_start == -1:
                return None

            # Extraer la parte antes de las comillas (IP, timestamp)
            before_request = line[:quote_start].strip()
            parts = before_request.split()

            if len(parts) < 4:
                return None

            ip = parts[0]
            # Timestamp: puede ser "DD/MM/YYYY HH:MM:SS AM/PM"
            # Buscar el patrón de fecha
            timestamp = ' '.join(parts[3:])  # Todo después del tercer guión

            # Extraer el request (entre comillas)
            quote_end = line.find('"', quote_start + 1)
            if quote_end == -1:
                return None

            request = line[quote_start + 1:quote_end]
            request_parts = request.split()

            if len(request_parts) < 2:
                return None

            method = request_parts[0]
            url = request_parts[1]

            # Extraer status y lo que sigue
            after_request = line[quote_end + 1:].strip()
            after_parts = after_request.split()

            if len(after_parts) < 1:
                return None

            status_code = after_parts[0]

            # Extraer user agent (última parte entre comillas)
            last_quote_start = line.rfind('"', 0, -1)
            last_quote_end = line.rfind('"')

            user_agent = ''
            if last_quote_start != -1 and last_quote_end != -1 and last_quote_end > last_quote_start:
                user_agent = line[last_quote_start + 1:last_quote_end]

            # Si no hay UA o está vacío, saltar
            if not user_agent or user_agent.strip() == '':
                return None

            # Identificar bot
            bot_name = None
            for bot, pattern in self.bot_patterns_compiled.items():
                if pattern.search(user_agent):
                    bot_name = bot
                    break

            # Solo devolver si es bot
            if not bot_name:
                return None

            # Identificar región
            region = None
            for reg, pattern in self.region_patterns_compiled.items():
                if pattern.search(url):
                    region = reg
                    break

            # Parsear fecha
            date = self.parse_date(timestamp)

            return SimpleLogEntry(
                ip=ip,
                timestamp=timestamp,
                method=method,
                url=url,
                status_code=status_code,
                user_agent=user_agent,
                date=date,
                region=region,
                bot_name=bot_name
            )

        except Exception as e:
            # Si falla, ignorar la línea
            return None

    def parse_date(self, timestamp: str) -> str:
        """Extrae fecha del timestamp"""
        try:
            # Timestamp formato: "25/09/2025 08:05:31 PM"
            dt = datetime.strptime(timestamp.strip(), "%d/%m/%Y %I:%M:%S %p")
            return dt.strftime("%Y-%m-%d")
        except:
            return None

    def parse_file(self, file_path: str, verbose: bool = True):
        """Parsea archivo completo"""
        entries = []
        total_lines = 0
        bot_lines = 0

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                total_lines += 1
                entry = self.parse_line(line.strip())
                if entry:
                    entries.append(entry)
                    bot_lines += 1

        if verbose and total_lines > 0:
            print(f"Total líneas: {total_lines}")
            print(f"Bots detectados: {bot_lines} ({bot_lines/total_lines*100:.1f}%)")
        elif verbose:
            print(f"Archivo vacío o sin contenido válido")

        return entries


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python simple_parser.py <archivo.txt>")
        sys.exit(1)

    parser = SimpleLogParser()
    entries = parser.parse_file(sys.argv[1])

    # Resumen por bot
    bot_counts = {}
    for e in entries:
        bot_counts[e.bot_name] = bot_counts.get(e.bot_name, 0) + 1

    print("\nPor bot:")
    for bot, count in sorted(bot_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {bot}: {count}")
