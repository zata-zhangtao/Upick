from src.services import RecommendationSystem
from src.data_processing import WebCrawler
import sqlite3


if __name__ == "__main__":
    # # 假设这是RecommendationSystem类的实例
    rec_system = RecommendationSystem()
    rec_system.run()
        
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