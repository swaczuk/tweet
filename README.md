# Google AI Mode Scraper

A comprehensive web scraper for extracting AI-generated highlights, URLs, titles, and meta descriptions from Google's AI Mode (formerly SGE - Search Generative Experience) search results.

## Features

- Extract AI-generated overview/summary from Google AI Mode
- Retrieve URLs, titles, and meta descriptions from search results
- Capture AI-highlighted snippets from search results
- Support for multiple languages and regions
- Both CLI and web interface options
- Batch scraping support
- Export results to JSON

## Project Structure

```
.
├── google_ai_scraper.py  # Core scraper logic
├── app.py                # Flask API server
├── index.html            # Web interface
├── styles/
│   └── styles.css        # Styling for web interface
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- ChromeDriver (automatically managed by selenium)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd tweet
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install ChromeDriver

The scraper uses Selenium with Chrome. ChromeDriver will be managed automatically, but ensure you have Google Chrome installed on your system.

## Usage

### Option 1: Web Interface (Recommended)

1. Start the Flask server:

```bash
python app.py
```

2. Open your browser and navigate to:

```
http://127.0.0.1:5000
```

3. Enter your search query, select language and region, then click "Scrape Results"

4. View the AI overview and search results, or export as JSON

**Server Options:**

```bash
# Run on different port
python app.py -p 8080

# Run on all network interfaces
python app.py -H 0.0.0.0

# Run in debug mode
python app.py -d
```

### Option 2: Command Line Interface

Run the scraper directly from the command line:

```bash
# Basic usage
python google_ai_scraper.py "your search query"

# With language and region
python google_ai_scraper.py "climate change solutions" -l en -r US

# Export to JSON
python google_ai_scraper.py "artificial intelligence" -o results.json

# Show browser window (not headless)
python google_ai_scraper.py "machine learning" --no-headless

# Custom wait time (for slow connections)
python google_ai_scraper.py "deep learning" -w 10
```

**CLI Options:**

- `-l, --language`: Language code (default: en)
- `-r, --region`: Region code (default: US)
- `-o, --output`: Output JSON file
- `--no-headless`: Show browser window
- `-w, --wait`: Wait time for page load in seconds (default: 5)

### Option 3: Python API

Use the scraper in your own Python code:

```python
from google_ai_scraper import GoogleAIModeScraper

# Initialize scraper
with GoogleAIModeScraper(headless=True) as scraper:
    # Single query
    result = scraper.scrape(
        query="best practices for web scraping",
        language="en",
        region="US"
    )

    # Access results
    print(f"AI Overview: {result.ai_overview}")

    for res in result.results:
        print(f"Title: {res.title}")
        print(f"URL: {res.url}")
        print(f"Description: {res.meta_description}")
        print(f"AI Highlight: {res.ai_highlight}")
        print()

# Batch scraping
with GoogleAIModeScraper() as scraper:
    queries = [
        "machine learning",
        "deep learning",
        "neural networks"
    ]

    results = scraper.scrape_batch(queries, language="en", region="US")

    for result in results:
        print(f"Query: {result.query}")
        print(f"Results found: {len(result.results)}")
```

## API Endpoints

If using the Flask server, the following endpoints are available:

### POST /api/scrape

Scrape a single query.

**Request:**
```json
{
  "query": "search query",
  "language": "en",
  "region": "US",
  "wait_time": 5
}
```

**Response:**
```json
{
  "query": "search query",
  "language": "en",
  "region": "US",
  "ai_overview": "AI-generated overview text...",
  "results": [
    {
      "url": "https://example.com",
      "title": "Page Title",
      "meta_description": "Description...",
      "ai_highlight": "Highlighted text..."
    }
  ]
}
```

### POST /api/scrape/batch

Scrape multiple queries.

**Request:**
```json
{
  "queries": ["query1", "query2"],
  "language": "en",
  "region": "US"
}
```

**Response:**
```json
[
  {
    "query": "query1",
    "language": "en",
    "region": "US",
    "ai_overview": "...",
    "results": [...]
  },
  {
    "query": "query2",
    "language": "en",
    "region": "US",
    "ai_overview": "...",
    "results": [...]
  }
]
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "selenium_available": true
}
```

## Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Japanese (ja)
- Korean (ko)
- Chinese Simplified (zh-CN)
- Chinese Traditional (zh-TW)
- Arabic (ar)
- Russian (ru)
- Dutch (nl)
- Swedish (sv)
- Polish (pl)

## Supported Regions

- US (United States)
- GB (United Kingdom)
- CA (Canada)
- AU (Australia)
- ES (Spain)
- FR (France)
- DE (Germany)
- IT (Italy)
- JP (Japan)
- KR (South Korea)
- CN (China)
- IN (India)
- BR (Brazil)
- MX (Mexico)
- NL (Netherlands)
- SE (Sweden)
- PL (Poland)

## Data Structure

### AIModeScrapeResult

```python
{
    "query": str,              # Search query
    "language": str,           # Language code
    "region": str,             # Region code
    "ai_overview": str,        # AI-generated overview (optional)
    "results": [SearchResult]  # List of search results
}
```

### SearchResult

```python
{
    "url": str,                # Result URL
    "title": str,              # Page title
    "meta_description": str,   # Meta description
    "ai_highlight": str        # AI-highlighted snippet (optional)
}
```

## Important Notes

### Rate Limiting

- Be respectful of Google's servers
- The scraper includes automatic delays between requests
- Consider implementing additional rate limiting for production use

### Google's Terms of Service

This tool is designed for educational and research purposes. Make sure you comply with Google's Terms of Service when using this scraper.

### AI Mode Availability

Google AI Mode (SGE) may not be available in all regions or for all users. The scraper attempts to access AI Mode but results may vary based on:

- Geographic location
- Google account status
- A/B testing groups
- Google's rollout schedule

### Selector Updates

Google frequently updates its HTML structure. If the scraper stops working:

1. The CSS selectors in `_extract_ai_overview()` and `_extract_search_results()` may need updating
2. Check Google's current HTML structure using browser developer tools
3. Update the selectors in `google_ai_scraper.py`

## Troubleshooting

### "ChromeDriver not found"

Install ChromeDriver or ensure Chrome is installed:

```bash
pip install webdriver-manager
```

### "Selenium not available"

Install Selenium:

```bash
pip install selenium
```

### No AI Overview extracted

- AI Mode might not be enabled for your location/account
- Try different regions or languages
- Verify AI Mode is visible when manually searching on Google
- Update the CSS selectors if Google changed the HTML structure

### Empty results

- Increase wait time: `-w 10` or `wait_time=10`
- Check your internet connection
- Verify the query returns results on Google
- Try with `--no-headless` to see what's happening

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational and research purposes only.

## Disclaimer

This tool is provided as-is for research and educational purposes. Users are responsible for ensuring their use complies with Google's Terms of Service and applicable laws. The authors are not responsible for any misuse of this tool.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.
