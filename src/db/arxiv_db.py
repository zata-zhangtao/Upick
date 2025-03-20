import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .config import SUBSCRIPTIONS_DB_PATH
from src.log import get_logger

logger = get_logger("db.arxiv_db")

def init_arxiv_tables():
    """Initialize SQLite tables for arXiv papers storage"""
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    
    # Create arxiv_papers table
    c.execute('''CREATE TABLE IF NOT EXISTS arxiv_papers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  arxiv_id TEXT UNIQUE NOT NULL,
                  title TEXT NOT NULL,
                  abstract TEXT,
                  authors TEXT,
                  subjects TEXT,
                  arxiv_url TEXT,
                  comments TEXT,
                  fetched_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                  category TEXT)''')
    
    # Create arxiv_categories table for tracking categories fetched
    c.execute('''CREATE TABLE IF NOT EXISTS arxiv_categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category_code TEXT UNIQUE NOT NULL,
                  category_name TEXT NOT NULL,
                  last_fetched_at TIMESTAMP DEFAULT (datetime('now', 'localtime')))''')
    
    conn.commit()
    conn.close()
    
    logger.debug("ArXiv tables initialized")

def save_papers(papers: List[Dict[str, Any]], category: str = "cs.AI") -> str:
    """Save or update arXiv papers in the database
    
    Args:
        papers: List of paper dictionaries
        category: Category code of the papers
        
    Returns:
        Status message
    """
    if not papers:
        return "No papers to save"
    
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    
    new_count = 0
    updated_count = 0
    
    for paper in papers:
        arxiv_id = paper.get("arxiv_id")
        if not arxiv_id:
            continue
            
        # Check if paper already exists
        c.execute("SELECT id FROM arxiv_papers WHERE arxiv_id = ?", (arxiv_id,))
        existing = c.fetchone()
        
        # Prepare data
        title = paper.get("title", "")
        abstract = paper.get("abstract", "")
        authors = json.dumps(paper.get("authors", []), ensure_ascii=False)
        subjects = paper.get("subjects", "")
        arxiv_url = paper.get("arxiv_url", "")
        comments = paper.get("comments", "")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if existing:
            # Update existing paper
            c.execute("""
                UPDATE arxiv_papers
                SET title = ?, abstract = ?, authors = ?, subjects = ?, 
                    arxiv_url = ?, comments = ?, fetched_at = ?, category = ?
                WHERE arxiv_id = ?
            """, (title, abstract, authors, subjects, arxiv_url, comments, 
                 current_time, category, arxiv_id))
            updated_count += 1
        else:
            # Insert new paper
            c.execute("""
                INSERT INTO arxiv_papers
                (arxiv_id, title, abstract, authors, subjects, arxiv_url, comments, fetched_at, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (arxiv_id, title, abstract, authors, subjects, arxiv_url, 
                 comments, current_time, category))
            new_count += 1
    
    # Update category last fetched time
    c.execute("""
        INSERT INTO arxiv_categories (category_code, category_name, last_fetched_at)
        VALUES (?, ?, ?)
        ON CONFLICT(category_code) DO UPDATE SET last_fetched_at = excluded.last_fetched_at
    """, (category, category, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Saved {new_count} new papers and updated {updated_count} existing papers")
    return f"Saved {new_count} new papers and updated {updated_count} existing papers"

def get_papers(category: Optional[str] = None, 
               search_term: Optional[str] = None,
               subject_filter: Optional[str] = None,
               limit: int = 100) -> List[Dict[str, Any]]:
    """Get papers from the database with optional filtering
    
    Args:
        category: Filter by specific category
        search_term: Search in title, abstract, authors, subjects
        subject_filter: Filter by subject area
        limit: Maximum number of papers to return
        
    Returns:
        List of paper dictionaries
    """
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    c = conn.cursor()
    
    query = "SELECT * FROM arxiv_papers WHERE 1=1"
    params = []
    
    # Apply category filter
    if category:
        query += " AND category = ?"
        params.append(category)
    
    # Apply search filter
    if search_term:
        # Search in multiple fields
        query += """ AND (
            title LIKE ? OR 
            abstract LIKE ? OR 
            authors LIKE ? OR 
            subjects LIKE ?
        )"""
        search_pattern = f"%{search_term}%"
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
    
    # Apply subject filter
    if subject_filter:
        if subject_filter == "Computer Science":
            query += " AND subjects LIKE ?"
            params.append("%cs.%")
        elif subject_filter == "Physics":
            query += " AND (subjects LIKE ? OR subjects LIKE ?)"
            params.extend(["%physics%", "%physics.%"])
        elif subject_filter == "Mathematics":
            query += " AND (subjects LIKE ? OR subjects LIKE ?)"
            params.extend(["%math%", "%math.%"])
        elif subject_filter == "Other":
            query += """ AND subjects NOT LIKE ? 
                         AND subjects NOT LIKE ?
                         AND subjects NOT LIKE ?
                         AND subjects NOT LIKE ?
                         AND subjects NOT LIKE ?
                         AND subjects NOT LIKE ?"""
            params.extend(["%cs.%", "%physics%", "%physics.%", "%math%", "%math.%", "%stat.%"])
    
    # Order by most recent
    query += " ORDER BY fetched_at DESC LIMIT ?"
    params.append(limit)
    
    c.execute(query, params)
    results = c.fetchall()
    
    papers = []
    for row in results:
        # Convert to dictionary
        paper = dict(row)
        
        # Parse JSON authors
        try:
            if paper.get('authors'):
                paper['authors'] = json.loads(paper['authors'])
        except (json.JSONDecodeError, TypeError):
            paper['authors'] = []
        
        papers.append(paper)
    
    conn.close()
    logger.debug(f"Retrieved {len(papers)} papers from database")
    return papers

def get_categories() -> List[Dict[str, Any]]:
    """Get list of categories and their last fetch time
    
    Returns:
        List of category dictionaries
    """
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM arxiv_categories ORDER BY last_fetched_at DESC")
    categories = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return categories

def delete_old_papers(days_to_keep: int = 30) -> str:
    """Delete papers older than specified days
    
    Args:
        days_to_keep: Number of days to keep papers
        
    Returns:
        Status message
    """
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    
    # Calculate cutoff date
    cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d %H:%M:%S')
    
    # Delete old papers
    c.execute("DELETE FROM arxiv_papers WHERE fetched_at < ?", (cutoff_date,))
    deleted_count = c.rowcount
    
    conn.commit()
    conn.close()
    
    logger.info(f"Deleted {deleted_count} papers older than {days_to_keep} days")
    return f"Deleted {deleted_count} papers older than {days_to_keep} days"

# Initialize tables when module is imported
init_arxiv_tables() 