#!/usr/bin/env python3
"""
Batch Reelgood Scraper
Process multiple Reelgood URLs from a file or command line

Usage:
    python3 batch_scraper.py url1 url2 url3
    python3 batch_scraper.py --file urls.txt
"""

import sys
import time
from reelgood_scraper import scrape_reelgood, generate_summary

def process_urls(urls, delay=2):
    """
    Process multiple URLs with delay between requests
    
    Args:
        urls: List of Reelgood URLs
        delay: Seconds to wait between requests (be respectful!)
    """
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"Processing {i}/{len(urls)}: {url}")
        print('='*60)
        
        data = scrape_reelgood(url)
        summary = generate_summary(data)
        print(summary)
        
        results.append(data)
        
        # Be respectful - wait between requests
        if i < len(urls):
            print(f"\n⏳ Waiting {delay} seconds before next request...")
            time.sleep(delay)
    
    return results

def read_urls_from_file(filename):
    """Read URLs from a text file (one per line)"""
    try:
        with open(filename, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return urls
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Batch Reelgood Scraper")
        print("\nUsage:")
        print("  python3 batch_scraper.py url1 url2 url3")
        print("  python3 batch_scraper.py --file urls.txt")
        print("\nExample:")
        print("  python3 batch_scraper.py \\")
        print("    https://reelgood.com/movie/inception-2010 \\")
        print("    https://reelgood.com/show/breaking-bad-2008")
        sys.exit(1)
    
    urls = []
    
    # Check if reading from file
    if sys.argv[1] in ['--file', '-f']:
        if len(sys.argv) < 3:
            print("❌ Error: Please specify a filename")
            print("Usage: python3 batch_scraper.py --file urls.txt")
            sys.exit(1)
        urls = read_urls_from_file(sys.argv[2])
        print(f"📄 Loaded {len(urls)} URLs from {sys.argv[2]}")
    else:
        # URLs provided as command line arguments
        urls = sys.argv[1:]
    
    if not urls:
        print("❌ Error: No URLs to process")
        sys.exit(1)
    
    print(f"\n🚀 Starting batch processing of {len(urls)} URL(s)...")
    results = process_urls(urls)
    
    print(f"\n{'='*60}")
    print(f"✅ Completed! Processed {len(results)} URL(s)")
    print('='*60)
