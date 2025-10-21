#!/usr/bin/env python3
"""
Manual debug script - Always pauses for user interaction
Useful for solving CAPTCHAs and inspecting the page
"""

from google_ai_scraper import GoogleAIModeScraper
import json

def manual_test():
    """Test the scraper with manual control"""
    print("=" * 60)
    print("Google AI Mode Scraper - MANUAL MODE")
    print("=" * 60)
    print()
    print("This script will ALWAYS pause after loading the page.")
    print("You can:")
    print("  - Solve CAPTCHAs")
    print("  - Inspect the page")
    print("  - Wait for content to load")
    print()

    # Get search query from user
    query = input("Enter search query (or press Enter for default): ").strip()
    if not query:
        query = "what is artificial intelligence"

    language = input("Language code (default: en): ").strip() or "en"
    region = input("Region code (default: US): ").strip() or "US"

    print(f"\n🔍 Searching for: {query}")
    print(f"🌍 Language: {language}, Region: {region}")
    print("\n⚠️  The script will pause after loading - you'll have time to solve any CAPTCHAs")
    print()

    # Create scraper with visible browser
    with GoogleAIModeScraper(headless=False) as scraper:
        result = scraper.scrape(
            query=query,
            language=language,
            region=region,
            wait_time=3,
            verbose=True,
            wait_for_user=True  # ALWAYS pause for user
        )

        print("\n" + "=" * 60)
        print("EXTRACTION RESULTS")
        print("=" * 60)

        print(f"\nQuery: {result.query}")
        print(f"Language: {result.language}")
        print(f"Region: {result.region}")

        if result.ai_overview:
            print(f"\n📝 AI Overview Found ({len(result.ai_overview)} characters):")
            print("-" * 60)
            print(result.ai_overview[:500] + "..." if len(result.ai_overview) > 500 else result.ai_overview)
        else:
            print("\n⚠️  No AI Overview found")
            print("This is normal - Google AI Mode may not be available in your region")

        print(f"\n🔍 Search Results: {len(result.results)} found")
        print("-" * 60)

        if result.results:
            for i, res in enumerate(result.results, 1):
                print(f"\n{i}. {res.title}")
                print(f"   URL: {res.url[:80]}...")
                if res.meta_description:
                    desc = res.meta_description[:150]
                    print(f"   Description: {desc}...")
                if res.ai_highlight:
                    print(f"   ✨ AI Highlight: {res.ai_highlight}")
        else:
            print("\n⚠️  No search results found")
            print("\nPossible reasons:")
            print("1. CAPTCHA wasn't solved correctly")
            print("2. The page didn't load properly")
            print("3. CSS selectors need updating")
            print("4. You're being rate-limited by Google")

        # Save to file
        output_file = "manual_debug_results.json"
        data = {
            'query': result.query,
            'language': result.language,
            'region': result.region,
            'ai_overview': result.ai_overview,
            'results_count': len(result.results),
            'results': [
                {
                    'url': r.url,
                    'title': r.title,
                    'meta_description': r.meta_description,
                    'ai_highlight': r.ai_highlight
                }
                for r in result.results
            ]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Full results saved to: {output_file}")

        # Ask if user wants to see the raw HTML
        see_html = input("\nDo you want to save the raw HTML? (y/n): ").strip().lower()
        if see_html == 'y':
            # Get the current page HTML
            html_file = "page_source.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(scraper.page.content())
            print(f"📄 Raw HTML saved to: {html_file}")
            print("   You can open this in a browser to inspect the structure")

        print()

if __name__ == '__main__':
    try:
        manual_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
