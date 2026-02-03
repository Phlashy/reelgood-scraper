#!/usr/bin/env python3
"""
Reelgood Streaming Availability Scraper
Extracts streaming platform and country availability from Reelgood URLs

Usage:
    python3 reelgood_scraper.py <reelgood_url>
    python3 reelgood_scraper.py <reelgood_url> --region us
    python3 reelgood_scraper.py <reelgood_url> --all-regions

Regions:
    all - All Regions
    au - Australia
    ca - Canada
    uk - United Kingdom
    nz - New Zealand
    us - United States

Requirements:
    pip install playwright
    playwright install chromium
"""

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import sys
import json
import os

# Create a stealth instance to avoid bot detection
stealth = Stealth()

# Available regions (order matches dropdown)
REGIONS = {
    'all': 'All Regions',
    'us': 'United States',
    'uk': 'United Kingdom',
    'ca': 'Canada',
    'au': 'Australia',
    'nz': 'New Zealand',
}

# Browser launch args for low-memory environments (Docker/Railway)
BROWSER_ARGS = [
    '--disable-dev-shm-usage',  # Overcome limited /dev/shm in Docker
    '--disable-gpu',  # Disable GPU acceleration
    '--no-sandbox',  # Required for Docker
    '--disable-setuid-sandbox',
    '--disable-extensions',  # No extensions needed
    '--disable-background-networking',
    '--disable-default-apps',
    '--disable-sync',
    '--disable-translate',
    '--mute-audio',
    '--hide-scrollbars',
    '--metrics-recording-only',
    '--no-first-run',
]


def get_current_region(page):
    """Get the currently selected region from the title-specific dropdown"""
    try:
        # The dropdown button shows the current region - look for the span inside
        # that contains just the country name (not the full dropdown menu)
        region_span = page.query_selector('div.e3nus5z7 span.e3nus5z6, div[class*="e3nus5z"] > span')
        if region_span:
            text = region_span.inner_text().strip()
            if text and text in ['Canada', 'United States', 'United Kingdom', 'Australia', 'New Zealand', 'All Regions']:
                return text

        # Fallback: look for the first line of the dropdown div
        dropdown = page.query_selector('div.e3nus5z7, div[class*="e3nus5z"]')
        if dropdown:
            text = dropdown.inner_text().strip().split('\n')[0]
            return text
    except:
        pass
    return "Unknown"


def select_region(page, target_region):
    """Select a specific region from the title-specific dropdown"""
    try:
        current = get_current_region(page)
        if current == target_region:
            return target_region

        # Find and click the region dropdown
        dropdown = page.query_selector('div.e3nus5z7, div[class*="e3nus5z"]')
        if not dropdown:
            print(f"Warning: Region dropdown not found")
            return current

        dropdown.click()
        page.wait_for_timeout(500)  # Wait for dropdown to open

        # Find the target region option and get its coordinates
        # Options are DIVs with class e3nus5z3
        menu_item = page.evaluate(f'''() => {{
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
            while (walker.nextNode()) {{
                const el = walker.currentNode;
                const text = el.textContent.trim();
                // Check if this element directly contains the country name
                const directText = Array.from(el.childNodes)
                    .filter(n => n.nodeType === Node.TEXT_NODE)
                    .map(n => n.textContent.trim())
                    .join('');

                if (directText === "{target_region}" || (text === "{target_region}" && el.children.length === 0)) {{
                    const rect = el.getBoundingClientRect();
                    if (rect.height > 0 && rect.width > 0 && rect.y > 0 && rect.y < 600) {{
                        return {{x: rect.x + rect.width/2, y: rect.y + rect.height/2}};
                    }}
                }}
            }}
            return null;
        }}''')

        if menu_item:
            page.mouse.click(menu_item['x'], menu_item['y'])
            page.wait_for_timeout(1200)  # Wait for content to update after region change
            return target_region

        # Close dropdown if we couldn't find the option
        page.keyboard.press('Escape')
        return current

    except Exception as e:
        try:
            page.keyboard.press('Escape')
        except:
            pass
        print(f"Warning: Could not select region '{target_region}': {e}")
        return get_current_region(page)


def extract_platforms(page):
    """Extract streaming platforms from the page (Free and Subscription only, no rent/buy)"""

    # First check if there are any service logos on the page at all
    logo_count = page.evaluate('() => document.querySelectorAll("img[src*=\\"service-logos\\"]").length')
    print(f"    Found {logo_count} service logos on page")

    # Use JavaScript to find platforms and their categories
    platforms_data = page.evaluate('''() => {
        const results = [];
        const imgs = document.querySelectorAll('img[src*="service-logos"]');

        for (const img of imgs) {
            const platform = img.alt;
            if (!platform) continue;

            // Walk up the DOM to find the category (Free, Sub, Rent, Buy)
            let el = img;
            let category = '';

            for (let i = 0; i < 15; i++) {
                el = el.parentElement;
                if (!el) break;

                // Look for category section headers
                const text = el.textContent || '';

                // Check if we've reached a section with a category label
                // Categories appear as section headers like "Free", "Sub", "Rent", "Buy"
                const firstChild = el.firstElementChild;
                if (firstChild) {
                    const headerText = firstChild.textContent.trim();
                    if (['Free', 'Sub', 'Rent', 'Buy'].includes(headerText)) {
                        category = headerText;
                        break;
                    }
                }

                // Also check for category in class names or data attributes
                if (el.className && typeof el.className === 'string') {
                    if (el.className.includes('free')) category = 'Free';
                    else if (el.className.includes('sub')) category = 'Sub';
                    else if (el.className.includes('rent')) category = 'Rent';
                    else if (el.className.includes('buy')) category = 'Buy';
                    if (category) break;
                }
            }

            // If still no category, try to infer from nearby text
            if (!category) {
                let sibling = img.parentElement;
                for (let i = 0; i < 5 && sibling; i++) {
                    const prev = sibling.previousElementSibling;
                    if (prev) {
                        const prevText = prev.textContent.trim();
                        if (['Free', 'Sub', 'Rent', 'Buy'].includes(prevText)) {
                            category = prevText;
                            break;
                        }
                    }
                    sibling = sibling.parentElement;
                }
            }

            results.push({platform: platform, category: category || 'Unknown'});
        }

        return results;
    }''')

    # Separate into subscription and free platforms
    subscription_platforms = set()
    free_platforms = set()

    for item in platforms_data:
        if item['category'] == 'Sub':
            subscription_platforms.add(item['platform'])
        elif item['category'] == 'Free':
            free_platforms.add(item['platform'])

    return {
        'subscription': sorted(list(subscription_platforms)),
        'free': sorted(list(free_platforms))
    }


def scrape_reelgood(url, region=None):
    """
    Scrape streaming availability from a Reelgood URL using Playwright.

    Args:
        url: Reelgood URL for a movie or TV show
        region: Optional region code (all, au, ca, uk, nz, us) or None for default

    Returns:
        dict: Contains title, platforms, region info, and availability details
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        # Apply stealth techniques to avoid bot detection
        stealth.apply_stealth_sync(page)

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_selector('h1', timeout=15000)
            page.wait_for_timeout(1500)  # Wait for page content to load

            # Scroll to Where to Watch section
            page.evaluate('''() => {
                const h2s = document.querySelectorAll('h2');
                for (const h of h2s) {
                    if (h.textContent.includes('Where to Watch')) {
                        h.scrollIntoView({block: 'start'});
                        break;
                    }
                }
            }''')
            page.wait_for_timeout(500)  # Wait for scroll

            # Select region if specified
            if region and region in REGIONS:
                target_region = REGIONS[region]
                select_region(page, target_region)

            detected_region = get_current_region(page)

            # Extract title
            title = "Unknown Title"
            try:
                title_elem = page.query_selector('h1')
                if title_elem:
                    title = title_elem.inner_text().strip()
            except:
                pass

            # Extract streaming platforms
            platforms = extract_platforms(page)

            browser.close()

            return {
                "title": title,
                "platforms": platforms,
                "region": detected_region,
                "url": url,
                "platform_count": len(platforms['subscription']) + len(platforms['free'])
            }

        except Exception as e:
            browser.close()
            return {"error": f"Failed to scrape URL: {str(e)}"}


def scrape_all_regions(url):
    """Scrape streaming availability for all regions"""
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        # Apply stealth techniques to avoid bot detection
        stealth.apply_stealth_sync(page)

        try:
            print(f"Loading URL: {url}")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_selector('h1', timeout=15000)
            page.wait_for_timeout(1500)  # Wait for page content to load

            # Check if we hit a Cloudflare challenge page
            page_title = page.title()
            print(f"Page title: {page_title}")
            if 'just a moment' in page_title.lower() or page_title.strip() == '':
                print("WARNING: Cloudflare challenge detected - page not loaded properly!")

            # Scroll to Where to Watch section
            page.evaluate('''() => {
                const h2s = document.querySelectorAll('h2');
                for (const h of h2s) {
                    if (h.textContent.includes('Where to Watch')) {
                        h.scrollIntoView({block: 'start'});
                        break;
                    }
                }
            }''')
            page.wait_for_timeout(500)  # Wait for scroll

            # Get title once
            title = "Unknown Title"
            try:
                title_elem = page.query_selector('h1')
                if title_elem:
                    title = title_elem.inner_text().strip()
            except:
                pass

            # Scrape each region (skip 'all' for individual region scraping)
            regions_to_scrape = {k: v for k, v in REGIONS.items() if k != 'all'}

            for region_code, region_name in regions_to_scrape.items():
                print(f"  Scraping {region_name}...")

                select_region(page, region_name)
                platforms = extract_platforms(page)

                results[region_code] = {
                    "region": region_name,
                    "platforms": platforms,
                    "platform_count": len(platforms['subscription']) + len(platforms['free'])
                }

            browser.close()

            return {
                "title": title,
                "url": url,
                "regions": results
            }

        except Exception as e:
            browser.close()
            return {"error": f"Failed to scrape URL: {str(e)}"}


def generate_summary(data, all_regions=False):
    """Generate a human-readable summary from scraped data"""
    if "error" in data:
        return f"Error: {data['error']}\n\nNote: Make sure you have internet connectivity and the URL is valid."

    summary = f"STREAMING AVAILABILITY SUMMARY\n"
    summary += f"{'=' * 60}\n\n"
    summary += f"Title: {data['title']}\n"

    if all_regions and 'regions' in data:
        summary += f"\n{'=' * 60}\n"

        for region_code, region_data in data['regions'].items():
            summary += f"\n{region_data['region']} ({region_data['platform_count']} platforms):\n"
            platforms = region_data['platforms']
            if platforms['subscription'] or platforms['free']:
                if platforms['subscription']:
                    summary += "  Subscription:\n"
                    for platform in platforms['subscription']:
                        summary += f"    - {platform}\n"
                if platforms['free']:
                    summary += "  Free:\n"
                    for platform in platforms['free']:
                        summary += f"    - {platform}\n"
            else:
                summary += "  (No streaming platforms available)\n"
    else:
        summary += f"Region: {data['region']}\n"
        summary += f"Platforms Found: {data['platform_count']}\n\n"

        platforms = data['platforms']
        if platforms['subscription'] or platforms['free']:
            summary += "Available on:\n"
            if platforms['subscription']:
                summary += "  Subscription:\n"
                for platform in platforms['subscription']:
                    summary += f"    - {platform}\n"
            if platforms['free']:
                summary += "  Free:\n"
                for platform in platforms['free']:
                    summary += f"    - {platform}\n"
        else:
            summary += "No streaming platforms detected.\n"

    summary += f"\n{'=' * 60}\n"
    summary += f"Source: {data['url']}\n"

    return summary


def print_help():
    """Print usage help"""
    print("""
Reelgood Streaming Availability Scraper

Usage:
    python3 reelgood_scraper.py <url>                    # Use detected region
    python3 reelgood_scraper.py <url> --region <code>   # Specific region
    python3 reelgood_scraper.py <url> --all-regions     # All regions

Region codes:
    all - All Regions (combined view)
    au  - Australia
    ca  - Canada
    uk  - United Kingdom
    nz  - New Zealand
    us  - United States

Options:
    --debug, -d      Show raw JSON data
    --json           Output only JSON (no summary)
    --help, -h       Show this help message

Examples:
    python3 reelgood_scraper.py https://reelgood.com/movie/inception-2010
    python3 reelgood_scraper.py https://reelgood.com/movie/inception-2010 --region us
    python3 reelgood_scraper.py https://reelgood.com/movie/inception-2010 --all-regions
""")


if __name__ == "__main__":
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        sys.exit(0)

    test_url = sys.argv[1]

    # Parse arguments
    all_regions = '--all-regions' in sys.argv or '--all' in sys.argv
    json_only = '--json' in sys.argv
    debug = '--debug' in sys.argv or '-d' in sys.argv

    region = None
    if '--region' in sys.argv:
        idx = sys.argv.index('--region')
        if idx + 1 < len(sys.argv):
            region = sys.argv[idx + 1].lower()
            if region not in REGIONS:
                print(f"Error: Unknown region '{region}'")
                print(f"Valid regions: {', '.join(REGIONS.keys())}")
                sys.exit(1)

    if not json_only:
        print(f"Scraping: {test_url}\n")

    if all_regions:
        data = scrape_all_regions(test_url)
    else:
        data = scrape_reelgood(test_url, region=region)

    if json_only:
        print(json.dumps(data, indent=2))
    else:
        summary = generate_summary(data, all_regions=all_regions)
        print(summary)

        if debug:
            print("\nRaw data (debug mode):")
            print(json.dumps(data, indent=2))
