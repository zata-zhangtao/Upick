import os
import sqlite3
from .db_operate import add_subscription, refresh_content, get_updates, delete_subscription, get_subscriptions, delete_old_content, save_summary_feedback
from .config import SUBSCRIPTIONS_DB_PATH
from src.log import get_logger

logger = get_logger("db.init")

__all__ = [
    "add_subscription",
    "refresh_content",
    "get_updates",
    "delete_subscription",
    "get_subscriptions",
    "delete_old_content",
    "SUBSCRIPTIONS_DB_PATH",
    "save_summary_feedback"
]

def init_db():
    """Initialize SQLite database with subscription and content tables"""
    logger.info("Initializing database...")
    
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    
    # Enable timezone support
    c.execute("PRAGMA timezone='Asia/Shanghai'")
    
    # Create subscriptions table
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  url TEXT NOT NULL,
                  description TEXT,
                  check_interval INTEGER NOT NULL,
                  created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                  last_updated_at TIMESTAMP DEFAULT (datetime('now', 'localtime')))''')
    
    # Create contents table
    c.execute('''CREATE TABLE IF NOT EXISTS contents
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subscription_id INTEGER NOT NULL,
                  content TEXT NOT NULL,
                  fetched_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                  FOREIGN KEY (subscription_id) REFERENCES subscriptions (id))''')
    
    # Create content_updates table
    c.execute('''CREATE TABLE IF NOT EXISTS content_updates
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subscription_id INTEGER NOT NULL,
                  old_content_id INTEGER NOT NULL,
                  new_content_id INTEGER NOT NULL,
                  similarity_ratio REAL NOT NULL,
                  diff_details TEXT NOT NULL,
                  updated_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                  FOREIGN KEY (subscription_id) REFERENCES subscriptions (id),
                  FOREIGN KEY (old_content_id) REFERENCES contents (id),
                  FOREIGN KEY (new_content_id) REFERENCES contents (id))''')
    
    # Create summaries table with all columns including feedback columns
    c.execute('''CREATE TABLE IF NOT EXISTS summaries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  content_update_id INTEGER NOT NULL,
                  summary TEXT NOT NULL,
                  feedback_score REAL DEFAULT 0.0,
                  feedback_comment TEXT,
                  feedback_at TIMESTAMP,
                  created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                  FOREIGN KEY (content_update_id) REFERENCES content_updates (id))''')
    
    conn.commit()
    conn.close()
    
    logger.info("Database initialized successfully")

init_db()
