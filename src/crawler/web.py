"""
General web crawler implementation for extracting clean text content from websites.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
from .base import BaseCrawler
from . import utils
from .registry import registry


class WebCrawler(BaseCrawler):
    """
    General-purpose web crawler for fetching and cleaning content from any website.
    Specialized in extracting readable text content from HTML pages.
    """
    
    def __init__(self, user_agent: Optional[str] = None):
        """
        Initialize the web crawler with default headers.
        
        Args:
            user_agent: Optional custom user agent string
        """
        default_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.headers = {
            'User-Agent': user_agent or default_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

    def detect_encoding(self, response: requests.Response, content: bytes) -> str:
        """
        Detect the encoding of the webpage content.
        
        - 自动检测网页内容的字符编码，确保网页内容能够被正确解析和显示
        - 处理不同网站可能使用的不同编码方式
        
        Args:
            response: HTTP response object
            content: Raw content bytes
            
        Returns:
            Detected character encoding 返回编码
        """
        if 'charset' in response.headers.get('content-type', '').lower():
            return response.apparent_encoding
        
        soup = BeautifulSoup(content, 'html.parser')
        meta_charset = soup.find('meta', charset=True)
        meta_content = soup.find('meta', {'http-equiv': 'Content-Type'})
        
        if meta_charset:
            return meta_charset.get('charset')
        elif meta_content and 'charset' in meta_content.get('content', '').lower():
            return meta_content.get('content').lower().split('charset=')[-1]
        
        # Try common encodings
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
        for encoding in encodings:
            try:
                content.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue
        return response.apparent_encoding

    def clean_html(self, soup: BeautifulSoup) -> str:
        """
        Clean HTML content by removing unwanted elements and attributes.
        
        - 移除不必要的HTML元素和属性
        - 保留文本内容，确保网页内容能够被正确解析和显示
        - 保留链接（a标签）的URL信息
        
        Args:
            soup: BeautifulSoup object containing the parsed HTML
            
        Returns:
            Clean text content with preserved links
        """
        for tag in soup.find_all(['style', 'script']):
            tag.decompose()
            
        for tag in soup.find_all():
            if 'style' in tag.attrs:
                del tag['style']
        
        # Preserve links by adding URL in parentheses after link text
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href')
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                # If the link already has text, append the URL in parentheses
                if a_tag.get_text().strip():
                    a_tag.string = f"{a_tag.get_text().strip()} ({href})"
                else:
                    a_tag.string = href
        
        text = soup.get_text(separator='\n').strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n'.join(lines)

    def fetch_and_clean_content(self, url: str, max_retries: int = 3) -> str:
        """
        Fetch webpage content and clean it to extract readable text.
        - 获取网页内容并清理，提取可读的文本内容
        - 使用自动检测的编码方式处理网页内容
        - 移除不必要的HTML元素和属性
        - 保留文本内容，确保网页内容能够被正确解析和显示
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retries on failure
            
        Returns:
            Clean text content or error message
        """
        def fetch_operation():
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            encoding = self.detect_encoding(response, response.content)
            response.encoding = encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self.clean_html(soup)
        
        try:
            # Use the retry utility function
            result = utils.retry(fetch_operation, max_retries=max_retries)
            if result is None:
                return f"Failed to retrieve content from {url} after {max_retries} attempts"
            return result
        except Exception as e:
            return f"Error: {e}"
            
    def fetch_structured_content(self, url: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Fetch webpage content and return a structured object with metadata.
        - 根据fetch_and_clean_content获取的内容，并返回结构化对象，包含元数据
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retries on failure
            
        Returns:
            Dictionary with content and metadata 返回包含内容和元数据的字典
        """
        content = self.fetch_and_clean_content(url, max_retries)
        
        # Check if content is an error message
        if content.startswith("Error:") or content.startswith("Failed to"):
            return {"url": url, "error": content, "content": None}
        
        return {
            "url": url,
            "content": content,
            "timestamp": utils.get_current_timestamp()
        }
    
    def crawl(self, url: str) -> List[Dict[str, Any]]:
        """
        Crawl the specified URL and extract data.
        - 爬取指定URL并提取数据
        - 如果存在专门的爬虫，则使用专门的爬虫
        - 如果不存在专门的爬虫，则使用通用的爬虫
        
        Args:
            url: URL to crawl
            
        Returns:
            List of dictionaries containing the extracted data 返回包含提取数据的列表
        """
        # Check if there's a specialized crawler for this URL
        specialized_crawler_class = registry.get_crawler(url)
        
        if specialized_crawler_class:
            # Use the specialized crawler
            crawler = specialized_crawler_class()
            return crawler.crawl(url)
        
        # Fall back to general web crawler
        result = self.fetch_structured_content(url)
        return [result] 
    

if __name__ == "__main__":
    crawler = WebCrawler()

    result = crawler.crawl("https://arxiv.org/list/cs.AI/new")
    # print(crawler.crawl("https://arxiv.org/list/cs.AI/new"))
    # print(len(result))
    # print(result[0])
    print(type(result[0]))
    import numpy as np
    # print(np.array(result).shape)



