#!/usr/bin/env python3
"""
Flask API server for Google AI Mode Scraper
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google_ai_scraper import GoogleAIModeScraper, AIModeScrapeResult
from dataclasses import asdict
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Initialize scraper (shared instance)
scraper = None
DEBUG_MODE = False  # Set to True to show browser window


def get_scraper():
    """Get or create scraper instance"""
    global scraper
    if scraper is None:
        scraper = GoogleAIModeScraper(headless=not DEBUG_MODE)
    return scraper


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')


@app.route('/styles/<path:path>')
def serve_styles(path):
    """Serve CSS files"""
    return send_from_directory('styles', path)


@app.route('/api/scrape', methods=['POST'])
def scrape():
    """
    Scrape Google AI Mode results

    Expected JSON payload:
    {
        "query": "search query",
        "language": "en",
        "region": "US"
    }
    """
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing required field: query'
            }), 400

        query = data.get('query')
        language = data.get('language', 'en')
        region = data.get('region', 'US')
        wait_time = data.get('wait_time', 5)

        # Validate inputs
        if not query.strip():
            return jsonify({
                'error': 'Query cannot be empty'
            }), 400

        # Perform scraping
        scraper_instance = get_scraper()
        result = scraper_instance.scrape(
            query=query,
            language=language,
            region=region,
            wait_time=wait_time
        )

        # Convert to dict and return
        return jsonify(asdict(result))

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/scrape/batch', methods=['POST'])
def scrape_batch():
    """
    Scrape multiple queries at once

    Expected JSON payload:
    {
        "queries": ["query1", "query2", ...],
        "language": "en",
        "region": "US"
    }
    """
    try:
        data = request.get_json()

        if not data or 'queries' not in data:
            return jsonify({
                'error': 'Missing required field: queries'
            }), 400

        queries = data.get('queries')
        language = data.get('language', 'en')
        region = data.get('region', 'US')

        if not isinstance(queries, list) or len(queries) == 0:
            return jsonify({
                'error': 'Queries must be a non-empty list'
            }), 400

        # Perform batch scraping
        scraper_instance = get_scraper()
        results = scraper_instance.scrape_batch(
            queries=queries,
            language=language,
            region=region
        )

        # Convert to dict and return
        return jsonify([asdict(r) for r in results])

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'selenium_available': 'selenium' in globals()
    })


@app.teardown_appcontext
def cleanup(error=None):
    """Cleanup scraper on app shutdown"""
    global scraper
    if scraper:
        scraper.close()
        scraper = None


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Google AI Mode Scraper API Server')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Port to run server on')
    parser.add_argument('-H', '--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('-d', '--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--show-browser', action='store_true', help='Show browser window (for debugging)')

    args = parser.parse_args()

    # Set debug mode if --show-browser is enabled
    DEBUG_MODE = args.show_browser

    print(f"Starting Google AI Mode Scraper API on {args.host}:{args.port}")
    if DEBUG_MODE:
        print("⚠️  DEBUG MODE: Browser window will be VISIBLE")
    print(f"Open http://{args.host}:{args.port} in your browser")

    app.run(host=args.host, port=args.port, debug=args.debug)
