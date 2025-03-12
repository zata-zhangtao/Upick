
__all__ = [
    "add_subscription",
]

from .db_operate import add_subscription

import sqlite3

def init_db():
    """Initialize SQLite database with subscription table"""
    conn = sqlite3.connect('resources\database\subscriptions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  url TEXT NOT NULL,
                  check_interval INTEGER NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    

init_db()
    
