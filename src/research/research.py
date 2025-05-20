import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from src.crawler import WebCrawler
from typing import Dict, List, Optional, Any

def search_and_list_results_tavily(api_key: str, query: str, num_results: int = 5, time_range: str = 'day', exclude_domains: List[str] = [], **kwargs) -> Dict[str, Any]:
    """
    使用 Tavily API 进行搜索，并返回结构化的搜索结果。
    
    Args:
        api_key: Tavily API密钥
        query: 搜索查询
        num_results: 返回结果数量
        time_range: 时间范围
        exclude_domains: 要排除的域名列表
        **kwargs: 其他Tavily API参数
        
    Returns:
        Dict包含:
        - success: bool 表示是否成功
        - error: str 错误信息(如果有)
        - answer: str Tavily的总结性回答
        - results: List[Dict] 搜索结果列表
    """
    if not api_key:
        return {
            "success": False,
            "error": "请在代码中设置 TAVILY_API_KEY，或设置 TAVILY_API_KEY 环境变量。\n你需要前往 https://tavily.com/ 注册并获取你的 API 密钥。"
        }
    if not query:
        return {
            "success": False,
            "error": "请输入你要搜索的关键字。"
        }

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            search_depth="basic",
            include_answer=True,
            max_results=num_results,
            time_range=time_range,
            exclude_domains=exclude_domains,
        )
        
        results = []
        if "results" in response and response["results"]:
            for result in response["results"]:
                title = result.get("title", "N/A")
                link = result.get("url", "N/A")
                tavily_content = result.get("content", "N/A")
                raw_content = result.get("raw_content", None)
                
                result_data = {
                    "title": title,
                    "url": link,
                    "content": tavily_content,
                }
                
                if raw_content:
                    result_data["raw_content"] = raw_content
                elif link and link != "N/A":
                    try:
                        page_content = WebCrawler().fetch_and_clean_content(link)
                        result_data["page_content"] = page_content
                    except Exception as e:
                        result_data["page_content_error"] = str(e)
                
                results.append(result_data)

        return {
            "success": True,
            "answer": response.get("answer", ""),
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"执行 Tavily 搜索时发生错误: {str(e)}"
        }

if __name__ == "__main__":
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    keyword = input("请输入你要搜索的关键字: ")
    if keyword:
        results = search_and_list_results_tavily(api_key=TAVILY_API_KEY, query=keyword, num_results=3, time_range='day')
        if not results["success"]:
            print(f"错误: {results['error']}")
        else:
            if results["answer"]:
                print(f"\nTavily 总结性回答:\n{results['answer']}\n")
            for i, result in enumerate(results["results"], 1):
                print(f"\n结果 {i}:")
                print(f"标题: {result['title']}")
                print(f"链接: {result['url']}")
                print(f"内容: {result['content']}")
                if "page_content" in result:
                    print(f"页面内容: {result['page_content'][:1000]}...")
    else:
        print("关键字不能为空。")