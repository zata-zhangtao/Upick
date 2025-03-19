import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time

# 配置爬虫参数
START_URL = "https://www.aibase.com/zh/daily"  # 替换为你想爬取的起始URL
MAX_DEPTH = 1  # 最大爬取深度
OUTPUT_FILE = "crawled_data.json"  # 输出文件名

# 用于存储已访问的URL，避免重复
visited_urls = set()

# 用于存储爬取结果
crawled_data = []

def crawl(url, depth=0):
    # 检查深度限制和是否已访问
    if depth > MAX_DEPTH or url in visited_urls:
        return
    
    print(f"正在爬取: {url} (深度: {depth})")
    
    try:
        # 发送HTTP请求
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()  # 检查请求是否成功
        
        # 标记为已访问
        visited_urls.add(url)
        
        # 解析HTML内容
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 提取当前页面的标题作为主要内容（可以根据需要修改）
        page_title = soup.title.string if soup.title else "无标题"

        # 提取页面中的内容
        content = soup.get_text()
        
        # 存储当前页面的URL和内容
        crawled_data.append({
            "url": url,
            "title": page_title,
            "depth": depth,
            "content": content
        })
        
        # 提取页面中的所有链接
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            link_text = link.text.strip() or "无文本"
            
            # 将相对URL转换为绝对URL
            absolute_url = urljoin(url, href)
            
            # 简单过滤，只爬取http或https链接
            if absolute_url.startswith(("http://", "https://")):
                # 递归爬取新链接
                crawl(absolute_url, depth + 1)
                
        # 避免过于频繁请求，礼貌爬取
        time.sleep(1)
        
    except requests.RequestException as e:
        print(f"爬取 {url} 失败: {e}")
        
def save_to_file(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")

def main():
    print("开始爬取...")
    crawl(START_URL)
    save_to_file(crawled_data, OUTPUT_FILE)
    print(f"爬取完成，共爬取 {len(crawled_data)} 个页面")

if __name__ == "__main__":
    main()