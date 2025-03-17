from ast import List
import sqlite3
from src.agent import SubscriptionAgent


SUBSCRIPTIONS_DB_PATH = 'resources\database\subscriptions.db'

def add_subscription(url, check_interval):
    """Add new subscription to database and fetch initial content or update check interval if URL exists"""
    from src.services.crawler import WebCrawler
    from datetime import datetime

    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()

    # Check if URL already exists
    c.execute("SELECT id FROM subscriptions WHERE url = ?", (url,))
    existing = c.fetchone()

    if existing:
        # Update check interval for existing subscription
        subscription_id = existing[0]
        c.execute("UPDATE subscriptions SET check_interval = ? WHERE id = ?",
                  (check_interval, subscription_id))
        
        conn.commit()
        conn.close()
        return f"Updated check interval for existing subscription: {url}"
    else:
        # Add new subscription
        c.execute("INSERT INTO subscriptions (url, check_interval) VALUES (?, ?)",
                  (url, check_interval))
        subscription_id = c.lastrowid

        # Fetch initial content
        crawler = WebCrawler()
        content = crawler.fetch_and_clean_content(url)

        # Store content
        c.execute("INSERT INTO contents (subscription_id, content) VALUES (?, ?)",
                  (subscription_id, content))

        # Update last_updated_at timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("UPDATE subscriptions SET last_updated_at = ? WHERE id = ?",
                  (current_time, subscription_id))

        conn.commit()
        conn.close()
        return f"Successfully added subscription and fetched initial content: {url} : {content}"

def refresh_content():
    """Refresh content for all subscriptions that need updating based on check_interval"""
    from src.services.crawler import WebCrawler
    from datetime import datetime, timedelta
    from src.services.contentdiff import get_content_diff, has_significant_changes
    import json

    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()

    # Get all subscriptions with their last update time and check interval
    c.execute("""
        SELECT id, url, last_updated_at, check_interval 
        FROM subscriptions
    """)
    subscriptions = c.fetchall()
    
    current_time = datetime.now()
    crawler = WebCrawler()
    updated_count = 0
    
    
    # 
    for sub_id, url, last_updated, interval in subscriptions:
        last_updated = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
        time_diff = current_time - last_updated
        
        # Check if enough time has passed (interval is in minutes)
        if time_diff > timedelta(minutes=interval):
            # Get most recent content for this subscription
            c.execute("""
                SELECT id, content FROM contents 
                WHERE subscription_id = ? 
                ORDER BY fetched_at DESC LIMIT 1
            """, (sub_id,))
            old_content_row = c.fetchone()
            old_content_id = old_content_row[0]
            old_content = old_content_row[1]
            
            # Fetch new content
            new_content = crawler.fetch_and_clean_content(url)
            
            # Store new content
            c.execute("""
                INSERT INTO contents (subscription_id, content) 
                VALUES (?, ?)
            """, (sub_id, new_content))
            new_content_id = c.lastrowid
            
            # Calculate differences and store in content_updates
            similarity, diffs = get_content_diff(old_content, new_content)
            summary = SubscriptionAgent().generate_summary(diffs)
            print(summary)
            c.execute("""
                INSERT INTO content_updates 
                (subscription_id, old_content_id, new_content_id, similarity_ratio, diff_details, summary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sub_id, old_content_id, new_content_id, similarity, json.dumps(diffs,ensure_ascii=False), json.dumps(summary.model_dump(),ensure_ascii=False)))
            
            # Update last_updated_at timestamp
            c.execute("""
                UPDATE subscriptions 
                SET last_updated_at = ? 
                WHERE id = ?
            """, (current_time.strftime('%Y-%m-%d %H:%M:%S'), sub_id))
            
            updated_count += 1

    conn.commit()
    conn.close()

    return f"Successfully refreshed content for {updated_count} "

def get_updates() -> List[List[str, str, str, str]]:
    """
    Get content updates from database.
    
    Returns:
        List[List[str, str, str, str]]: A list of updates, where each update contains
                                        [url, updated_at, summary, diff_details]
    """
    # Connect to database
    conn = sqlite3.connect('resources/database/subscriptions.db')
    c = conn.cursor()
    
    # Query for content updates joined with subscription information
    c.execute("""
        SELECT cu.diff_details, cu.summary, cu.updated_at, s.url
        FROM content_updates cu
        JOIN subscriptions s ON cu.subscription_id = s.id
        ORDER BY cu.updated_at DESC
    """)
    
    # Fetch all results
    updates = c.fetchall()
    conn.close()
    
    # Format updates into a more readable structure
    formatted_updates = []
    for diff_details, summary, updated_at, url in updates:
        formatted_updates.append([url, updated_at, summary, diff_details])
    
    return formatted_updates




