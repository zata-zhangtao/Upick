from flask import Blueprint, request, jsonify
import sys
import os

# Add the parent directory to sys.path to import from data_processing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_processing.web_crawler import fetch_and_clean_content

crawler_api = Blueprint('crawler_api', __name__)

@crawler_api.route('/api/crawler', methods=['POST'])
def crawl_website():
    """API endpoint to crawl a website and return the cleaned content"""
    data = request.json
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url']
    
    try:
        # Call the fetch_and_clean_content function from web_crawler.py
        content = fetch_and_clean_content(url)
        
        if content is False:
            return jsonify({'error': 'Failed to fetch content from the URL'}), 500
        
        return jsonify({'content': content})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500