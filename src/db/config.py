import os
from pathlib import Path

# 数据库路径
# 创建目录结构确保数据库文件可以被创建
db_dir = Path(__file__).resolve().parent / ".." / ".." / "resources" / "database"
os.makedirs(db_dir, exist_ok=True)
SUBSCRIPTIONS_DB_PATH = db_dir / "subscriptions.db"

# 确保路径是字符串格式，避免在某些环境下的路径解析问题
SUBSCRIPTIONS_DB_PATH = str(SUBSCRIPTIONS_DB_PATH)
