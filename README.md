# Reelgood Streaming Availability Scraper

A Python tool that extracts streaming platform and country availability information from Reelgood.com URLs.

## Features

- Extracts movie/TV show title
- Identifies available streaming platforms
- Shows region/country availability
- Clean, readable text summary output
- Handles errors gracefully

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

### Install Dependencies

```bash
pip install requests beautifulsoup4
```

Or if you're on a system that requires the `--break-system-packages` flag:

```bash
pip install requests beautifulsoup4 --break-system-packages
```

## Usage

### Basic Usage

```bash
python3 reelgood_scraper.py <reelgood_url>
```

### Examples

**Scrape a movie:**
```bash
python3 reelgood_scraper.py https://reelgood.com/movie/inception-2010
```

**Scrape a TV show:**
```bash
python3 reelgood_scraper.py https://reelgood.com/show/breaking-bad-2008
```

**Run with debug mode to see raw data:**
```bash
python3 reelgood_scraper.py https://reelgood.com/movie/the-matrix-1999 --debug
```

### Sample Output

```
📺 STREAMING AVAILABILITY SUMMARY
============================================================

Title: Inception (2010)
Region: United States
Platforms Found: 3

Available on:
  ✓ Netflix
  ✓ Prime Video
  ✓ HBO Max

============================================================
Source: https://reelgood.com/movie/inception-2010
```

## How It Works

1. **Fetches the Reelgood page** using the provided URL
2. **Parses the HTML** to extract:
   - Title from page headers and metadata
   - Streaming platforms from service buttons, images, and structured data
   - Region/country information from metadata and page elements
3. **Generates a summary** in an easy-to-read format

## Limitations

- Reelgood may update their website structure, which could require updates to the scraper
- Some content may require specific regional settings
- Rate limiting: Be respectful and don't hammer the site with too many requests
- This tool is for personal use only - respect Reelgood's terms of service

## Troubleshooting

**No platforms detected:**
- The content might not be available for streaming
- Reelgood's page structure may have changed
- Try a different URL or check the debug output

**Connection errors:**
- Check your internet connection
- Verify the URL is correct and accessible
- Reelgood might be temporarily down

**Import errors:**
- Make sure you've installed the required packages: `pip install requests beautifulsoup4`

## Tips

- Always use the full Reelgood URL (including `https://`)
- The tool defaults to US region data if no region is specified
- Use debug mode (`--debug`) to see the raw extracted data

## Legal Notice

This tool is for personal, educational use only. Please respect Reelgood's terms of service and don't use this for commercial purposes or excessive scraping.
