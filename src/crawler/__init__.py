"""
UPick Crawler Module

This module provides web crawling functionality for various websites.
"""

from .base import BaseCrawler
from .arxiv import ArxivCrawler
from .ieee import IEEECrawler
from .web import WebCrawler
from .registry import registry, CrawlerRegistry
from . import utils

# Register built-in crawlers with the registry
registry.register(r'https?://arxiv\.org/.*', ArxivCrawler)
registry.register(r'https?://ieee\.org/.*', IEEECrawler)

__all__ = [
    "BaseCrawler", 
    "ArxivCrawler", 
    "IEEECrawler", 
    "WebCrawler", 
    "CrawlerRegistry",
    "registry",
    "utils"
] 