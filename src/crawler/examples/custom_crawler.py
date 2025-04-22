"""
Example of a custom crawler plugin.

This file demonstrates how to create a custom crawler plugin for a specific website.
"""

from typing import Dict, Any, List
import re
from ..base import BaseCrawler
from ..registry import registry


class ExampleCrawler(BaseCrawler):
    """
    Example crawler for a specific website.
    
    This crawler demonstrates how to create a custom crawler plugin
    for a specific website.
    """
    
    def __init__(self, user_agent: str = None):
        """Initialize the crawler with custom headers."""
        super().__init__(user_agent)
        # Add any custom headers or configuration here
    
    def extract_data(self, soup):
        """
        Extract specific data from the webpage.
        
        Args:
            soup: BeautifulSoup object containing the parsed HTML
            
        Returns:
            Dictionary containing the extracted data
        """
        # Example: Extract title and main content
        title = soup.find('h1')
        title_text = title.get_text().strip() if title else "No title found"
        
        # Example: Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|article|post'))
        content_text = main_content.get_text().strip() if main_content else "No content found"
        
        return {
            "title": title_text,
            "content": content_text
        }
    
    def crawl(self, url: str) -> List[Dict[str, Any]]:
        """
        Crawl the specified URL and extract data.
        
        Args:
            url: URL to crawl
            
        Returns:
            List of dictionaries containing the extracted data
        """
        soup = self.fetch_page(url)
        if not soup:
            return [{"url": url, "error": "Failed to fetch page", "content": None}]
        
        # Extract data using the specialized extractor
        data = self.extract_data(soup)
        
        # Add metadata
        data["url"] = url
        data["timestamp"] = self.get_current_timestamp()
        
        return [data]


# Example of how to register the custom crawler
# This would typically be done in the application's initialization code
# registry.register(r'https?://example\.com/.*', ExampleCrawler) 