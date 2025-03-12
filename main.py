from src.services import RecommendationSystem
from src.services import create_interface
from src.data_processing import WebCrawler
import sqlite3
from flask import Flask
from src.services.crawler_api import crawler_api

def create_app():
    app = Flask(__name__, static_folder='src/pages', static_url_path='')
    app.register_blueprint(crawler_api)
    return app

if __name__ == "__main__":
    # Start the Flask application
    app = create_app()
    app.run(debug=True, port=5000)
    
    # Uncomment to use the original interface
    # interface = create_interface()
    # interface.launch()


# if __name__ == "__main__":
#     # # 假设这是RecommendationSystem类的实例
#     rec_system = RecommendationSystem()
#     rec_system.run()
        
    # # # 注册并登录测试用户
    # rec_system.register("test_user", "password123")
    # rec_system.login("test_user", "password123")
    
    # # # 添加测试订阅
    # test_url = "https://www.dmla7.com/type/ribendongman.html"
    # rec_system.add_subscription(test_url, "test prompt")
    
    # # 获取订阅ID（这里简化处理，实际应从数据库查询）
    # conn = sqlite3.connect(r'data\recommendation_system.db')
    # c = conn.cursor()
    # c.execute('SELECT id FROM subscriptions WHERE url = ?', (test_url,))
    # subscription_id = c.fetchone()[0]
    # conn.close()
    
    # # 创建爬虫实例并使用
    # crawler = WebCrawler("test_user")
    # crawler.crawl_and_store(test_url, subscription_id)