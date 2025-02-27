import sqlite3
import datetime
from urllib.parse import urlparse
from getpass import getpass
import hashlib
from src.data_processing import WebCrawler
import pandas as pd



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

    # region 注册登录
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
            return "登录成功", "已登录", "已登录"  # Return values for login_output, status, status_display
        else:
            return "用户名或密码错误", "未登录", "未登录"  # Return values for login_output, status, status_display
    # ednregion
    
    # region 添加订阅
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
    # endregion
    
    def get_subscriptions(self):
        """获取当前用户的订阅信息"""
        if not self.current_user:
            return "请先登录", []  # Return empty list for dataframe if not logged in
        
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            c.execute('SELECT url, prompt, created_at FROM subscriptions WHERE user_id = ?', (self.current_user,))
            subscriptions = c.fetchall()
            
            if not subscriptions:
                return "暂无订阅", []  # Return empty list if no subscriptions
            
            # Convert to a list of dictionaries for Gradio Dataframe
            subscription_list = [{"URL": row[0], "提示词": row[1], "创建时间": row[2]} for row in subscriptions]
            return "订阅列表如下", pd.DataFrame(subscription_list)  # Return success message and data
        
        except sqlite3.Error as e:
            return f"数据库错误: {e}", []  # Return error message and empty list
        finally:
            conn.close()
            
            
            
    def get_subscription_updates(self):
        """获取当前用户的订阅更新内容"""
        if not self.current_user:
            return "请先登录", []  # Return empty list for dataframe if not logged in
        
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            # Join subscriptions and content_history to get URL and content details
            c.execute('''
                SELECT s.url, ch.content_url, ch.content_text, ch.recorded_at, ch.status
                FROM subscriptions s
                LEFT JOIN content_history ch ON s.id = ch.subscription_id
                WHERE s.user_id = ?
                ORDER BY ch.recorded_at DESC
            ''', (self.current_user,))
            updates = c.fetchall()
            
            if not updates or all(update[1] is None for update in updates):  # Check if there’s no content
                return "暂无更新内容", []  # Return empty list if no updates
            
            # Convert to a list of dictionaries for Gradio Dataframe
            update_list = [
                {
                    "订阅URL": row[0],           # Subscription URL
                    "内容URL": row[1] or "N/A",  # Content URL (if exists)
                    "内容文本": row[2] or "N/A", # Content text (if exists)
                    "记录时间": row[3],          # Recorded timestamp
                    "状态": "已读" if row[4] == 1 else "未读"  # Status (read/unread)
                } for row in updates
            ]
            return "更新内容如下", pd.DataFrame(update_list)  # Return success message and data
        
        except sqlite3.Error as e:
            return f"数据库错误: {e}", []  # Return error message and empty list
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
# 创建 Gradio 界面
import gradio as gr

def create_interface():
    rec_system = RecommendationSystem()
    
    
    # region   测试时登录默认用户
    default_username = "zata"
    default_password = "zata"  # 你可以设置一个默认密码
    login_output, status_value, status_display_value = rec_system.login(default_username, default_password)
    print(f"默认登录用户 {default_username}: {login_output}")
    # endregion
    with gr.Blocks(title="推荐系统") as demo:
        gr.Markdown("# 欢迎使用推荐系统")

        # 状态显示
        status = gr.State(value="未登录")
        status_display = gr.Textbox(label="当前状态", value="未登录", interactive=False)

        # 注册界面
        with gr.Tab("注册"):
            reg_username = gr.Textbox(label="用户名")
            reg_password = gr.Textbox(label="密码", type="password")
            reg_output = gr.Textbox(label="结果")
            reg_button = gr.Button("注册")
            reg_button.click(
                fn=rec_system.register,
                inputs=[reg_username, reg_password],
                outputs=reg_output
            )

        # 登录界面
        with gr.Tab("登录"):
            login_username = gr.Textbox(label="用户名")
            login_password = gr.Textbox(label="密码", type="password")
            login_output = gr.Textbox(label="结果")
            login_button = gr.Button("登录")
            # Fixed: Removed _js and simplified outputs
            login_button.click(
                fn=rec_system.login,
                inputs=[login_username, login_password],
                outputs=[login_output, status, status_display]
            )

        # 添加订阅界面
        with gr.Tab("添加订阅列表"):
            sub_url = gr.Textbox(label="URL")
            sub_prompt = gr.Textbox(label="提示词")
            sub_output = gr.Textbox(label="结果")
            sub_button = gr.Button("添加订阅")
            sub_button.click(
                fn=rec_system.add_subscription,
                inputs=[sub_url, sub_prompt],
                outputs=sub_output
            )
        # 查看订阅界面
        with gr.Tab("查看订阅"):
            sub_status = gr.Textbox(label="状态")
            sub_table = gr.Dataframe(label="订阅列表", headers=["URL", "提示词", "创建时间"])
            sub_refresh_button = gr.Button("刷新")
            sub_refresh_button.click(
                fn=rec_system.get_subscriptions,
                inputs=None,  # No inputs needed
                outputs=[sub_status, sub_table]
            )
        # 查看订阅更新内容界面
        with gr.Tab("查看订阅更新内容"):
            update_status = gr.Textbox(label="状态")
            update_table = gr.Dataframe(
                label="更新内容列表",
                headers=["订阅URL", "内容URL", "内容文本", "记录时间", "状态"]
            )
            update_refresh_button = gr.Button("刷新")
            update_refresh_button.click(
                fn=rec_system.get_subscription_updates,
                inputs=None,
                outputs=[update_status, update_table]
            )

    return demo

# Launch the interface
if __name__ == "__main__":
    interface = create_interface()
    interface.launch()