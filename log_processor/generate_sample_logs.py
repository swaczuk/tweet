#!/usr/bin/env python3
"""
Genera logs de ejemplo para probar el sistema
"""
import random
from datetime import datetime, timedelta
import zipfile
import os


# URLs de ejemplo por región
SAMPLE_URLS = {
    "AU": [
        "/au/insurance/business",
        "/au/insurance/personal",
        "/au/about-us",
        "/au/contact",
        "/au/services/risk-management",
        "/au/services/employee-benefits",
        "/au/blog/insurance-tips",
        "/au/resources/guides",
        "/au/careers",
        "/au/news",
    ],
    "UK": [
        "/uk/insurance/business",
        "/uk/insurance/personal",
        "/uk/about-us",
        "/uk/contact",
        "/uk/services/risk-management",
        "/uk/blog/insurance-news",
        "/uk/resources/whitepapers",
        "/uk/careers",
    ],
    "CA": [
        "/ca/insurance/business",
        "/ca/insurance/personal",
        "/ca/about-us",
        "/ca/services/risk-management",
        "/ca/blog",
    ],
    "CA-FR": [
        "/ca-fr/assurance/entreprise",
        "/ca-fr/assurance/personnelle",
        "/ca-fr/a-propos",
        "/ca-fr/services",
    ],
    "RPS": [
        "https://www.rpsins.com/services",
        "https://www.rpsins.com/about",
        "https://www.rpsins.com/contact",
        "https://www.rpsins.com/resources",
        "https://www.rpsins.com/blog",
    ],
    "GB": [
        "https://www.gallagherbassett.com/services",
        "https://www.gallagherbassett.com/about",
        "https://www.gallagherbassett.com/contact",
        "https://www.gallagherbassett.com/resources",
    ],
    "MAIN": [
        "/about-us",
        "/services",
        "/contact",
        "/careers",
        "/news",
        "/blog",
    ],
}

# User agents de bots
BOT_USER_AGENTS = [
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.0; +https://openai.com/gptbot)",
    "Mozilla/5.0 (compatible; ChatGPT-User/1.0; +https://openai.com)",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +slack@anthropic.com)",
    "Mozilla/5.0 (compatible; anthropic-ai/1.0)",
    "Mozilla/5.0 (compatible; PerplexityBot/1.0; +https://perplexity.ai)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
    "Mozilla/5.0 (compatible; DuckDuckBot-Https/1.1; https://duckduckgo.com/duckduckbot)",
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
]

# IPs de ejemplo
SAMPLE_IPS = [
    "66.249.64.1",  # Googlebot
    "20.102.96.1",  # GPTBot
    "52.167.144.1",  # Claude
    "40.77.167.1",  # Bing
    "157.55.39.1",  # Yahoo
]


def generate_log_entry(timestamp, region=None):
    """Genera una entrada de log"""
    ip = random.choice(SAMPLE_IPS)
    user_agent = random.choice(BOT_USER_AGENTS)

    if region:
        url = random.choice(SAMPLE_URLS[region])
    else:
        region = random.choice(list(SAMPLE_URLS.keys()))
        url = random.choice(SAMPLE_URLS[region])

    # Formato: IP - - [timestamp] "METHOD /path HTTP/1.1" status size "referer" "user-agent"
    timestamp_str = timestamp.strftime("%d/%b/%Y:%H:%M:%S +0000")
    status = random.choice([200, 200, 200, 304, 404])  # Más 200s
    size = random.randint(1000, 50000)

    return f'{ip} - - [{timestamp_str}] "GET {url} HTTP/1.1" {status} {size} "-" "{user_agent}"\n'


def generate_log_file(filename, num_entries=1000, region=None):
    """Genera un archivo de log"""
    print(f"Generando {filename} con {num_entries} entradas...")

    start_date = datetime(2024, 1, 1)

    with open(filename, "w") as f:
        for i in range(num_entries):
            # Distribuir a lo largo del mes
            offset = timedelta(minutes=random.randint(0, 43200))  # 30 días
            timestamp = start_date + offset

            entry = generate_log_entry(timestamp, region)
            f.write(entry)

    print(f"  ✅ {filename} creado")


def create_sample_zip():
    """Crea un ZIP de ejemplo con logs"""
    print("\n" + "="*80)
    print("Generando logs de ejemplo")
    print("="*80 + "\n")

    # Crear directorio temporal
    os.makedirs("temp_logs", exist_ok=True)

    # Generar logs por región
    log_files = []

    # Logs con muchas entradas
    generate_log_file("temp_logs/access_log_main.txt", num_entries=2000, region="MAIN")
    log_files.append("temp_logs/access_log_main.txt")

    generate_log_file("temp_logs/access_log_au.txt", num_entries=1500, region="AU")
    log_files.append("temp_logs/access_log_au.txt")

    generate_log_file("temp_logs/access_log_uk.txt", num_entries=1200, region="UK")
    log_files.append("temp_logs/access_log_uk.txt")

    generate_log_file("temp_logs/access_log_ca.txt", num_entries=800, region="CA")
    log_files.append("temp_logs/access_log_ca.txt")

    # Logs más pequeños
    generate_log_file("temp_logs/access_log_ca_fr.txt", num_entries=300, region="CA-FR")
    log_files.append("temp_logs/access_log_ca_fr.txt")

    generate_log_file("temp_logs/access_log_rps.txt", num_entries=500, region="RPS")
    log_files.append("temp_logs/access_log_rps.txt")

    generate_log_file("temp_logs/access_log_gb.txt", num_entries=400, region="GB")
    log_files.append("temp_logs/access_log_gb.txt")

    # Crear ZIP
    zip_filename = "logs_ejemplo.zip"
    print(f"\nCreando {zip_filename}...")

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for log_file in log_files:
            zipf.write(log_file, os.path.basename(log_file))

    print(f"  ✅ {zip_filename} creado")

    # Limpiar archivos temporales
    print("\nLimpiando archivos temporales...")
    for log_file in log_files:
        os.remove(log_file)
    os.rmdir("temp_logs")

    print("\n" + "="*80)
    print("✅ Logs de ejemplo generados exitosamente")
    print("="*80)
    print(f"\nArchivo generado: {zip_filename}")
    print(f"Total de archivos de log: {len(log_files)}")
    print("\nAhora puedes probar el procesador con:")
    print(f"  python process_logs.py {zip_filename} --month 2024-01-01 --no-upload --output-json results.json")
    print()


def create_nested_zip():
    """Crea un ZIP con ZIPs anidados para probar extracción recursiva"""
    print("\n" + "="*80)
    print("Generando ZIP con archivos anidados")
    print("="*80 + "\n")

    # Crear directorio temporal
    os.makedirs("temp_nested", exist_ok=True)

    # Generar logs
    generate_log_file("temp_nested/log1.txt", num_entries=500, region="AU")
    generate_log_file("temp_nested/log2.txt", num_entries=500, region="UK")

    # Crear ZIP interno
    print("\nCreando ZIP interno...")
    with zipfile.ZipFile("temp_nested/inner.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("temp_nested/log1.txt", "log1.txt")
        zipf.write("temp_nested/log2.txt", "log2.txt")

    # Generar más logs
    generate_log_file("temp_nested/log3.txt", num_entries=500, region="CA")

    # Crear ZIP externo
    print("\nCreando ZIP externo...")
    with zipfile.ZipFile("logs_nested_ejemplo.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("temp_nested/inner.zip", "region_logs/inner.zip")
        zipf.write("temp_nested/log3.txt", "region_logs/log3.txt")

    # Limpiar
    print("\nLimpiando archivos temporales...")
    for f in ["log1.txt", "log2.txt", "log3.txt", "inner.zip"]:
        if os.path.exists(f"temp_nested/{f}"):
            os.remove(f"temp_nested/{f}")
    os.rmdir("temp_nested")

    print("\n✅ logs_nested_ejemplo.zip creado")
    print("   Este ZIP contiene un ZIP anidado para probar la extracción recursiva")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--nested":
        create_nested_zip()
    else:
        create_sample_zip()

    print("\n💡 Para generar un ZIP con archivos anidados:")
    print("   python generate_sample_logs.py --nested")
    print()
