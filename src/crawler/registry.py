"""
Crawler Registry Module

This module provides a registry system for managing different crawler plugins
based on URL patterns.
"""

import re
from typing import Dict, Type, Optional, List, Tuple
from .base import BaseCrawler


class CrawlerRegistry:
    """
    Registry for managing different crawler plugins based on URL patterns.
    
    This class allows registering crawler classes with URL patterns and
    retrieving the appropriate crawler for a given URL.
    """
    
    def __init__(self):
        """Initialize an empty registry."""
        self._crawlers: List[Tuple[re.Pattern, Type[BaseCrawler]]] = []
    
    def register(self, pattern: str, crawler_class: Type[BaseCrawler]) -> None:
        """
        Register a crawler class with a URL pattern.
        
        Args:
            pattern: Regular expression pattern to match URLs
            crawler_class: The crawler class to use for matching URLs
        """
        regex = re.compile(pattern)
        self._crawlers.append((regex, crawler_class))
    
    def get_crawler(self, url: str) -> Optional[Type[BaseCrawler]]:
        """
        Get the appropriate crawler class for a given URL.
        
        Args:
            url: The URL to find a crawler for
            
        Returns:
            The crawler class or None if no matching crawler is found
        """
        for pattern, crawler_class in self._crawlers:
            if pattern.match(url):
                return crawler_class
        return None
    
    def get_all_crawlers(self) -> Dict[str, Type[BaseCrawler]]:
        """
        Get all registered crawlers with their patterns.
        
        Returns:
            Dictionary mapping pattern strings to crawler classes
        """
        return {pattern.pattern: crawler_class for pattern, crawler_class in self._crawlers}


# Global registry instance
registry = CrawlerRegistry() 