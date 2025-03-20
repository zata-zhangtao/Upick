"""
Command-line interface for the UPick crawler.
"""

import argparse
import sys
import os
from typing import Optional
import json
from datetime import datetime

from .base import BaseCrawler
from .arxiv import ArxivCrawler
from .ieee import IEEECrawler
from .web import WebCrawler
from . import utils


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="UPick Web Crawler")
    
    parser.add_argument("--source", "-s", type=str, choices=["arxiv", "ieee", "web"], 
                        default="arxiv", help="Source to crawl (default: arxiv)")
    
    parser.add_argument("--url", "-u", type=str,
                        help="URL to crawl (default: use the crawler's default URL)")
    
    parser.add_argument("--output", "-o", type=str,
                        help="Output filename (default: <source>_content_<timestamp>.json)")
    
    parser.add_argument("--output-dir", "-d", type=str, default="data",
                        help="Output directory (default: data)")
    
    parser.add_argument("--text-only", "-t", action="store_true",
                        help="Extract only text content (for web source)")
    
    parser.add_argument("--retries", "-r", type=int, default=3,
                        help="Number of retries for failed requests (default: 3)")
    
    return parser.parse_args()


def get_crawler(source: str) -> BaseCrawler:
    """
    Get the appropriate crawler based on the source.
    
    Args:
        source: Source to crawl
        
    Returns:
        Crawler instance
    """
    if source == "arxiv":
        return ArxivCrawler()
    elif source == "ieee":
        return IEEECrawler()
    elif source == "web":
        # Note: WebCrawler doesn't inherit from BaseCrawler, but we'll handle it specially
        return None  # Handled separately in main
    else:
        raise ValueError(f"Unknown source: {source}")


def main():
    """Main entry point for the crawler CLI."""
    args = parse_args()
    
    # Ensure output directory exists
    utils.ensure_directory(args.output_dir)
    
    # Generate output filename if not provided
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = os.path.join(args.output_dir, f"{args.source}_content_{timestamp}.json")
    else:
        args.output = os.path.join(args.output_dir, args.output)
    
    # Handle web crawler specially
    if args.source == "web":
        if not args.url:
            print("Error: URL is required for web source.")
            return 1
            
        web_crawler = WebCrawler()
        print(f"Starting web crawler for: {args.url}")
        
        try:
            if args.text_only:
                # Just get clean text
                content = web_crawler.fetch_and_clean_content(args.url, max_retries=args.retries)
                
                # Save raw text
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                # Get structured content
                result = web_crawler.fetch_structured_content(args.url, max_retries=args.retries)
                
                # Save as JSON
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                    
            print(f"Content saved to: {args.output}")
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    # Handle structured crawlers
    try:
        crawler = get_crawler(args.source)
        print(f"Starting {args.source} crawler...")
        
        papers = crawler.crawl(args.url)
        
        if papers:
            crawler.save_to_file(papers, args.output)
            print(f"Crawl complete! Found {len(papers)} papers.")
            print(f"Results saved to: {args.output}")
        else:
            print("No papers found.")
            return 1
            
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 