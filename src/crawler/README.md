# UPick Crawler

A flexible web crawling framework for extracting content from various websites.

## Features

- General-purpose web crawler for any website
- Specialized crawlers for specific websites (arXiv, IEEE, etc.)
- Plugin-based architecture for easy extension
- Clean text extraction from HTML content
- Configurable user agents and request headers
- Retry mechanism for handling transient failures

## Usage

### Basic Usage

```python
from upick.crawler import WebCrawler

# Create a crawler instance
crawler = WebCrawler()

# Crawl a URL
results = crawler.crawl("https://example.com")

# Process the results
for result in results:
    print(f"Title: {result.get('title', 'No title')}")
    print(f"Content: {result.get('content', 'No content')[:100]}...")
```

### Using Specialized Crawlers

The crawler automatically selects the appropriate specialized crawler based on the URL:

```python
from upick.crawler import WebCrawler

# The crawler will automatically use ArxivCrawler for arXiv URLs
results = WebCrawler().crawl("https://arxiv.org/abs/2101.12345")

# The crawler will automatically use IEEECrawler for IEEE URLs
results = WebCrawler().crawl("https://ieee.org/example")
```

## Creating Custom Crawlers

You can create custom crawlers for specific websites by extending the `BaseCrawler` class:

```python
from upick.crawler import BaseCrawler, registry
from typing import Dict, Any, List

class MyCustomCrawler(BaseCrawler):
    def crawl(self, url: str) -> List[Dict[str, Any]]:
        # Implement your custom crawling logic here
        soup = self.fetch_page(url)
        if not soup:
            return [{"url": url, "error": "Failed to fetch page", "content": None}]
        
        # Extract data using your custom logic
        data = {
            "url": url,
            "title": soup.find("h1").get_text().strip(),
            "content": soup.find("article").get_text().strip(),
            "timestamp": self.get_current_timestamp()
        }
        
        return [data]

# Register your custom crawler
registry.register(r"https?://example\.com/.*", MyCustomCrawler)
```

See `examples/custom_crawler.py` for a complete example.

## Plugin System

The crawler uses a plugin-based architecture that allows you to register custom crawlers for specific URL patterns. The system works as follows:

1. When a URL is crawled, the system checks if there's a specialized crawler registered for that URL pattern.
2. If a specialized crawler is found, it's used to crawl the URL.
3. If no specialized crawler is found, the general-purpose `WebCrawler` is used.

### Registering Custom Crawlers

To register a custom crawler, use the `registry` object:

```python
from upick.crawler import registry, BaseCrawler

class MyCustomCrawler(BaseCrawler):
    # Implement your custom crawler here
    pass

# Register the crawler with a URL pattern
registry.register(r"https?://example\.com/.*", MyCustomCrawler)
```

### URL Patterns

URL patterns are regular expressions that match URLs. The first matching pattern is used, so order matters. More specific patterns should be registered first.

## Testing

The crawler module includes a comprehensive test suite to ensure that all components work correctly. The tests cover:

- The crawler registry and crawler selection mechanism
- The custom crawler example
- The WebCrawler class

### Running Tests

To run the tests, use the following command:

```bash
python -m src.crawler.tests.run_tests
```

This will run all the tests and display the results.

### Writing Tests

When adding new features or fixing bugs, please add tests to ensure that the changes work correctly. The tests are organized as follows:

- `test_registry.py`: Tests for the CrawlerRegistry class and crawler selection
- `test_custom_crawler.py`: Tests for the ExampleCrawler class
- `run_tests.py`: Script to run all the tests

## Built-in Crawlers

- `WebCrawler`: General-purpose crawler for any website
- `ArxivCrawler`: Specialized crawler for arXiv.org
- `IEEECrawler`: Specialized crawler for IEEE.org

## License

This project is licensed under the MIT License - see the LICENSE file for details. 