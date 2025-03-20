# UPick Crawler Module

A flexible and extensible web crawling module for extracting content from various websites.

## Features

- Modular architecture for easy extension to new websites
- Base crawler class with common functionality
- Specialized crawlers for different sources (currently supports arXiv and IEEE)
- General-purpose WebCrawler for extracting clean text from any website
- Command-line interface for easy use
- Utility functions for common tasks
- Type annotations for better code reliability

## Usage

### As a Command-Line Tool

```bash
# Crawl arXiv papers (default)
python -m src.crawler.cli

# Crawl IEEE papers
python -m src.crawler.cli --source ieee

# Specify a custom URL
python -m src.crawler.cli --source arxiv --url "https://arxiv.org/list/cs.CL/recent"

# Specify output file
python -m src.crawler.cli --output my_papers.json
```

### As a Python Module

```python
from src.crawler import ArxivCrawler, IEEECrawler, WebCrawler

# Crawl arXiv papers
arxiv_crawler = ArxivCrawler()
papers = arxiv_crawler.crawl()
arxiv_crawler.save_to_file(papers, "arxiv_papers.json")

# Crawl IEEE papers
ieee_crawler = IEEECrawler()
papers = ieee_crawler.crawl("https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=machine%20learning")
ieee_crawler.save_to_file(papers, "ieee_papers.json")

# Extract general text content from any website
web_crawler = WebCrawler()
content = web_crawler.fetch_and_clean_content("https://example.com/article")
print(content)
```

## General Text Extraction

The `WebCrawler` class provides functionality to extract clean text content from any website:

```python
from src.crawler import WebCrawler

crawler = WebCrawler()
text = crawler.fetch_and_clean_content("https://example.com/article")
print(text)
```

The WebCrawler:
- Automatically detects page encoding
- Removes scripts, styles and other non-content elements
- Extracts clean readable text content
- Handles errors gracefully

## Extending for New Websites

To add support for a new website:

1. Create a new Python file in the `src/crawler` directory (e.g., `springer.py`)
2. Define a new crawler class that inherits from `BaseCrawler`
3. Implement the `crawl` method and any additional methods needed
4. Update `__init__.py` to import and expose the new crawler
5. Add the new crawler to the `get_crawler` function in `cli.py`

Example:

```python
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from .base import BaseCrawler

class SpringerCrawler(BaseCrawler):
    def __init__(self, default_url: str = "https://link.springer.com/search?query=artificial+intelligence"):
        super().__init__()
        self.default_url = default_url
    
    def crawl(self, url: Optional[str] = None) -> List[Dict[str, Any]]:
        # Implementation goes here
        pass
```

## Requirements

- Python 3.7+
- requests
- beautifulsoup4 