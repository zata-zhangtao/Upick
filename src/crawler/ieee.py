"""
Crawler implementation for IEEE Xplore Digital Library.
"""

from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from .base import BaseCrawler


class IEEECrawler(BaseCrawler):
    """
    Specialized crawler for extracting papers from IEEE Xplore.
    """
    
    def __init__(self, default_url: str = "https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=artificial%20intelligence&highlight=true&returnFacets=ALL"):
        """
        Initialize the IEEE crawler with default URL.
        
        Args:
            default_url: Default URL for the IEEE search results page
        """
        super().__init__()
        self.default_url = default_url
        # IEEE might need additional headers for proper crawling
        self.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://ieeexplore.ieee.org/"
        })
    
    def crawl(self, url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Crawl IEEE papers from the specified URL.
        
        Args:
            url: URL to crawl, uses default_url if not provided
            
        Returns:
            List of dictionaries containing paper information
        """
        target_url = url or self.default_url
        print(f"Starting crawl from: {target_url}")
        
        soup = self.fetch_page(target_url)
        if not soup:
            return []
        
        return self._extract_papers(soup)
    
    def _extract_papers(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Extract paper information from the parsed HTML.
        
        Args:
            soup: BeautifulSoup object containing the parsed HTML
            
        Returns:
            List of dictionaries containing paper information
        """
        papers = []
        
        # Find all paper entries
        paper_containers = soup.find_all("div", class_="List-results-items")
        
        for container in paper_containers:
            paper = {}
            
            # Extract title
            title_element = container.find("h3", class_="result-item-title")
            if title_element and title_element.find("a"):
                title_link = title_element.find("a")
                paper["title"] = title_link.get_text(strip=True)
                paper["url"] = "https://ieeexplore.ieee.org" + title_link["href"] if title_link.has_attr("href") else None
            
            # Extract authors
            authors_element = container.find("p", class_="author")
            if authors_element:
                authors_text = authors_element.get_text(strip=True)
                paper["authors"] = [author.strip() for author in authors_text.split(";")]
            
            # Extract publication info
            pub_element = container.find("div", class_="description")
            if pub_element:
                paper["publication"] = pub_element.get_text(strip=True)
            
            # Extract abstract
            abstract_element = container.find("div", class_="abstract-text")
            if abstract_element:
                paper["abstract"] = abstract_element.get_text(strip=True)
            
            # Extract DOI if available
            doi_element = container.find("a", class_="doi-link")
            if doi_element:
                paper["doi"] = doi_element.get_text(strip=True)
            
            if paper and "title" in paper:
                papers.append(paper)
        
        return papers
    
    def get_paper_details(self, url: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific paper.
        
        Args:
            url: URL of the paper detail page
            
        Returns:
            Dictionary containing detailed paper information
        """
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        details = {}
        
        # Extract title
        title_element = soup.find("h1", class_="document-title")
        if title_element:
            details["title"] = title_element.get_text(strip=True)
        
        # Extract authors
        authors_section = soup.find("div", class_="authors-info-container")
        if authors_section:
            author_elements = authors_section.find_all("span", class_="author")
            details["authors"] = [author.get_text(strip=True) for author in author_elements]
        
        # Extract abstract
        abstract_element = soup.find("div", class_="abstract-text")
        if abstract_element:
            details["abstract"] = abstract_element.get_text(strip=True)
        
        # Extract keywords
        keywords_section = soup.find("div", class_="keywords-container")
        if keywords_section:
            keyword_elements = keywords_section.find_all("a", class_="doc-keywords-link")
            details["keywords"] = [keyword.get_text(strip=True) for keyword in keyword_elements]
        
        # Extract DOI
        doi_element = soup.find("div", class_="doi-container")
        if doi_element:
            details["doi"] = doi_element.get_text(strip=True).replace("DOI:", "").strip()
        
        return details 