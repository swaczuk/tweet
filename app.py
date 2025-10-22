#!/usr/bin/env python3
"""
Flask API server for Google AI Mode Scraper
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from google_ai_scraper import GoogleAIModeScraper
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Global config - Browser visible by default to handle CAPTCHAs
# Google almost always shows CAPTCHA, so visible browser is needed
SHOW_BROWSER = True  # Set to False for headless mode


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

        # Perform scraping with new instance (avoid threading issues)
        # Browser visible by default to handle CAPTCHAs
        with GoogleAIModeScraper(headless=not SHOW_BROWSER) as scraper:
            result = scraper.scrape(
                query=query,
                language=language,
                region=region,
                wait_time=wait_time,
                wait_for_user=SHOW_BROWSER  # Pause for CAPTCHA if browser is visible
            )

        # Convert to structured dict and return
        return jsonify(result.to_structured_dict())

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

        # Perform batch scraping with new instance (avoid threading issues)
        with GoogleAIModeScraper(headless=not SHOW_BROWSER) as scraper:
            results = scraper.scrape_batch(
                queries=queries,
                language=language,
                region=region
            )

        # Convert to structured dict and return
        return jsonify([r.to_structured_dict() for r in results])

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'playwright_available': True
    })


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Google AI Mode Scraper API Server')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Port to run server on')
    parser.add_argument('-H', '--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('-d', '--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode (invisible). Not recommended - CAPTCHAs cannot be solved.')

    args = parser.parse_args()

    # Browser is visible by default, unless --headless is specified
    SHOW_BROWSER = not args.headless

    print(f"Starting Google AI Mode Scraper API on {args.host}:{args.port}")
    print(f"Browser mode: {'HEADLESS (invisible)' if args.headless else 'VISIBLE'}")
    if not args.headless:
        print("ℹ️  Browser will open automatically for CAPTCHA solving")
        print("   The terminal will pause - solve CAPTCHA and press ENTER to continue")
    print(f"Open http://{args.host}:{args.port} in your browser")
    print()

    app.run(host=args.host, port=args.port, debug=args.debug)
