#!/usr/bin/env python3
"""
Capture page HTML to analyze structure and update selectors
"""

from google_ai_scraper import GoogleAIModeScraper
import sys

def capture_html():
    query = input("Enter search query (or press Enter for default): ").strip()
    if not query:
        query = "artificial intelligence"

    print(f"\n🔍 Capturing HTML for: {query}")
    print("Browser will open - solve CAPTCHA if needed\n")

    with GoogleAIModeScraper(headless=False) as scraper:
        # Initialize the browser
        scraper._init_browser()

        # Navigate to the page
        url = scraper._build_google_url(query, language="en", region="US")
        print(f"🔗 URL: {url}\n")

        scraper.page.goto(url, wait_until='networkidle', timeout=30000)

        # Wait for user
        print("\n" + "="*60)
        print("🤖 PAUSED - Solve CAPTCHA if needed")
        print("="*60)
        print("After solving CAPTCHA (if any), press ENTER to capture HTML...")
        input()

        # Give a moment for page to settle
        import time
        time.sleep(3)

        # Get the HTML
        html_content = scraper.page.content()

        # Save to file
        output_file = "google_ai_mode_page.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n✅ HTML saved to: {output_file}")
        print(f"   File size: {len(html_content)} bytes")
        print()
        print("📝 Next steps:")
        print("   1. Open the HTML file in a text editor")
        print("   2. Look for the search results structure")
        print("   3. Find the CSS classes/IDs used for results")
        print()

if __name__ == '__main__':
    try:
        capture_html()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
