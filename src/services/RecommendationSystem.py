import sqlite3
import datetime
from urllib.parse import urlparse
from getpass import getpass
import hashlib
from src.data_processing import WebCrawler




class RecommendationSystem:
    def __init__(self):
        self.db_name = r'data\recommendation_system.db'
        self.current_user = None
        self.init_db()


    # region 初始化数据库
    def init_db(self):
        """初始化数据库"""

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # 用户信息表
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE NOT NULL,
                     password TEXT NOT NULL)''')
        # 订阅信息表
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER,
                     url TEXT NOT NULL,
                     prompt TEXT NOT NULL,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     FOREIGN KEY (user_id) REFERENCES users(id))''')
        # 内容历史记录表
        c.execute('''CREATE TABLE IF NOT EXISTS content_history 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subscription_id INTEGER,
                    content_hash TEXT,
                    content_text TEXT,          -- 新增: 存储原始内容文本
                    content_url TEXT,          -- 新增: 存储内容相关的URL
                    status INTEGER DEFAULT 0,  -- 新增: 状态标记（例如已读/未读）
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id))''')
        
        conn.commit()
        conn.close()
        
    # endregion

    def hash_password(self, password):
        """简单密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        """注册用户"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            c.execute('SELECT id FROM users WHERE username = ?', (username,))
            if c.fetchone():
                print("用户名已存在")
                return False
                
            hashed_password = self.hash_password(password)
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                     (username, hashed_password))
            conn.commit()
            print("注册成功")
            return True
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return False
        finally:
            conn.close()

    def login(self, username, password):
        """用户登录"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        hashed_password = self.hash_password(password)
        c.execute('SELECT id FROM users WHERE username = ? AND password = ?',
                 (username, hashed_password))
        user = c.fetchone()
        
        conn.close()
        
        if user:
            self.current_user = user[0]
            print("登录成功")
            return True
        else:
            print("用户名或密码错误")
            return False

    def add_subscription(self, url, prompt):
        """添加订阅并立即进行第一次爬取"""
        if not self.current_user:
            print("请先登录")
            return False
            
        # 验证URL格式
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                print("无效的URL格式")
                return False
        except ValueError:
            print("无效的URL格式")
            return False
            
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            # 插入订阅记录
            c.execute('INSERT INTO subscriptions (user_id, url, prompt) VALUES (?, ?, ?)',
                    (self.current_user, url, prompt))
            subscription_id = c.lastrowid  # 获取刚插入的订阅ID
            conn.commit()
            print(f"订阅添加成功: {url} - {prompt}")
            
            # 创建WebCrawler实例并立即爬取
            crawler = WebCrawler(f"user_{self.current_user}", self.db_name)
            crawl_success = crawler.crawl_and_store(url, subscription_id)
            
            if crawl_success:
                print(f"初次爬取并保存成功: {url}")
            else:
                print(f"初次爬取失败: {url}")
                
            return True
            
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return False
        finally:
            conn.close()
    def run(self):
        """主循环"""
        while True:
            print("\n1. 注册")
            print("2. 登录")
            print("3. 添加订阅")
            print("4. 退出")
            choice = input("请选择操作 (1-4): ")

            if choice == '1':
                username = input("请输入用户名: ")
                password = getpass("请输入密码: ")
                self.register(username, password)

            elif choice == '2':
                username = input("请输入用户名: ")
                password = getpass("请输入密码: ")
                self.login(username, password)

            elif choice == '3':
                if not self.current_user:
                    print("请先登录")
                    continue
                url = input("请输入URL: ")
                prompt = input("请输入提示词: ")
                self.add_subscription(url, prompt)

            elif choice == '4':
                print("退出程序")
                break

            else:
                print("无效选项，请重试")
