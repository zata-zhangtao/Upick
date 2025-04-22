"""
Test runner script for the crawler module.

This script runs all the tests for the crawler module.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import the crawler module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the test modules
from src.crawler.tests.test_registry import TestCrawlerRegistry, TestCrawlerSelection
from src.crawler.tests.test_custom_crawler import TestExampleCrawler

# Create a test suite
suite = unittest.TestSuite()

# Add the test cases to the suite
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCrawlerRegistry))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCrawlerSelection))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestExampleCrawler))

# Run the tests
if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with a non-zero code if there were failures
    sys.exit(not result.wasSuccessful()) 