# 文件名: data_query.py

import sqlite3
from typing import List, Tuple, Optional
import datetime

class DataQuery:
    """数据库查询类，提供对推荐系统数据库的查询功能"""
    
    def __init__(self, db_path: str = r'data\recommendation_system.db'):
        """初始化查询类
        
        Args:
            db_path (str): 数据库文件路径
        """
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def user_exists(self, user_id: int) -> bool:
        """检查用户是否存在
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            bool: 用户是否存在
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('SELECT id FROM users WHERE id = ?', (user_id,))
            result = c.fetchone()
            conn.close()
            return bool(result)
        except sqlite3.Error as e:
            print(f"检查用户失败: {e}")
            return False

    def get_user_subscriptions(self, user_id: int) -> List[Tuple]:
        """获取用户的所有订阅
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            List[Tuple]: 订阅列表，每个元素包含(id, url, prompt, created_at)
        """
        if not self.user_exists(user_id):
            print("用户不存在")
            return []
            
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('''SELECT id, url, prompt, created_at 
                        FROM subscriptions 
                        WHERE user_id = ? 
                        ORDER BY created_at DESC''', (user_id,))
            results = c.fetchall()
            conn.close()
            return results
        except sqlite3.Error as e:
            print(f"查询订阅失败: {e}")
            return []

    def get_content_history(self, subscription_id: int, 
                          limit: int = 100) -> List[Tuple]:
        """获取特定订阅的内容历史
        
        Args:
            subscription_id (int): 订阅ID
            limit (int): 返回的最大记录数，默认为100
            
        Returns:
            List[Tuple]: 内容历史列表，每个元素包含(id, content_hash, content_text, 
                        content_url, status, recorded_at)
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            # 验证订阅是否存在
            c.execute('SELECT user_id FROM subscriptions WHERE id = ?', (subscription_id,))
            user_id = c.fetchone()
            if not user_id or not self.user_exists(user_id[0]):
                print("订阅或用户不存在")
                return []

            c.execute('''SELECT id, content_hash, content_text, content_url, 
                        status, recorded_at 
                        FROM content_history 
                        WHERE subscription_id = ? 
                        ORDER BY recorded_at DESC 
                        LIMIT ?''', (subscription_id, limit))
            results = c.fetchall()
            conn.close()
            return results
        except sqlite3.Error as e:
            print(f"查询内容历史失败: {e}")
            return []

    def get_unread_content(self, user_id: int) -> List[Tuple]:
        """获取用户的所有未读内容
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            List[Tuple]: 未读内容列表，每个元素包含(subscription_id, content_url, 
                        content_text, recorded_at)
        """
        if not self.user_exists(user_id):
            print("用户不存在")
            return []
            
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('''SELECT ch.subscription_id, ch.content_url, ch.content_text, 
                        ch.recorded_at
                        FROM content_history ch
                        JOIN subscriptions s ON ch.subscription_id = s.id
                        WHERE s.user_id = ? AND ch.status = 0
                        ORDER BY ch.recorded_at DESC''', (user_id,))
            results = c.fetchall()
            conn.close()
            return results
        except sqlite3.Error as e:
            print(f"查询未读内容失败: {e}")
            return []

    def mark_content_as_read(self, content_id: int) -> bool:
        """将内容标记为已读
        
        Args:
            content_id (int): 内容历史记录ID
            
        Returns:
            bool: 操作是否成功
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            # 验证内容是否存在
            c.execute('SELECT subscription_id FROM content_history WHERE id = ?', (content_id,))
            sub_id = c.fetchone()
            if not sub_id:
                print("内容不存在")
                return False
                
            c.execute('UPDATE content_history SET status = 1 WHERE id = ?', 
                     (content_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"标记已读失败: {e}")
            return False

    def get_subscription_by_url(self, user_id: int, url: str) -> Optional[Tuple]:
        """根据URL获取订阅信息
        
        Args:
            user_id (int): 用户ID
            url (str): 订阅URL
            
        Returns:
            Optional[Tuple]: 订阅信息(id, url, prompt, created_at) 或 None
        """
        if not self.user_exists(user_id):
            print("用户不存在")
            return None
            
        try:
            conn = self._get_connection()
            c = conn.cursor()
            c.execute('SELECT id, url, prompt, created_at FROM subscriptions '
                     'WHERE user_id = ? AND url = ?', (user_id, url))
            result = c.fetchone()
            conn.close()
            return result
        except sqlite3.Error as e:
            print(f"查询订阅失败: {e}")
            return None

    def get_content_count(self, subscription_id: int) -> int:
        """获取特定订阅的内容总数
        
        Args:
            subscription_id (int): 订阅ID
            
        Returns:
            int: 内容总数
        """
        try:
            conn = self._get_connection()
            c = conn.cursor()
            # 验证订阅是否存在
            c.execute('SELECT user_id FROM subscriptions WHERE id = ?', (subscription_id,))
            user_id = c.fetchone()
            if not user_id or not self.user_exists(user_id[0]):
                print("订阅或用户不存在")
                return 0
                
            c.execute('SELECT COUNT(*) FROM content_history WHERE subscription_id = ?', 
                     (subscription_id,))
            count = c.fetchone()[0]
            conn.close()
            return count
        except sqlite3.Error as e:
            print(f"查询内容总数失败: {e}")
            return 0

# 示例使用
if __name__ == "__main__":
    query = DataQuery()
    
    user_id = 1  # 示例用户ID
    if query.user_exists(user_id):
        subscriptions = query.get_user_subscriptions(user_id)
        print("用户订阅:", subscriptions)
        
        if subscriptions:
            sub_id = subscriptions[0][0]
            history = query.get_content_history(sub_id)
            print("内容历史:", history)
            
        unread = query.get_unread_content(user_id)
        print("未读内容:", unread)
    else:
        print("测试用户不存在")