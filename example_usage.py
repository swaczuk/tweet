#!/usr/bin/env python3
"""
Example usage of Google AI Mode Scraper

This script demonstrates different ways to use the scraper.
"""

from google_ai_scraper import GoogleAIModeScraper, save_results


def example_single_query():
    """Example: Scrape a single query"""
    print("=" * 60)
    print("Example 1: Single Query Scraping")
    print("=" * 60)

    with GoogleAIModeScraper(headless=True) as scraper:
        result = scraper.scrape(
            query="best programming languages 2024",
            language="en",
            region="US"
        )

        print(f"\nQuery: {result.query}")
        print(f"Language: {result.language} | Region: {result.region}\n")

        if result.ai_overview:
            print(f"AI Overview:\n{result.ai_overview}\n")
            print("-" * 60)

        print(f"\nFound {len(result.results)} results:\n")

        for i, res in enumerate(result.results[:5], 1):  # Show first 5
            print(f"{i}. {res.title}")
            print(f"   URL: {res.url}")
            if res.meta_description:
                desc = res.meta_description[:100]
                print(f"   Description: {desc}...")
            if res.ai_highlight:
                print(f"   AI Highlight: {res.ai_highlight}")
            print()


def example_multiple_languages():
    """Example: Scrape the same query in different languages"""
    print("\n" + "=" * 60)
    print("Example 2: Multi-language Scraping")
    print("=" * 60)

    query = "climate change"

    languages = [
        ("en", "US", "English"),
        ("es", "ES", "Spanish"),
        ("fr", "FR", "French"),
    ]

    with GoogleAIModeScraper(headless=True) as scraper:
        for lang, region, name in languages:
            print(f"\n{name} ({lang}-{region}):")
            print("-" * 40)

            result = scraper.scrape(
                query=query,
                language=lang,
                region=region
            )

            if result.ai_overview:
                overview = result.ai_overview[:150]
                print(f"AI Overview: {overview}...")

            print(f"Results found: {len(result.results)}")

            # Delay between requests
            import time
            time.sleep(2)


def example_batch_scraping():
    """Example: Scrape multiple queries at once"""
    print("\n" + "=" * 60)
    print("Example 3: Batch Scraping")
    print("=" * 60)

    queries = [
        "machine learning basics",
        "python web scraping",
        "data science tools",
    ]

    with GoogleAIModeScraper(headless=True) as scraper:
        results = scraper.scrape_batch(queries, language="en", region="US")

        for result in results:
            print(f"\nQuery: {result.query}")
            print(f"Results: {len(result.results)}")
            if result.ai_overview:
                overview = result.ai_overview[:100]
                print(f"AI Overview: {overview}...")
            print("-" * 40)


def example_save_to_json():
    """Example: Save results to JSON file"""
    print("\n" + "=" * 60)
    print("Example 4: Save to JSON")
    print("=" * 60)

    with GoogleAIModeScraper(headless=True) as scraper:
        result = scraper.scrape(
            query="artificial intelligence trends",
            language="en",
            region="US"
        )

        output_file = "example_output.json"
        save_results(result, output_file)
        print(f"\nResults saved to: {output_file}")


def example_custom_wait_time():
    """Example: Use custom wait time for slow connections"""
    print("\n" + "=" * 60)
    print("Example 5: Custom Wait Time")
    print("=" * 60)

    with GoogleAIModeScraper(headless=True) as scraper:
        result = scraper.scrape(
            query="deep learning frameworks",
            language="en",
            region="US",
            wait_time=10  # Wait 10 seconds for page load
        )

        print(f"Query: {result.query}")
        print(f"Results found: {len(result.results)}")


if __name__ == "__main__":
    print("\nGoogle AI Mode Scraper - Usage Examples")
    print("========================================\n")

    # Run examples
    # Uncomment the examples you want to run

    # Example 1: Single query
    example_single_query()

    # Example 2: Multiple languages
    # example_multiple_languages()

    # Example 3: Batch scraping
    # example_batch_scraping()

    # Example 4: Save to JSON
    # example_save_to_json()

    # Example 5: Custom wait time
    # example_custom_wait_time()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
