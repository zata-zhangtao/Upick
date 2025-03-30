import sqlite3

SUBSCRIPTIONS_DB_PATH = "/Users/zata/code/Upick/resources/database/subscriptions.db"

def get_stats():
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH) # connect to database  连接数据库
    c = conn.cursor()
    
    # Get paper count  获取论文数量
    c.execute("SELECT COUNT(*) FROM arxiv_papers")
    paper_count = c.fetchone()[0]

    print(f"paper_count: {paper_count}")
    
    # Get category count  获取类别数量
    c.execute("SELECT COUNT(*) FROM arxiv_categories")
    category_count = c.fetchone()[0]
    
    # Get latest paper date  获取最新论文日期
    c.execute("SELECT MAX(fetched_at) FROM arxiv_papers")
    latest_date = c.fetchone()[0] or "No papers"
    
    conn.close()
    
    return paper_count, category_count, latest_date

if __name__ == "__main__":
    print(get_stats())
