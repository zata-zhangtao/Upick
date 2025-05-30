from typing import List,Tuple
import sqlite3
from src.agent import SubscriptionAgent
from src.log import get_logger
from src.crawler import WebCrawler
from datetime import datetime, timedelta
import json
from .config import SUBSCRIPTIONS_DB_PATH
logger = get_logger("db.db_operate")



def add_subscription(url:str, check_interval:int)->str:
    """添加订阅   Add new subscription to database and fetch initial content or update check interval if URL exists
    flowchart TD
        A[开始] --> B{URL是否为空?}
        B -->|是| C[返回错误: 请输入有效URL]
        B -->|否| D{URL格式是否正确?}
        D -->|否| E[返回错误: URL必须以http://或https://开头]
        D -->|是| F[连接数据库]
        F --> G{URL是否已存在?}
        
        G -->|是| H[更新检查间隔]
        H --> I[提交事务并关闭连接]
        I --> J[返回更新成功消息]
        
        G -->|否| K[添加新订阅]
        K --> L[获取初始内容]
        L --> src.crawler.WebCrawler-->L
        L --> M[存储内容到数据库]
        M --> N[更新最后更新时间]
        N --> O[插入content_updates记录]
        
        O --> P{内容是否有效?}
        P -->|否| Q[提交事务并关闭连接]
        Q --> R[返回获取内容失败消息]
        
        P -->|是| S[生成摘要]
        S -->src.agent.generate_summary -->S
        S --> T{摘要是否生成成功?}
        T -->|是| U[存储摘要到数据库]
        T -->|否| V[记录未生成摘要日志]
        U --> W[提交事务并关闭连接]
        V --> W
        W --> X[返回添加成功消息]
  
    Args:
        url (str): The URL of the subscription.
        check_interval (int): The interval in minutes between checks.
    Returns:
        str: A message indicating the result of the operation.
    """


    if not url:
        return "Please enter a valid URL"
    
    # Check if URL has a valid format
    if not url.startswith(('http://', 'https://')):
        return "Invalid URL format. URL must start with http:// or https://"

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
        # content = crawler.fetch_and_clean_content(url)
        content = crawler.crawl(url)  # this is a list of dicts
        content_json = json.dumps(content, ensure_ascii=False)

        logger.info(f"爬取内容content_json前100字符: {content_json[:100]}")

        c.execute("INSERT INTO contents (subscription_id, content) VALUES (?, ?)",
                (subscription_id, content_json))
        content_id = c.lastrowid
        # Update last_updated_at timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("UPDATE subscriptions SET last_updated_at = ? WHERE id = ?",
                (current_time, subscription_id))
        
        # insert into content_updates
        c.execute("""
                    INSERT INTO content_updates 
                    (subscription_id, old_content_id, new_content_id, similarity_ratio, diff_details)
                    VALUES (?, ?, ?, ?, ?)
                """, (subscription_id, "None", content_id, 0, content_json))
        
        #   如果内容为空，则返回失败
        logger.debug(f"Content details: {content}")
        logger.debug(f"Content type: {type(content)}")
        logger.debug(f"Content length: {len(content) if content else 0}")
        if content and len(content) > 0:
            logger.debug(f"First content item: {content[0]}")
        if content is None or  len(content) == 0 or content[0]["content"] is None or  content[0]["content"].startswith("Failed to retrieve content ") or "404" in content[0]["content"] or "502" in content[0]["content"]:
            conn.commit()
            conn.close()
            logger.error(f"Failed to retrieve content: {url}")
            return f"Failed to retrieve content: {url}"
        
        else:
            
            content_update_id = c.lastrowid

            # summary when first adding a subscription, generate a summary  第一次添加订阅时，生成摘要
            summary = SubscriptionAgent().generate_summary(content_json)

            if summary.content is not None and len(summary.content) > 0:
                logger.info(f"生成摘要并插入数据库... {url} --- {summary}")
                c.execute("INSERT INTO summaries (content_update_id, summary) VALUES (?, ?)",
                        (content_update_id, json.dumps(summary.model_dump(), ensure_ascii=False)))
            else:
                logger.info(f"没有生成摘要... {url}")
    
            logger.info(f"成功添加订阅并获取初始内容: {url}")
            conn.commit()
            conn.close()
            return f"Successfully added subscription and fetched initial content: {url}"

def refresh_content(similarity_threshold:float=0.95)->str:
    """ 刷新内容,根据订阅的url  Refresh content for all subscriptions that need updating based on check_interval

    Args:
        similarity_threshold (float): The threshold for similarity.
        default is 0.95
    Returns:
        str: A message indicating the number of subscriptions that were refreshed.

    """
    from src.services.contentdiff import get_content_diff, has_significant_changes

    logger.info("开始刷新内容...")

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
    logger.debug(f"开始遍历所有订阅...订阅长度: {len(subscriptions)}")
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
            new_content = crawler.crawl(url)
            new_content = json.dumps(new_content, ensure_ascii=False)
            
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
                # Insert into content_updates (without summary field)
                c.execute("""
                    INSERT INTO content_updates 
                    (subscription_id, old_content_id, new_content_id, similarity_ratio, diff_details)
                    VALUES (?, ?, ?, ?, ?)
                """, (sub_id, old_content_id, new_content_id, similarity, json.dumps(diffs,ensure_ascii=False)))
                
                content_update_id = c.lastrowid
                
                # Generate summary
                summary = SubscriptionAgent().generate_summary(diffs)
                if summary.content is not None and len(summary.content) > 0:
                    logger.info(f"生成摘要并插入数据库... {url} --- {summary}")
                    
                    # Store summary in the summaries table
                    c.execute("""
                        INSERT INTO summaries 
                        (content_update_id, summary)
                        VALUES (?, ?)
                    """, (content_update_id, json.dumps(summary.model_dump(), ensure_ascii=False)))
                else:
                    logger.info(f"没有生成摘要... {url}")
                
            # 更新最后检查时间,无论是否生成摘要  "Update last_updated_at timestamp, whether a summary is generated or not"
            c.execute("""
                UPDATE subscriptions 
                SET last_updated_at = ? 
                WHERE id = ?
            """, (current_time.strftime('%Y-%m-%d %H:%M:%S'), sub_id))
            
            updated_count += 1

            conn.commit()
    conn.close()
    logger.info(f"成功刷新内容... {updated_count} 个订阅")

    return f"Successfully refreshed content for {updated_count} subscriptions"

def get_updates() -> List[Tuple[str, str, str, str]]:
    """ 获取内容更新  Get content updates from database.
    
    Returns:
        List[List[str, str, str, str]]: A list of updates, where each update contains
                                        [url, updated_at, summary, diff_details]
    """
    # Connect to database
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    
    # Query for content updates joined with subscription information and summaries
    c.execute("""
        SELECT cu.diff_details, s.summary, cu.updated_at, sub.url, cu.id, s.id
        FROM content_updates cu
        JOIN subscriptions sub ON cu.subscription_id = sub.id
        JOIN summaries s ON s.content_update_id = cu.id
        ORDER BY cu.updated_at DESC
    """)
    
    # Fetch all results
    updates = c.fetchall()
    conn.close()
    
    # Format updates into a more readable structure
    formatted_updates = []
    for diff_details, summary, updated_at, url, content_update_id, summary_id in updates:
        formatted_updates.append([url, updated_at, summary, diff_details, content_update_id, summary_id])
    
    return formatted_updates

def delete_subscription(subscription_id: int) -> str:
    """删除订阅   Delete a subscription and all associated data
    
    Args:
        subscription_id (int): The ID of the subscription to delete.
        
    Returns:
        str: A message indicating the result of the operation.
    """
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    
    try:
        # Get subscription URL for logging/return message
        c.execute("SELECT url FROM subscriptions WHERE id = ?", (subscription_id,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            return f"No subscription found with ID {subscription_id}"
        
        url = result[0]
        
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Get all content_update_ids to delete related summaries
        c.execute("""
            SELECT id FROM content_updates 
            WHERE subscription_id = ?
        """, (subscription_id,))
        content_update_ids = [row[0] for row in c.fetchall()]
        
        # Delete related summaries
        if content_update_ids:
            placeholders = ','.join(['?'] * len(content_update_ids))
            c.execute(f"""
                DELETE FROM summaries 
                WHERE content_update_id IN ({placeholders})
            """, content_update_ids)
        
        # Delete from content_updates table
        c.execute("""
            DELETE FROM content_updates 
            WHERE subscription_id = ?
        """, (subscription_id,))
        
        # Delete from contents table
        c.execute("""
            DELETE FROM contents 
            WHERE subscription_id = ?
        """, (subscription_id,))
        
        # Finally delete the subscription
        c.execute("""
            DELETE FROM subscriptions 
            WHERE id = ?
        """, (subscription_id,))
        
        # Commit transaction
        conn.commit()
        conn.close()
        
        logger.info(f"成功删除订阅: {url}")
        return f"Successfully deleted subscription: {url}"
        
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        conn.close()
        logger.error(f"删除订阅时出错: {str(e)}")
        return f"Error deleting subscription: {str(e)}"

def get_subscriptions() -> List[Tuple[int, str, str, int]]:
    """获取所有订阅   Get all subscriptions from database
    
    Returns:
        List[Tuple[int, str, str, int]]: A list of subscriptions, where each subscription contains
                                        [id, url, last_updated_at, check_interval]
    """
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    
    c.execute("""
        SELECT id, url, last_updated_at, check_interval 
        FROM subscriptions
        ORDER BY last_updated_at DESC
    """)
    
    subscriptions = c.fetchall()
    conn.close()
    
    return subscriptions

def delete_old_content(days_to_keep: int = 30) -> str:
    """删除旧内容   Delete old content from the database to optimize storage
    
    This function deletes content older than the specified number of days
    while keeping the latest content for each subscription.
    
    Args:
        days_to_keep (int): Number of days of content to keep. Default is 30.
        
    Returns:
        str: A message indicating the result of the operation.
    """
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    
    try:
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Get the date threshold
        c.execute("""
            SELECT datetime('now', 'localtime', ?)
        """, (f'-{days_to_keep} days',))
        threshold_date = c.fetchone()[0]
        
        # Find content_updates older than the threshold, but exclude the latest update for each subscription
        c.execute("""
            WITH latest_updates AS (
                SELECT subscription_id, MAX(updated_at) as max_updated_at
                FROM content_updates
                GROUP BY subscription_id
            )
            SELECT cu.id 
            FROM content_updates cu
            LEFT JOIN latest_updates lu 
                ON cu.subscription_id = lu.subscription_id 
                AND cu.updated_at = lu.max_updated_at
            WHERE cu.updated_at < ? 
                AND lu.max_updated_at IS NULL
        """, (threshold_date,))
        
        old_content_update_ids = [row[0] for row in c.fetchall()]
        
        if not old_content_update_ids:
            conn.close()
            return f"No old content updates found to delete"
        
        # Delete related summaries
        placeholders = ','.join(['?'] * len(old_content_update_ids))
        c.execute(f"""
            DELETE FROM summaries 
            WHERE content_update_id IN ({placeholders})
        """, old_content_update_ids)
        summaries_deleted = c.rowcount
        
        # Delete old content updates
        c.execute(f"""
            DELETE FROM content_updates 
            WHERE id IN ({placeholders})
        """, old_content_update_ids)
        updates_deleted = c.rowcount
        
        # Find and delete content not referenced by any content_update
        c.execute("""
            DELETE FROM contents
            WHERE id NOT IN (
                SELECT old_content_id FROM content_updates
                UNION
                SELECT new_content_id FROM content_updates
            )
            AND fetched_at < ?
        """, (threshold_date,))
        contents_deleted = c.rowcount
        
        # Commit transaction
        conn.commit()
        conn.close()
        
        logger.info(f"成功删除过期内容: {updates_deleted} 更新, {summaries_deleted} 摘要, {contents_deleted} 内容")
        return f"Successfully deleted old content: {updates_deleted} updates, {summaries_deleted} summaries, {contents_deleted} contents"
        
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        conn.close()
        logger.error(f"删除旧内容时出错: {str(e)}")
        return f"Error deleting old content: {str(e)}"

def save_summary_feedback(summary_id: int, feedback_score: float, feedback_comment: str = None) -> str:
    """保存摘要反馈   Save feedback for a summary to be used in incremental learning
    
    Args:
        summary_id (int): The ID of the summary
        feedback_score (float): A score between 0.0 and 1.0 indicating quality
        feedback_comment (str, optional): Optional comment about the summary
        
    Returns:
        str: A message indicating success or failure
    """
    if not isinstance(feedback_score, (int, float)) or feedback_score < 0 or feedback_score > 1:
        return "Feedback score must be a number between 0 and 1"
    
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    
    try:
        # Check if the summary exists
        c.execute("SELECT id, content_update_id FROM summaries WHERE id = ?", (summary_id,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            return f"No summary found with ID {summary_id}"
        
        content_update_id = result[1]
        
        # Get the diff_details for the content update (for incremental learning)
        c.execute("SELECT diff_details FROM content_updates WHERE id = ?", (content_update_id,))
        diff_result = c.fetchone()
        
        if not diff_result:
            conn.close()
            return f"No content update found with ID {content_update_id}"
        
        diff_details = diff_result[0]
        
        # Update the summary with feedback
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("""
            UPDATE summaries
            SET feedback_score = ?, feedback_comment = ?, feedback_at = ?
            WHERE id = ?
        """, (feedback_score, feedback_comment, current_time, summary_id))
        
        conn.commit()
        
        # Call the incremental learning function with the feedback
        from src.agent.summary import SubscriptionAgent
        
        # Get the summary content
        c.execute("SELECT summary FROM summaries WHERE id = ?", (summary_id,))
        summary_content = c.fetchone()[0]
        
        # Extract summary data
        try:
            summary_data = json.loads(summary_content)
            key_points = summary_data.get('key_points', [])
            key_points_text = "\n".join(key_points) if isinstance(key_points, list) else str(key_points)
            
            # Create metadata
            metadata = {
                "summary_id": summary_id,
                "content_update_id": content_update_id,
                "feedback_comment": feedback_comment,
                "feedback_at": current_time
            }
            
            # Save to incremental learning system
            agent = SubscriptionAgent()
            agent.save_feedback(
                input_text=diff_details,
                output_text=key_points_text,
                feedback_score=feedback_score,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error saving to incremental learning: {str(e)}")
            # Continue anyway - we still want to save the feedback to the database
        
        conn.close()
        return f"Successfully saved feedback for summary {summary_id}"
        
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"Error saving summary feedback: {str(e)}")
        return f"Error saving feedback: {str(e)}"




if __name__ == "__main__":
    delete_subscription(6) # 删除订阅 id=2
