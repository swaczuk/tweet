#!/usr/bin/env python3
"""
Simple test to show JSON output structure
"""

from google_ai_scraper import GoogleAIModeScraper
import json

def show_json_structure():
    """Test and display JSON structure"""
    print("=" * 60)
    print("JSON Output Structure Test")
    print("=" * 60)
    print()

    query = input("Enter search query (or press Enter for default): ").strip()
    if not query:
        query = "artificial intelligence"

    print(f"\n🔍 Searching: {query}")
    print("Browser will open - solve CAPTCHA if needed\n")

    with GoogleAIModeScraper(headless=False) as scraper:
        result = scraper.scrape(
            query=query,
            language="en",
            region="US",
            wait_time=5,
            verbose=True,
            wait_for_user=True
        )

        # Convert to the JSON structure
        json_data = {
            "query": result.query,
            "language": result.language,
            "region": result.region,
            "ai_overview": result.ai_overview,
            "total_results": len(result.results),
            "results": []
        }

        # Add each result separately
        for res in result.results:
            json_data["results"].append({
                "url": res.url,
                "title": res.title,
                "meta_description": res.meta_description,
                "highlighted_text": res.ai_highlight
            })

        # Save to file
        output_file = "json_output_example.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 60)
        print("JSON OUTPUT")
        print("=" * 60)

        # Show pretty-printed JSON
        print(json.dumps(json_data, indent=2, ensure_ascii=False))

        print("\n" + "=" * 60)
        print(f"✅ Saved to: {output_file}")
        print("=" * 60)

        # Show structure summary
        print("\n📊 STRUCTURE SUMMARY:")
        print(f"   - Query: {json_data['query']}")
        print(f"   - Total Results: {json_data['total_results']}")
        print(f"   - AI Overview: {'Yes' if json_data['ai_overview'] else 'No'}")
        print()

        print("📄 Each result contains:")
        print("   - url: The webpage URL")
        print("   - title: The page title")
        print("   - meta_description: Full description/snippet")
        print("   - highlighted_text: Text that Google emphasized")
        print()

        if json_data["results"]:
            print("📝 Example first result:")
            first = json_data["results"][0]
            print(f"   URL: {first['url']}")
            print(f"   Title: {first['title'][:60]}...")
            print(f"   Description: {first['meta_description'][:100] if first['meta_description'] else 'N/A'}...")
            print(f"   Highlights: {first['highlighted_text'][:100] if first['highlighted_text'] else 'N/A'}...")

if __name__ == '__main__':
    try:
        show_json_structure()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
