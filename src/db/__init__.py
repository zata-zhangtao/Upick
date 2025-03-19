import os
import sqlite3
from .db_operate import add_subscription, refresh_content, get_updates

from .config import SUBSCRIPTIONS_DB_PATH



__all__ = [
    "add_subscription",
    "refresh_content",
    "get_updates",
    "SUBSCRIPTIONS_DB_PATH"
]







def init_db():
    """Initialize SQLite database with subscription and content tables"""
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    
    # Enable timezone support
    c.execute("PRAGMA timezone='Asia/Shanghai'")
    
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  url TEXT NOT NULL,
                  check_interval INTEGER NOT NULL,
                  created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                  last_updated_at TIMESTAMP DEFAULT (datetime('now', 'localtime')))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS contents
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subscription_id INTEGER NOT NULL,
                  content TEXT NOT NULL,
                  fetched_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                  FOREIGN KEY (subscription_id) REFERENCES subscriptions (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS content_updates
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subscription_id INTEGER NOT NULL,
                  old_content_id INTEGER NOT NULL,
                  new_content_id INTEGER NOT NULL,
                  similarity_ratio REAL NOT NULL,
                  diff_details TEXT NOT NULL,
                  summary TEXT,
                  updated_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                  FOREIGN KEY (subscription_id) REFERENCES subscriptions (id),
                  FOREIGN KEY (old_content_id) REFERENCES contents (id),
                  FOREIGN KEY (new_content_id) REFERENCES contents (id))''')
    conn.commit()
    conn.close()
    

init_db()
    
