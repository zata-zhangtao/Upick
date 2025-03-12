from typing import List
from src.data_processing import WebCrawler

class User:

    
    def __init__(self, user_id):
        self.user_id = user_id
        self.crawler = WebCrawler()
        self.subscriptions = [
            {
                "url": "https://www.zhihu.com/hot",
                "prompt": "知乎热榜"
            },
            {
                "url": "https://www.aibase.com/zh/daily",
                "prompt": "AI每日新闻"
            }
        ]


    def add_subscription(self, url, prompt):
        '''
        添加用户订阅的网站
        '''
        return f"用户名: {self.user_id}"
    
    def remove_subscription(self, url):
        '''
        删除用户订阅的网站
        '''
        return f"用户名: {self.user_id}"

    
    def get_subscription(self):
        '''
        获取用户订阅的网站
        '''
        return f"用户名: {self.user_id}"
    
    def get_subscription_updates(self):
        '''
        获取用户订阅的网站更新
        '''
        return f"用户名: {self.user_id}"
    


    def get_content_of_subscription(self)->List[dict[str,str]]:
        '''
        获取用户订阅的网站内容
        '''
        content_list = []
        for subscription in self.subscriptions:
            # 使用爬虫
            content = self.crawler.crawl_raw_content(subscription["url"])
            content_list.append({"url":subscription["url"],"content":content})
        return content_list
    
    def get_summary(self)->str:
        '''
        获取用户订阅的网站总结,所有网站的总结
        '''
        return f"用户名: {self.user_id}"
    

    
    
