#!/usr/bin/env python3
"""
Google AI Mode Scraper
Extracts AI-generated highlights, URLs, titles, and meta descriptions from Google Search
"""

import json
import time
import argparse
from typing import Dict, List, Optional
from urllib.parse import quote_plus, urlencode
from dataclasses import dataclass, asdict

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError as e:
    SELENIUM_AVAILABLE = False
    WEBDRIVER_MANAGER_AVAILABLE = False
    print(f"Warning: Selenium/webdriver-manager not available. Install with: pip install selenium webdriver-manager")
    print(f"Error details: {e}")

try:
    from bs4 import BeautifulSoup
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests/beautifulsoup4 not available. Install with: pip install requests beautifulsoup4")


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
    """Scraper for Google AI Mode (SGE) search results"""

    def __init__(self, headless: bool = True):
        """
        Initialize the scraper

        Args:
            headless: Run browser in headless mode (no GUI)
        """
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required for this scraper. Install with: pip install selenium")

        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Add experimental options to avoid detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Use webdriver-manager to automatically handle ChromeDriver versions
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Fallback to using system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Error initializing ChromeDriver: {e}")
            print("Tip: Install webdriver-manager with: pip install webdriver-manager")
            raise

        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

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

    def scrape(self, query: str, language: str = 'en', region: str = 'US', wait_time: int = 5) -> AIModeScrapeResult:
        """
        Scrape Google AI Mode results

        Args:
            query: Search query
            language: Language code
            region: Region code
            wait_time: Time to wait for page load (seconds)

        Returns:
            AIModeScrapeResult with extracted data
        """
        if self.driver is None:
            self._init_driver()

        result = AIModeScrapeResult(query=query, language=language, region=region)

        try:
            # Navigate to Google Search
            url = self._build_google_url(query, language, region)
            self.driver.get(url)

            # Wait for page to load
            time.sleep(wait_time)

            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract AI Overview/Summary
            result.ai_overview = self._extract_ai_overview(soup)

            # Extract search results
            result.results = self._extract_search_results(soup)

        except Exception as e:
            print(f"Error during scraping: {e}")

        return result

    def _extract_ai_overview(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Extract AI-generated overview text

        Args:
            soup: BeautifulSoup object of the page

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
            'div[class*="Wnoohf"]'
        ]

        for selector in ai_selectors:
            elements = soup.select(selector)
            if elements:
                # Get text from all matching elements
                text_parts = []
                for elem in elements:
                    text = elem.get_text(strip=True, separator=' ')
                    if text:
                        text_parts.append(text)

                if text_parts:
                    return ' '.join(text_parts)

        return None

    def _extract_search_results(self, soup: BeautifulSoup) -> List[SearchResult]:
        """
        Extract regular search results with AI highlights

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            List of SearchResult objects
        """
        results = []

        # Find all search result divs
        # Google uses various class names, these are common ones
        result_divs = soup.select('div.g, div[data-sokoban-container], div.Gx5Zad')

        for div in result_divs:
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
                desc_elem = div.select_one('div[data-sncf], div.VwiC3b, div[style*="-webkit-line-clamp"]')
                meta_description = desc_elem.get_text(strip=True) if desc_elem else ''

                # Extract AI highlight (if present)
                ai_highlight = None
                highlight_elem = div.select_one('span[style*="background"], mark, em.highlighted')
                if highlight_elem:
                    ai_highlight = highlight_elem.get_text(strip=True)

                # Only add if we have at least a title and URL
                if title and url:
                    results.append(SearchResult(
                        url=url,
                        title=title,
                        meta_description=meta_description,
                        ai_highlight=ai_highlight
                    ))

            except Exception as e:
                print(f"Error extracting result: {e}")
                continue

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
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None

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
