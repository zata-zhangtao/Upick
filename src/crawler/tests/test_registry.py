"""
Tests for the crawler registry and crawler selection.

This module tests the functionality of the CrawlerRegistry class and
the crawler selection mechanism.
"""

import unittest
from unittest.mock import MagicMock, patch
from ..registry import CrawlerRegistry
from ..base import BaseCrawler


class MockCrawler(BaseCrawler):
    """Mock crawler for testing."""
    
    def crawl(self, url):
        return [{"url": url, "content": "Mock content"}]


class AnotherMockCrawler(BaseCrawler):
    """Another mock crawler for testing."""
    
    def crawl(self, url):
        return [{"url": url, "content": "Another mock content"}]


class TestCrawlerRegistry(unittest.TestCase):
    """Test cases for the CrawlerRegistry class."""
    
    def setUp(self):
        """Set up a fresh registry for each test."""
        self.registry = CrawlerRegistry()
    
    def test_register_and_get_crawler(self):
        """Test registering a crawler and retrieving it."""
        # Register a crawler
        self.registry.register(r"https?://example\.com/.*", MockCrawler)
        
        # Get the crawler for a matching URL
        crawler_class = self.registry.get_crawler("https://example.com/page")
        self.assertEqual(crawler_class, MockCrawler)
        
        # Get the crawler for a non-matching URL
        crawler_class = self.registry.get_crawler("https://other.com/page")
        self.assertIsNone(crawler_class)
    
    def test_multiple_crawlers(self):
        """Test registering multiple crawlers and retrieving them."""
        # Register multiple crawlers
        self.registry.register(r"https?://example\.com/.*", MockCrawler)
        self.registry.register(r"https?://another\.com/.*", AnotherMockCrawler)
        
        # Get the crawler for a matching URL
        crawler_class = self.registry.get_crawler("https://example.com/page")
        self.assertEqual(crawler_class, MockCrawler)
        
        # Get the crawler for another matching URL
        crawler_class = self.registry.get_crawler("https://another.com/page")
        self.assertEqual(crawler_class, AnotherMockCrawler)
        
        # Get the crawler for a non-matching URL
        crawler_class = self.registry.get_crawler("https://other.com/page")
        self.assertIsNone(crawler_class)
    
    def test_get_all_crawlers(self):
        """Test getting all registered crawlers."""
        # Register multiple crawlers
        self.registry.register(r"https?://example\.com/.*", MockCrawler)
        self.registry.register(r"https?://another\.com/.*", AnotherMockCrawler)
        
        # Get all crawlers
        all_crawlers = self.registry.get_all_crawlers()
        
        # Check that all crawlers are returned
        self.assertEqual(len(all_crawlers), 2)
        self.assertEqual(all_crawlers[r"https?://example\.com/.*"], MockCrawler)
        self.assertEqual(all_crawlers[r"https?://another\.com/.*"], AnotherMockCrawler)


class TestCrawlerSelection(unittest.TestCase):
    """Test cases for the crawler selection mechanism."""
    
    @patch('src.crawler.registry.registry')
    def test_crawler_selection(self, mock_registry):
        """Test that the WebCrawler selects the appropriate crawler."""
        from ..web import WebCrawler
        
        # Set up the mock registry
        mock_registry.get_crawler.return_value = MockCrawler
        
        # Create a WebCrawler instance
        web_crawler = WebCrawler()
        
        # Call the crawl method
        with patch.object(MockCrawler, 'crawl') as mock_crawl:
            mock_crawl.return_value = [{"url": "https://example.com", "content": "Mock content"}]
            
            # Call the crawl method
            result = web_crawler.crawl("https://example.com")
            
            # Check that the registry was queried
            mock_registry.get_crawler.assert_called_once_with("https://example.com")
            
            # Check that the mock crawler was used
            mock_crawl.assert_called_once_with("https://example.com")
            
            # Check the result
            self.assertEqual(result, [{"url": "https://example.com", "content": "Mock content"}])
    
    @patch('src.crawler.registry.registry')
    def test_fallback_to_web_crawler(self, mock_registry):
        """Test that the WebCrawler falls back to itself if no specialized crawler is found."""
        from ..web import WebCrawler
        
        # Set up the mock registry to return None
        mock_registry.get_crawler.return_value = None
        
        # Create a WebCrawler instance
        web_crawler = WebCrawler()
        
        # Call the crawl method
        with patch.object(WebCrawler, 'fetch_structured_content') as mock_fetch:
            mock_fetch.return_value = {"url": "https://example.com", "content": "Web crawler content"}
            
            # Call the crawl method
            result = web_crawler.crawl("https://example.com")
            
            # Check that the registry was queried
            mock_registry.get_crawler.assert_called_once_with("https://example.com")
            
            # Check that fetch_structured_content was called
            mock_fetch.assert_called_once_with("https://example.com")
            
            # Check the result
            self.assertEqual(result, [{"url": "https://example.com", "content": "Web crawler content"}])


if __name__ == '__main__':
    unittest.main() 