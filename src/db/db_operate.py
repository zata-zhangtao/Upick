from typing import List,Tuple
import sqlite3
from src.agent import SubscriptionAgent
from src.log import get_logger
from src.services.crawler import WebCrawler
from datetime import datetime
from .config import SUBSCRIPTIONS_DB_PATH
logger = get_logger("db.db_operate")





def add_subscription(url:str, check_interval:int)->str:
    """添加订阅   Add new subscription to database and fetch initial content or update check interval if URL exists
    Args:
        url (str): The URL of the subscription.
        check_interval (int): The interval in minutes between checks.
    Returns:
        str: A message indicating the result of the operation.
    """

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

def refresh_content(similarity_threshold:float=0.95)->str:
    """ 刷新内容,根据订阅的url  Refresh content for all subscriptions that need updating based on check_interval

    Args:
        similarity_threshold (float): The threshold for similarity.
        default is 0.95
    Returns:
        str: A message indicating the number of subscriptions that were refreshed.

    """
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
    subscriptions = c.fetchall() # 获取所有订阅 主要是url  Get all subscriptions
    
    current_time = datetime.now() # 当前时间  Current time
    crawler = WebCrawler() # 爬虫对象  WebCrawler object
    updated_count = 0 # 更新计数  Update count
    
    # 遍历所有订阅  Traverse all subscriptions
    for sub_id, url, last_updated, interval in subscriptions:
        last_updated = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S') # 将last_updated转换为datetime对象  Convert last_updated to datetime object
        time_diff = current_time - last_updated # 计算时间差  Calculate time difference
        
        # 检查是否足够时间  Check if enough time has passed (interval is in minutes)
        if time_diff > timedelta(minutes=interval): # 如果时间差大于间隔时间  If the time difference is greater than the interval
            # 获取最新内容  Get most recent content for this subscription
            c.execute("""
                SELECT id, content FROM contents 
                WHERE subscription_id = ? 
                ORDER BY fetched_at DESC LIMIT 1
            """, (sub_id,))
            old_content_row = c.fetchone() # 获取最新内容  Get most recent content for this subscription
            old_content_id = old_content_row[0] # 获取内容id  Get content id
            old_content = old_content_row[1] # 获取内容  Get content
            
            # 获取新内容  Fetch new content
            new_content = crawler.fetch_and_clean_content(url)
            
            # 存储新内容  Store new content
            c.execute("""
                INSERT INTO contents (subscription_id, content) 
                VALUES (?, ?)
            """, (sub_id, new_content))
            new_content_id = c.lastrowid # 获取新内容id  Get new content id
            
            # 计算差异并存储在content_updates中  Calculate differences and store in content_updates
            similarity, diffs = get_content_diff(old_content, new_content)
            
            # 如果相似度低于阈值，则生成摘要   if similarity is less than the threshold, generate a summary
            if similarity < similarity_threshold and len(diffs)>0:
                summary = SubscriptionAgent().generate_summary(diffs)
                logger.debug(f"生成摘要: {summary}")
                c.execute("""
                    INSERT INTO content_updates 
                    (subscription_id, old_content_id, new_content_id, similarity_ratio, diff_details, summary)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (sub_id, old_content_id, new_content_id, similarity, json.dumps(diffs,ensure_ascii=False), json.dumps(summary.model_dump(),ensure_ascii=False)))
            
            # 更新最后检查时间,无论是否生成摘要  "Update last_updated_at timestamp, whether a summary is generated or not"
            c.execute("""
                UPDATE subscriptions 
                SET last_updated_at = ? 
                WHERE id = ?
            """, (current_time.strftime('%Y-%m-%d %H:%M:%S'), sub_id))
            
            updated_count += 1

    conn.commit()
    conn.close()

    return f"Successfully refreshed content for {updated_count} "

def get_updates() -> List[Tuple[str, str, str, str]]:
    """ 获取内容更新  Get content updates from database.
    
    Returns:
        List[List[str, str, str, str]]: A list of updates, where each update contains
                                        [url, updated_at, summary, diff_details]
    """
    # Connect to database
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
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




