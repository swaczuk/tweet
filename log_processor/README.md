# Log Processor - Procesamiento de Logs y Carga a BigQuery

Sistema automatizado para procesar logs mensuales de servidor, extraer estadísticas de hits de bots por URL y región, y cargar los datos a BigQuery.

## 📋 Características

- ✅ Extracción recursiva de archivos ZIP (maneja ZIPs anidados)
- ✅ Parseo de logs en formato Apache/Nginx Combined Log
- ✅ Detección automática de bots (Googlebot, ChatGPT, Claude, Gemini, Perplexity, etc.)
- ✅ Identificación de regiones por URL
- ✅ Agregación de hits por URL, bot y región
- ✅ Extracción de top N URLs por región
- ✅ Carga automática a BigQuery
- ✅ Exportación a JSON
- ✅ Configuración personalizable de bots y regiones

## 🏗️ Estructura del Proyecto

```
log_processor/
├── __init__.py              # Módulo principal
├── zip_extractor.py         # Extractor de archivos ZIP recursivo
├── log_parser.py            # Parser de logs
├── data_aggregator.py       # Agregador de datos
├── bigquery_uploader.py     # Uploader a BigQuery
├── process_logs.py          # Script principal
├── config.example.json      # Configuración de ejemplo
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

## 📦 Instalación

### 1. Instalar dependencias

```bash
cd log_processor
pip install -r requirements.txt
```

### 2. Configurar credenciales de Google Cloud

#### Opción A: Usar archivo de credenciales (Recomendado)

1. Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilita la API de BigQuery
3. Crea una cuenta de servicio con permisos de BigQuery
4. Descarga el archivo JSON de credenciales
5. Guarda el archivo en un lugar seguro (ej: `~/gcp-credentials.json`)

#### Opción B: Usar credenciales por defecto

```bash
gcloud auth application-default login
```

### 3. Crear dataset y tabla en BigQuery (Opcional)

El script puede crear la tabla automáticamente, pero puedes crearla manualmente:

```sql
CREATE TABLE IF NOT EXISTS `tu-proyecto.analytics_logs.bot_hits_by_url` (
  month DATE NOT NULL,
  region STRING NOT NULL,
  url STRING NOT NULL,
  bot STRING NOT NULL,
  hits INTEGER NOT NULL,
  upload_timestamp TIMESTAMP NOT NULL
);
```

## 🚀 Uso

### Uso Básico

```bash
python process_logs.py logs_enero_2024.zip \
  --month 2024-01-01 \
  --project-id tu-proyecto-gcp \
  --dataset-id analytics_logs \
  --table-id bot_hits_by_url \
  --credentials ~/gcp-credentials.json
```

### Opciones Avanzadas

```bash
# Extraer top 100 URLs en lugar de 50
python process_logs.py logs.zip \
  --month 2024-01-01 \
  --project-id tu-proyecto-gcp \
  --dataset-id analytics_logs \
  --top-n 100 \
  --credentials ~/gcp-credentials.json

# Solo procesar, no subir a BigQuery (útil para pruebas)
python process_logs.py logs.zip \
  --month 2024-01-01 \
  --project-id tu-proyecto-gcp \
  --dataset-id analytics_logs \
  --no-upload \
  --output-json results.json

# Reemplazar datos existentes del mes
python process_logs.py logs.zip \
  --month 2024-01-01 \
  --project-id tu-proyecto-gcp \
  --dataset-id analytics_logs \
  --replace \
  --credentials ~/gcp-credentials.json

# Usar bots personalizados
python process_logs.py logs.zip \
  --month 2024-01-01 \
  --project-id tu-proyecto-gcp \
  --dataset-id analytics_logs \
  --custom-bots custom_bots.json \
  --credentials ~/gcp-credentials.json
```

### Archivo de Bots Personalizados

Crea un archivo JSON con bots adicionales:

```json
{
  "MiBot": "MiBot\\/\\d+\\.\\d+",
  "OtroCrawler": "OtroCrawler",
  "CustomBot": "CustomBot.*"
}
```

## 📊 Esquema de BigQuery

La tabla en BigQuery tiene la siguiente estructura:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `month` | DATE | Mes de los datos (formato: YYYY-MM-01) |
| `region` | STRING | Código de región (AU, UK, CA, CA-FR, RPS, GB, MAIN) |
| `url` | STRING | URL completa |
| `bot` | STRING | Nombre del bot (Googlebot, GPTBot, ClaudeBot, etc.) |
| `hits` | INTEGER | Número de hits recibidos |
| `upload_timestamp` | TIMESTAMP | Timestamp de cuando se subieron los datos |

## 🤖 Bots Detectados

El sistema detecta automáticamente los siguientes bots:

### Motores de Búsqueda
- Googlebot
- Bingbot
- Yahoo! Slurp
- DuckDuckBot
- Baiduspider
- YandexBot

### IA Conversacional
- GPTBot (ChatGPT)
- Google-Extended
- ClaudeBot (Claude)
- PerplexityBot
- Gemini (via Google-Extended)

### Otros
- Applebot
- facebookexternalhit
- LinkedInBot
- Twitterbot
- Slackbot
- Discordbot
- Internet Archive
- SEO crawlers (SemrushBot, AhrefsBot, etc.)

## 🌍 Regiones Detectadas

El sistema identifica las siguientes regiones basándose en las URLs:

| Región | Patrón | Ejemplo |
|--------|--------|---------|
| AU | `/au/` | `www.ajg.com/au/page` |
| UK | `/uk/` | `www.ajg.com/uk/page` |
| CA | `/ca/` | `www.ajg.com/ca/page` |
| CA-FR | `/ca-fr/` | `www.ajg.com/ca-fr/page` |
| RPS | `rpsins.com` | `www.rpsins.com/page` |
| GB | `gallagherbassett.com` | `www.gallagherbassett.com/page` |
| MAIN | `www.ajg.com` (sin subdirectorio regional) | `www.ajg.com/page` |

## 📝 Formato de Log Soportado

El parser soporta el formato Combined Log de Apache/Nginx:

```
192.168.1.1 - - [01/Jan/2024:12:00:00 +0000] "GET /au/page HTTP/1.1" 200 1234 "https://google.com" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
```

## 🔧 Uso Programático

También puedes usar los módulos directamente en tu código Python:

```python
from log_processor import LogProcessor

# Crear procesador
processor = LogProcessor(
    project_id="tu-proyecto-gcp",
    dataset_id="analytics_logs",
    table_id="bot_hits_by_url",
    credentials_path="~/gcp-credentials.json",
    top_n=50
)

# Procesar logs y subir a BigQuery
processor.run(
    zip_path="logs_enero_2024.zip",
    month="2024-01-01",
    upload=True,
    replace=False,
    output_json="results.json"
)
```

### Usar módulos individuales

```python
from log_processor import ZipExtractor, LogParser, DataAggregator

# Extraer archivos
with ZipExtractor() as extractor:
    txt_files = extractor.process_zip("logs.zip")

# Parsear logs
parser = LogParser()
for txt_file in txt_files:
    entries = parser.parse_file(txt_file)

    # Agregar datos
    aggregator = DataAggregator()
    aggregator.add_entries(entries)

# Obtener top URLs
top_urls = aggregator.get_top_urls_by_region("AU", top_n=50)
```

## 📈 Consultas de BigQuery

### Top 10 URLs globalmente

```sql
SELECT
  url,
  region,
  SUM(hits) as total_hits
FROM `tu-proyecto.analytics_logs.bot_hits_by_url`
WHERE month = '2024-01-01'
GROUP BY url, region
ORDER BY total_hits DESC
LIMIT 10;
```

### Hits por bot por región

```sql
SELECT
  region,
  bot,
  SUM(hits) as total_hits
FROM `tu-proyecto.analytics_logs.bot_hits_by_url`
WHERE month = '2024-01-01'
GROUP BY region, bot
ORDER BY region, total_hits DESC;
```

### Comparación mes a mes

```sql
SELECT
  month,
  region,
  SUM(hits) as total_hits
FROM `tu-proyecto.analytics_logs.bot_hits_by_url`
WHERE month >= '2024-01-01' AND month < '2024-07-01'
GROUP BY month, region
ORDER BY month, region;
```

### Top URLs por bot específico

```sql
SELECT
  url,
  region,
  SUM(hits) as total_hits
FROM `tu-proyecto.analytics_logs.bot_hits_by_url`
WHERE month = '2024-01-01' AND bot = 'GPTBot'
GROUP BY url, region
ORDER BY total_hits DESC
LIMIT 50;
```

## 🐛 Troubleshooting

### Error: "No se encontraron archivos .txt"

- Verifica que el ZIP contenga archivos .txt
- Asegúrate de que los archivos tengan la extensión correcta
- Los archivos pueden estar en carpetas dentro del ZIP

### Error: "No se encontraron entradas de bots"

- Verifica el formato de los logs
- Asegúrate de que los logs contengan User-Agents de bots
- Usa `--output-json` para ver qué se está parseando

### Error de autenticación con BigQuery

- Verifica que el archivo de credenciales sea válido
- Asegúrate de tener permisos en BigQuery
- Prueba con `gcloud auth application-default login`

### El parser no detecta mi bot

- Agrega el bot con `--custom-bots` y un archivo JSON
- O modifica el archivo `log_parser.py` para agregar el bot permanentemente

## 🔒 Seguridad

- **Credenciales**: NUNCA commitas archivos de credenciales al repositorio
- **Permisos**: Usa cuentas de servicio con permisos mínimos necesarios
- **Logs**: Los logs pueden contener información sensible, manéjalos con cuidado

## 📄 Licencia

Este proyecto es para uso interno de la organización.

## 🤝 Contribuir

Para agregar funcionalidades o reportar bugs, contacta al equipo de desarrollo.

## 📞 Soporte

Para preguntas o problemas, contacta a:
- Email: [tu-email@ejemplo.com]
- Slack: #analytics-team

## 📚 Recursos Adicionales

- [Documentación de BigQuery](https://cloud.google.com/bigquery/docs)
- [Google Cloud Python Client](https://github.com/googleapis/python-bigquery)
- [Apache Log Format](https://httpd.apache.org/docs/current/logs.html)
