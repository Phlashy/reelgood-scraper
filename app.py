#!/usr/bin/env python3
"""
Reelgood Streaming Availability Web App
Flask backend that serves the scraper functionality via a web interface
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from reelgood_scraper import scrape_all_regions, search_reelgood, REGIONS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    """API endpoint to scrape a Reelgood URL"""
    data = request.get_json()
    url = data.get('url', '').strip()

    # Validate URL
    if not url:
        return jsonify({'error': 'Please enter a URL'}), 400

    if 'reelgood.com' not in url:
        return jsonify({'error': 'Please enter a valid Reelgood URL'}), 400

    try:
        logger.info(f"Starting scrape for URL: {url}")

        # Scrape all regions
        result = scrape_all_regions(url)

        logger.info(f"Scrape completed for: {url}")

        if 'error' in result:
            logger.error(f"Scrape error: {result['error']}")
            return jsonify({'error': result['error']}), 500

        # Format the response
        response = {
            'title': result['title'],
            'url': result['url'],
            'regions': []
        }

        for region_code, region_data in result['regions'].items():
            response['regions'].append({
                'code': region_code,
                'name': region_data['region'],
                'subscription': region_data['platforms']['subscription'],
                'free': region_data['platforms']['free'],
                'platform_count': region_data['platform_count']
            })

        return jsonify(response)

    except Exception as e:
        logger.exception(f"Scraping failed with exception: {str(e)}")
        return jsonify({'error': f'Scraping failed: {str(e)}'}), 500


@app.route('/search', methods=['POST'])
def search():
    """API endpoint to search for movies/shows on Reelgood"""
    data = request.get_json()
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'error': 'Please enter a search query'}), 400

    if len(query) < 2:
        return jsonify({'error': 'Search query must be at least 2 characters'}), 400

    try:
        logger.info(f"Searching for: {query}")
        result = search_reelgood(query)

        if 'error' in result:
            logger.error(f"Search error: {result['error']}")
            return jsonify({'error': result['error']}), 500

        logger.info(f"Search completed, found {result['count']} results")
        return jsonify(result)

    except Exception as e:
        logger.exception(f"Search failed with exception: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
