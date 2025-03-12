import sqlite3
def add_subscription(url, check_interval):
    """Add new subscription to database"""
    conn = sqlite3.connect('resources\database\subscriptions.db')
    c = conn.cursor()
    c.execute("INSERT INTO subscriptions (url, check_interval) VALUES (?, ?)",
              (url, check_interval))
    conn.commit()
    conn.close()
    return f"Successfully added subscription: {url}"
