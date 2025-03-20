"""
Utility functions for web crawling.
"""

import time
from typing import Optional, Callable, Any, TypeVar, Dict, List
import logging
import os
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)
T = TypeVar('T')


def retry(func: Callable[..., T], max_retries: int = 3, delay: float = 2.0) -> Optional[T]:
    """
    Retry a function call with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Initial delay between retries in seconds
        
    Returns:
        Result of the function or None if all retries failed
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt < max_retries:
                wait_time = delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.2f}s")
                time.sleep(wait_time)
            else:
                logger.error(f"All {max_retries + 1} attempts failed: {e}")
                return None


def ensure_directory(directory: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure exists
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")


def merge_results(results_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge multiple crawl results, removing duplicates based on a key.
    
    Args:
        results_list: List of crawl results to merge
        
    Returns:
        Merged list with duplicates removed
    """
    merged = {}
    
    for results in results_list:
        for item in results:
            # Use a unique identifier if available, or fallback to title
            key = item.get("arxiv_id") or item.get("doi") or item.get("url") or item.get("title")
            if key and key not in merged:
                merged[key] = item
    
    return list(merged.values())


def get_current_timestamp() -> str:
    """
    Get the current timestamp in ISO format.
    
    Returns:
        Current timestamp as string
    """
    return datetime.now().isoformat() 