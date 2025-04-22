"""
Tests for the custom crawler example.

This module tests the functionality of the ExampleCrawler class.
"""

import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from ..examples.custom_crawler import ExampleCrawler


class TestExampleCrawler(unittest.TestCase):
    """Test cases for the ExampleCrawler class."""
    
    def setUp(self):
        """Set up a fresh crawler for each test."""
        self.crawler = ExampleCrawler()
    
    def test_extract_data(self):
        """Test the extract_data method."""
        # Create a mock BeautifulSoup object
        html = """
        <html>
            <head>
                <title>Example Page</title>
            </head>
            <body>
                <h1>Example Title</h1>
                <main>
                    <p>This is the main content of the page.</p>
                </main>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract data
        data = self.crawler.extract_data(soup)
        
        # Check the extracted data
        self.assertEqual(data['title'], 'Example Title')
        self.assertEqual(data['content'], 'This is the main content of the page.')
    
    def test_extract_data_no_title(self):
        """Test the extract_data method when there is no title."""
        # Create a mock BeautifulSoup object without a title
        html = """
        <html>
            <head>
                <title>Example Page</title>
            </head>
            <body>
                <main>
                    <p>This is the main content of the page.</p>
                </main>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract data
        data = self.crawler.extract_data(soup)
        
        # Check the extracted data
        self.assertEqual(data['title'], 'No title found')
        self.assertEqual(data['content'], 'This is the main content of the page.')
    
    def test_extract_data_no_content(self):
        """Test the extract_data method when there is no content."""
        # Create a mock BeautifulSoup object without content
        html = """
        <html>
            <head>
                <title>Example Page</title>
            </head>
            <body>
                <h1>Example Title</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract data
        data = self.crawler.extract_data(soup)
        
        # Check the extracted data
        self.assertEqual(data['title'], 'Example Title')
        self.assertEqual(data['content'], 'No content found')
    
    @patch.object(ExampleCrawler, 'fetch_page')
    def test_crawl_success(self, mock_fetch_page):
        """Test the crawl method when the page is successfully fetched."""
        # Create a mock BeautifulSoup object
        html = """
        <html>
            <head>
                <title>Example Page</title>
            </head>
            <body>
                <h1>Example Title</h1>
                <main>
                    <p>This is the main content of the page.</p>
                </main>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Set up the mock fetch_page method
        mock_fetch_page.return_value = soup
        
        # Call the crawl method
        result = self.crawler.crawl("https://example.com")
        
        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['url'], "https://example.com")
        self.assertEqual(result[0]['title'], "Example Title")
        self.assertEqual(result[0]['content'], "This is the main content of the page.")
        self.assertIn('timestamp', result[0])
    
    @patch.object(ExampleCrawler, 'fetch_page')
    def test_crawl_failure(self, mock_fetch_page):
        """Test the crawl method when the page fetch fails."""
        # Set up the mock fetch_page method to return None
        mock_fetch_page.return_value = None
        
        # Call the crawl method
        result = self.crawler.crawl("https://example.com")
        
        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['url'], "https://example.com")
        self.assertEqual(result[0]['error'], "Failed to fetch page")
        self.assertIsNone(result[0]['content'])


if __name__ == '__main__':
    unittest.main() 