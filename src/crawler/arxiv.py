"""
arXiv网站的爬虫实现
Crawler implementation for arXiv website.
"""

from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup, Tag
from .base import BaseCrawler
from src.log import get_logger
logger = get_logger("crawler.arxiv")


class ArxivCrawler(BaseCrawler):
    """专用于爬取arXiv论文信息
    Specialized crawler for extracting papers from arXiv.
    """
    
    def __init__(self, default_url: str = "https://arxiv.org/list/cs.AI/new"):
        """
        初始化arXiv爬虫,设置默认URL
        Initialize the arXiv crawler with default URL.
        
        Args:
            default_url: Default URL for the arXiv listing page
        """
        super().__init__()
        self.default_url = default_url
    
    def crawl(self, url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        从指定URL爬取arXiv论文
        Crawl arXiv papers from the specified URL.
        
        Args:
            url: URL to crawl, uses default_url if not provided
            
        Returns:
            List of dictionaries containing paper information 包含论文信息的字典列表
        """
        target_url = url or self.default_url
        print(f"Starting crawl from: {target_url}")
        
        soup = self.fetch_page(target_url)
        if not soup:
            return []
        
        return self._extract_papers(soup)
    
    def _extract_papers(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        从解析后的HTML中提取论文信息
        Extract paper information from the parsed HTML.
        
        Args:
            soup: BeautifulSoup object containing the parsed HTML
            
        Returns:
            List of dictionaries containing paper information 包含论文信息的字典列表
        """
        papers = []
        
        # 查找所有论文条目(dt/dd对)
        # Find all paper entries (dt/dd pairs)
        dt_tags = soup.find_all("dt")
        
        for dt_tag in dt_tags:
            # 查找对应的dd标签
            # Find the corresponding dd tag
            dd_tag = dt_tag.find_next_sibling("dd")
            if not dd_tag:
                continue
            
            paper = self._extract_paper_info(dt_tag, dd_tag)
            if paper:
                papers.append(paper)
        
        return papers
    
    def _extract_paper_info(self, dt_tag: Tag, dd_tag: Tag) -> Dict[str, Any]:
        """
        从HTML元素中提取单篇论文的信息
        Extract information about a single paper from its HTML elements.
        
        Args:
            dt_tag: The dt tag containing the paper's link
            dd_tag: The dd tag containing the paper's metadata
            
        Returns:
            Dictionary containing the paper's information
        """
        paper = {}
        
        # 提取arXiv URL和ID
        # Extract arXiv URL and ID
        paper_link = dt_tag.find("a", href=True, title="Abstract")
        if paper_link:
            paper["arxiv_url"] = "https://arxiv.org" + paper_link["href"] if not paper_link["href"].startswith("http") else paper_link["href"]
            paper["arxiv_id"] = paper_link.text.strip()
        
        # 从dd标签提取元数据
        # Extract metadata from dd tag
        meta_div = dd_tag.find("div", class_="meta")
        if not meta_div:
            return paper
        
        # 提取标题
        # Extract title
        title_div = meta_div.find("div", class_="list-title mathjax")
        if title_div:
            title_text = title_div.get_text(strip=True)
            if "Title:" in title_text:
                title_text = title_text.split("Title:", 1)[1].strip()
            paper["title"] = title_text
        
        # 提取摘要
        # Extract abstract
        abstract = meta_div.find("p", class_="mathjax")
        if abstract:
            paper["abstract"] = abstract.get_text(strip=True)
        
        # 提取评论
        # Extract comments
        comments_div = meta_div.find("div", class_="list-comments mathjax")
        if comments_div:
            comments_text = comments_div.get_text(strip=True)
            if "Comments:" in comments_text:
                comments_text = comments_text.split("Comments:", 1)[1].strip()
            paper["comments"] = comments_text
        
        # 提取作者
        # Extract authors
        authors_div = meta_div.find("div", class_="list-authors")
        if authors_div:
            authors = [a.get_text(strip=True) for a in authors_div.find_all("a")]
            paper["authors"] = authors
        
        # 提取主题
        # Extract subjects
        subjects_div = meta_div.find("div", class_="list-subjects")
        if subjects_div:
            subjects_text = subjects_div.get_text(strip=True)
            if "Subjects:" in subjects_text:
                subjects_text = subjects_text.split("Subjects:", 1)[1].strip()
            paper["subjects"] = subjects_text
        
        return paper 
    
    
def main():
    """
    测试ArxivCrawler的主函数
    Main function to test the ArxivCrawler.
    """
    crawler = ArxivCrawler()
    papers = crawler.crawl()
    print(f"Found {len(papers)} papers")
    
    # 打印第一篇论文作为示例
    # Print the first paper as an example
    if papers:
        print("\nExample paper:")
        for key, value in papers[0].items():
            print(f"{key}: {value}")
            
    # 保存到文件
    # Save to file
    crawler.save_to_file(papers, "arxiv_papers.json")
    
    
if __name__ == "__main__":
    main()