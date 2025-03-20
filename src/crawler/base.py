"""
Base crawler class that defines the common interface for all crawlers.
"""

import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json
from bs4 import BeautifulSoup


class BaseCrawler(ABC):
    """
    Abstract base class for all crawlers.
    
    Defines the common interface and utility methods that all specialized
    crawlers should implement or can use.
    """
    
    def __init__(self, user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"):
        """
        Initialize the crawler with basic configuration.
        
        Args:
            user_agent: User agent string for HTTP requests
        """
        self.headers = {"User-Agent": user_agent}
        
    def fetch_page(self, url: str, timeout: int = 20) -> Optional[BeautifulSoup]:
        """
        Fetch a web page and return its parsed content.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            BeautifulSoup object or None if request failed
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"Error fetching page {url}: {e}")
            return None
    
    @abstractmethod
    def crawl(self, url: str) -> List[Dict[str, Any]]:
        """
        Crawl the specified URL and extract data.
        
        Args:
            url: URL to crawl
            
        Returns:
            List of dictionaries containing the extracted data
        """
        pass
    
    def save_to_file(self, data: List[Dict[str, Any]], filename: str) -> None:
        """
        Save the crawled data to a JSON file.
        
        Args:
            data: Data to save
            filename: Output filename
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}") 