#!/usr/bin/env python3
"""
Google AI Mode Scraper
Extracts AI-generated highlights, URLs, titles, and meta descriptions from Google Search
Uses Playwright with Chromium for reliable browser automation
"""

import json
import time
import argparse
from typing import Dict, List, Optional
from urllib.parse import quote_plus, urlencode
from dataclasses import dataclass, asdict

try:
    from playwright.sync_api import sync_playwright, Browser, Page, Playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not available. Install with: pip install playwright")
    print("After installation, run: playwright install chromium")

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    print("Warning: beautifulsoup4 not available. Install with: pip install beautifulsoup4")


@dataclass
class SearchResult:
    """Data class for a single search result"""
    url: str
    title: str
    meta_description: str
    ai_highlight: Optional[str] = None


@dataclass
class AIModeScrapeResult:
    """Data class for the complete scrape result"""
    query: str
    language: str
    region: str
    ai_overview: Optional[str] = None
    results: List[SearchResult] = None

    def __post_init__(self):
        if self.results is None:
            self.results = []


class GoogleAIModeScraper:
    """Scraper for Google AI Mode (SGE) search results using Playwright"""

    def __init__(self, headless: bool = True):
        """
        Initialize the scraper

        Args:
            headless: Run browser in headless mode (no GUI)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright is required for this scraper.\n"
                "Install with:\n"
                "  pip install playwright\n"
                "  playwright install chromium"
            )

        if not BEAUTIFULSOUP_AVAILABLE:
            raise ImportError("BeautifulSoup4 is required. Install with: pip install beautifulsoup4")

        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _init_browser(self):
        """Initialize Playwright browser"""
        if self.playwright is None:
            self.playwright = sync_playwright().start()

            # Launch Chromium browser
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            # Create browser context with custom user agent
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )

            # Create new page
            self.page = self.context.new_page()

            # Remove webdriver detection
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

    def _build_google_url(self, query: str, language: str = 'en', region: str = 'US') -> str:
        """
        Build Google Search URL with AI Mode parameters

        Args:
            query: Search query
            language: Language code (e.g., 'en', 'es', 'fr')
            region: Region code (e.g., 'US', 'GB', 'ES')

        Returns:
            Complete Google Search URL
        """
        params = {
            'q': query,
            'hl': language,  # Interface language
            'gl': region,    # Geographic location
            'udm': '14',     # AI Mode parameter (may change)
        }

        base_url = 'https://www.google.com/search'
        return f"{base_url}?{urlencode(params)}"

    def scrape(self, query: str, language: str = 'en', region: str = 'US', wait_time: int = 5, verbose: bool = False, wait_for_user: bool = False) -> AIModeScrapeResult:
        """
        Scrape Google AI Mode results

        Args:
            query: Search query
            language: Language code
            region: Region code
            wait_time: Time to wait for page load (seconds)
            verbose: Print debug information
            wait_for_user: Wait for user input before extracting (useful for CAPTCHAs)

        Returns:
            AIModeScrapeResult with extracted data
        """
        if self.browser is None:
            self._init_browser()

        result = AIModeScrapeResult(query=query, language=language, region=region)

        try:
            # Navigate to Google Search
            url = self._build_google_url(query, language, region)
            if verbose:
                print(f"🔗 Navigating to: {url}")

            self.page.goto(url, wait_until='networkidle', timeout=30000)

            # Wait for page to load completely
            if verbose:
                print(f"⏳ Waiting {wait_time} seconds for page to load...")
            time.sleep(wait_time)

            # Check for CAPTCHA
            page_content_check = self.page.content()
            if 'captcha' in page_content_check.lower() or 'recaptcha' in page_content_check.lower():
                if verbose:
                    print("⚠️  CAPTCHA detected!")
                wait_for_user = True

            # Wait for user to solve CAPTCHA if needed
            if wait_for_user:
                print("\n" + "="*60)
                print("🤖 PAUSED - Solve the CAPTCHA in the browser window")
                print("="*60)
                print("After solving the CAPTCHA, press ENTER to continue...")
                input()
                print("✅ Continuing...\n")
                # Give extra time after CAPTCHA
                time.sleep(3)

            # Get page content
            page_content = self.page.content()
            soup = BeautifulSoup(page_content, 'html.parser')

            if verbose:
                print(f"📄 Page loaded, HTML size: {len(page_content)} bytes")
                print(f"🔍 Extracting AI Overview...")

            # Extract AI Overview/Summary
            result.ai_overview = self._extract_ai_overview(soup, verbose=verbose)

            if verbose:
                print(f"🔍 Extracting search results...")

            # Extract search results
            result.results = self._extract_search_results(soup, verbose=verbose)

            if verbose:
                print(f"✅ Extraction complete!")
                print(f"   - AI Overview: {'Found' if result.ai_overview else 'Not found'}")
                print(f"   - Results: {len(result.results)} found")

        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()

        return result

    def _extract_ai_overview(self, soup: BeautifulSoup, verbose: bool = False) -> Optional[str]:
        """
        Extract AI-generated overview text

        Args:
            soup: BeautifulSoup object of the page
            verbose: Print debug information

        Returns:
            AI overview text or None
        """
        # AI Mode overview selectors (these may need updating as Google changes the UI)
        ai_selectors = [
            'div[data-attrid="SGE"]',
            'div[class*="AI-generated"]',
            'div[class*="ai-overview"]',
            'div[jsname*="yEVEE"]',
            'div[class*="VwiC3b"]',
            'div[class*="Wnoohf"]',
            'div[data-hveid]',  # Common Google container
            'div.g-blk',  # AI block
        ]

        for selector in ai_selectors:
            elements = soup.select(selector)
            if verbose and elements:
                print(f"   Found {len(elements)} elements with selector: {selector}")

            if elements:
                # Get text from all matching elements
                text_parts = []
                for elem in elements:
                    text = elem.get_text(strip=True, separator=' ')
                    if text and len(text) > 50:  # Filter out very short snippets
                        text_parts.append(text)

                if text_parts:
                    if verbose:
                        print(f"   ✅ AI Overview extracted ({len(' '.join(text_parts))} chars)")
                    return ' '.join(text_parts)

        if verbose:
            print(f"   ⚠️  No AI Overview found with any selector")
        return None

    def _extract_search_results(self, soup: BeautifulSoup, verbose: bool = False) -> List[SearchResult]:
        """
        Extract regular search results with AI highlights

        Args:
            soup: BeautifulSoup object of the page
            verbose: Print debug information

        Returns:
            List of SearchResult objects
        """
        results = []

        # Find all search result divs
        # Google uses various class names, these are common ones
        result_divs = soup.select('div.g, div[data-sokoban-container], div.Gx5Zad, div.MjjYud')

        if verbose:
            print(f"   Found {len(result_divs)} potential result containers")

        for i, div in enumerate(result_divs):
            try:
                # Extract title
                title_elem = div.select_one('h3')
                title = title_elem.get_text(strip=True) if title_elem else ''

                # Extract URL
                link_elem = div.select_one('a')
                url = link_elem.get('href', '') if link_elem else ''

                # Clean URL if it's a Google redirect
                if url.startswith('/url?'):
                    import re
                    match = re.search(r'url=([^&]+)', url)
                    if match:
                        from urllib.parse import unquote
                        url = unquote(match.group(1))

                # Extract meta description
                desc_elem = div.select_one('div[data-sncf], div.VwiC3b, div[style*="-webkit-line-clamp"], span.aCOpRe')
                meta_description = desc_elem.get_text(strip=True) if desc_elem else ''

                # Extract AI highlight (if present)
                ai_highlight = None
                highlight_elem = div.select_one('span[style*="background"], mark, em.highlighted, b, strong')
                if highlight_elem:
                    ai_highlight = highlight_elem.get_text(strip=True)

                # Only add if we have at least a title and URL
                if title and url and url.startswith('http'):
                    results.append(SearchResult(
                        url=url,
                        title=title,
                        meta_description=meta_description,
                        ai_highlight=ai_highlight
                    ))
                    if verbose:
                        print(f"   ✓ Result {len(results)}: {title[:50]}...")
                elif verbose:
                    print(f"   ✗ Skipped div {i+1}: title='{title[:30] if title else 'none'}', url='{url[:50] if url else 'none'}'")

            except Exception as e:
                if verbose:
                    print(f"   ⚠️  Error extracting result {i+1}: {e}")
                continue

        if verbose:
            print(f"   ✅ Total valid results: {len(results)}")

        return results

    def scrape_batch(self, queries: List[str], language: str = 'en', region: str = 'US') -> List[AIModeScrapeResult]:
        """
        Scrape multiple queries

        Args:
            queries: List of search queries
            language: Language code
            region: Region code

        Returns:
            List of AIModeScrapeResult objects
        """
        results = []
        for query in queries:
            print(f"Scraping: {query}")
            result = self.scrape(query, language, region)
            results.append(result)

            # Be polite and add delay between requests
            time.sleep(2)

        return results

    def close(self):
        """Close the browser and cleanup"""
        if self.page:
            self.page.close()
            self.page = None

        if self.context:
            self.context.close()
            self.context = None

        if self.browser:
            self.browser.close()
            self.browser = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def save_results(results: AIModeScrapeResult, output_file: str):
    """
    Save results to JSON file

    Args:
        results: AIModeScrapeResult object or list of objects
        output_file: Path to output file
    """
    if isinstance(results, list):
        data = [asdict(r) for r in results]
    else:
        data = asdict(results)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_file}")


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description='Scrape Google AI Mode search results')
    parser.add_argument('query', help='Search query')
    parser.add_argument('-l', '--language', default='en', help='Language code (default: en)')
    parser.add_argument('-r', '--region', default='US', help='Region code (default: US)')
    parser.add_argument('-o', '--output', help='Output JSON file')
    parser.add_argument('--no-headless', action='store_true', help='Show browser window')
    parser.add_argument('-w', '--wait', type=int, default=5, help='Wait time for page load (default: 5s)')

    args = parser.parse_args()

    # Run scraper
    with GoogleAIModeScraper(headless=not args.no_headless) as scraper:
        result = scraper.scrape(args.query, args.language, args.region, args.wait)

        # Print results
        print(f"\n{'='*60}")
        print(f"Query: {result.query}")
        print(f"Language: {result.language} | Region: {result.region}")
        print(f"{'='*60}\n")

        if result.ai_overview:
            print(f"AI Overview:\n{result.ai_overview}\n")
            print(f"{'-'*60}\n")

        print(f"Found {len(result.results)} results:\n")

        for i, res in enumerate(result.results, 1):
            print(f"{i}. {res.title}")
            print(f"   URL: {res.url}")
            if res.meta_description:
                print(f"   Description: {res.meta_description[:150]}...")
            if res.ai_highlight:
                print(f"   AI Highlight: {res.ai_highlight}")
            print()

        # Save to file if specified
        if args.output:
            save_results(result, args.output)


if __name__ == '__main__':
    main()
