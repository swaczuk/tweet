# Log Processor - Guía de Bots Detectados

## 🤖 Bots de IA (Consolidados)

### ChatGPT
**Detecta:** GPTBot, ChatGPT-User, Google-Extended
- Todos los crawlers de OpenAI/ChatGPT se reportan como "ChatGPT"

### Claude
**Detecta:** ClaudeBot, Claude-Web, anthropic-ai
- Todos los crawlers de Anthropic/Claude se reportan como "Claude"

### Gemini
**Detecta:** Google-Extended, Gemini
- Bots del modelo Gemini de Google

### PerplexityBot
**Detecta:** PerplexityBot
- Bot del motor de búsqueda Perplexity AI

## 🔍 Motores de Búsqueda

- **Googlebot** - Google Search
- **Bingbot** - Microsoft Bing
- **YahooBot** - Yahoo Search
- **DuckDuckBot** - DuckDuckGo
- **Baiduspider** - Baidu (China)
- **YandexBot** - Yandex (Rusia)
- **Applebot** - Apple Siri/Spotlight

## 🛠️ Herramientas de Google

- **Google-InspectionTool** - Google Search Console
- **Google-Safety** - Google Safe Browsing

## 📱 Redes Sociales

- **FacebookBot** - Facebook link previews
- **LinkedInBot** - LinkedIn link previews
- **TwitterBot** - Twitter/X link previews
- **SlackBot** - Slack link previews
- **DiscordBot** - Discord link previews
- **TelegramBot** - Telegram link previews
- **WhatsAppBot** - WhatsApp link previews

## 📊 SEO & Analytics

- **SemrushBot** - Semrush SEO tool
- **AhrefsBot** - Ahrefs SEO tool
- **MJ12bot** - Majestic SEO
- **DotBot** - Moz/OpenSiteExplorer
- **BLEXBot** - BLEXBot crawler
- **DataForSeoBot** - DataForSEO API
- **RogerBot** - Moz's crawler
- **ScreamingFrog** - Screaming Frog SEO Spider
- **Sitebulb** - Sitebulb website auditor

## 🌐 Otros Crawlers

- **InternetArchive** - Archive.org Wayback Machine
- **PetalBot** - Huawei search
- **Bytespider** - ByteDance/TikTok
- **PingdomBot** - Pingdom monitoring
- **ImagesiftBot** - Image search bot

## 🔧 Agregar Bots Personalizados

Si necesitas agregar más bots, crea un archivo JSON:

```json
{
  "MiBot": "MiBot\\/\\d+",
  "OtroCrawler": "OtroCrawler"
}
```

Y úsalo con:
```bash
python process_logs.py logs.zip --custom-bots custom_bots.json ...
```

## 📝 Notas

- Los patrones usan regex de Python
- Los bots están ordenados por prioridad (IA primero, luego búsqueda, etc.)
- La consolidación ayuda a analizar tendencias sin fragmentación
