import requests
from bs4 import BeautifulSoup

class WebCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

    def detect_encoding(self, response, content):
        """Detect the encoding of the webpage content"""
        if 'charset' in response.headers.get('content-type', '').lower():
            return response.apparent_encoding
        
        soup = BeautifulSoup(content, 'html.parser')
        meta_charset = soup.find('meta', charset=True)
        meta_content = soup.find('meta', {'http-equiv': 'Content-Type'})
        
        if meta_charset:
            return meta_charset.get('charset')
        elif meta_content and 'charset' in meta_content.get('content', '').lower():
            return meta_content.get('content').lower().split('charset=')[-1]
        
        # Try common encodings
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030']
        for encoding in encodings:
            try:
                content.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue
        return response.apparent_encoding

    def clean_html(self, soup):
        """Clean HTML content by removing unwanted elements and attributes"""
        for tag in soup.find_all(['style', 'script']):
            tag.decompose()
            
        for tag in soup.find_all():
            if 'style' in tag.attrs:
                del tag['style']
        
        text = soup.get_text(separator='\n').strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n'.join(lines)

    def fetch_and_clean_content(self, url):
        """Fetch webpage content and clean it"""
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                return f"Failed to retrieve the page. Status code: {response.status_code}"

            encoding = self.detect_encoding(response, response.content)
            response.encoding = encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            clean_text = self.clean_html(soup)
            
            return clean_text

        except Exception as e:
            return f"Error: {e}"
        

if __name__ == "__main__":
    crawler = WebCrawler()
    url = "https://www.aibase.com/zh/daily"
    print(crawler.fetch_and_clean_content(url))
