#!/usr/bin/env python3
"""
Debug script to test Google AI Mode scraper with visible browser
"""

from google_ai_scraper import GoogleAIModeScraper
import json

def test_scraper():
    """Test the scraper with visible browser"""
    print("=" * 60)
    print("Google AI Mode Scraper - Debug Test")
    print("=" * 60)
    print()

    # Get search query from user
    query = input("Enter search query (or press Enter for default): ").strip()
    if not query:
        query = "what is artificial intelligence"

    print(f"\nSearching for: {query}")
    print("Browser window will open - watch what happens!")
    print()

    # Create scraper with visible browser
    with GoogleAIModeScraper(headless=False) as scraper:
        result = scraper.scrape(
            query=query,
            language="en",
            region="US",
            wait_time=5,
            verbose=True,
            wait_for_user=True  # Will pause automatically if CAPTCHA detected
        )

        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)

        print(f"\nQuery: {result.query}")
        print(f"Language: {result.language}")
        print(f"Region: {result.region}")

        if result.ai_overview:
            print(f"\n📝 AI Overview Found:")
            print("-" * 60)
            print(result.ai_overview[:300] + "..." if len(result.ai_overview) > 300 else result.ai_overview)
        else:
            print("\n⚠️  No AI Overview found")

        print(f"\n🔍 Search Results: {len(result.results)} found")
        print("-" * 60)

        if result.results:
            for i, res in enumerate(result.results[:5], 1):
                print(f"\n{i}. {res.title}")
                print(f"   URL: {res.url}")
                if res.meta_description:
                    desc = res.meta_description[:100]
                    print(f"   Description: {desc}...")
                if res.ai_highlight:
                    print(f"   ✨ AI Highlight: {res.ai_highlight}")
        else:
            print("⚠️  No search results found")
            print("\nThis might mean:")
            print("1. The CSS selectors need updating")
            print("2. Google's page structure has changed")
            print("3. The page didn't load properly")

        # Save to file
        output_file = "debug_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'query': result.query,
                'language': result.language,
                'region': result.region,
                'ai_overview': result.ai_overview,
                'results': [
                    {
                        'url': r.url,
                        'title': r.title,
                        'meta_description': r.meta_description,
                        'ai_highlight': r.ai_highlight
                    }
                    for r in result.results
                ]
            }, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Results saved to: {output_file}")
        print()

if __name__ == '__main__':
    try:
        test_scraper()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
