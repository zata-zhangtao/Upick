import requests
import sqlite3
import hashlib
from urllib.parse import urlparse
from bs4 import BeautifulSoup  # 添加BeautifulSoup来清理HTML
import datetime


# region 爬虫函数，传入url，返回内容
def fetch_and_clean_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Failed to retrieve the page. Status code: {response.status_code}"

        # 自动检测编码
        response.encoding = response.apparent_encoding
        raw_html = response.text

        soup = BeautifulSoup(raw_html, 'html.parser')
        for style_tag in soup.find_all('style'):
            style_tag.extract()
        for script_tag in soup.find_all('script'):
            script_tag.extract()
        for tag in soup.find_all():
            if 'style' in tag.attrs:
                del tag['style']

        clean_text = soup.get_text(separator='\n').strip()
        lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
        clean_text = '\n'.join(lines)

        return clean_text

    except Exception as e:
        return False

# endregion


















class WebCrawler:
    def __init__(self, username, db_path=r'data\recommendation_system.db'):
        """初始化爬虫类"""
        self.username = username
        self.db_path = db_path
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def clean_content(self, raw_html):
        """清理HTML内容，移除标签并保留纯文本
        
        Args:
            raw_html (str): 原始HTML内容
            
        Returns:
            str: 清理后的纯文本
        """
        if not raw_html:
            return ""
            
        # 使用BeautifulSoup解析HTML并提取文本
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # 移除脚本和样式元素
        for element in soup(['script', 'style']):
            element.decompose()
            
        # 获取纯文本
        text = soup.get_text()
        
        # 清理多余的空白
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

    def crawl_raw_content(self, url):
        """爬取网页的原始内容并生成对比文件
        
        Args:
            url (str): 要爬取的网页URL
            
        Returns:
            tuple: (原始内容, 清理后内容)，如果失败返回(None, None)
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            raw_content = response.text
            
            # 清理内容
            clean_content = self.clean_content(raw_content)
            
            # 生成对比文件
            # with open('content_comparison.txt', 'w', encoding='utf-8') as f:
            #     f.write("=== 原始内容 (前1000字符) ===\n")
            #     f.write(raw_content[:10000] + "\n\n")
            #     f.write("=== 清理后内容 (前1000字符) ===\n")
            #     f.write(clean_content[:10000] + "\n")
            
            # print("已生成对比文件：content_comparison.txt")
            return clean_content
            
        except requests.exceptions.RequestException as e:
            print(f"爬取 {url} 失败: {str(e)}")
            return  None

    def save_to_db(self, subscription_id, url, content, clean_content):
        """将爬取的内容保存到数据库"""
        if not content or not clean_content:
            return False

        content_hash = hashlib.md5(clean_content.encode()).hexdigest()

        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('SELECT id FROM content_history WHERE content_hash = ? AND subscription_id = ?',
                     (content_hash, subscription_id))
            if c.fetchone():
                print(f"内容已存在: {url}")
                return False

            c.execute('''INSERT INTO content_history 
                        (subscription_id, content_hash, content_text, content_url, status) 
                        VALUES (?, ?, ?, ?, ?)''',
                     (subscription_id, content_hash, clean_content, url, 0))
            
            conn.commit()
            print(f"内容已保存: {url}")
            return True
            
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            return False
            
        finally:
            conn.close()

    def crawl_and_store(self, url, subscription_id):
        """爬取网页并存储到数据库"""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                print("无效的URL格式")
                return False
        except ValueError:
            print("无效的URL格式")
            return False

        raw_content, clean_content = self.crawl_raw_content(url)
        if clean_content:
            return self.save_to_db(subscription_id, url, raw_content, clean_content)
        return False

if __name__ == "__main__":
    test_url = "https://www.dmla7.com/type/ribendongman.html"
    
    # conn = sqlite3.connect(r'data\recommendation_system.db')
    # c = conn.cursor()
    # c.execute('SELECT id FROM subscriptions WHERE url = ?', (test_url,))
    # subscription_id = c.fetchone()[0]
    # conn.close()
    
    crawler = WebCrawler("test_user")
    crawler.crawl_raw_content(test_url)