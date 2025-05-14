一个多功能网络爬虫框架，用于从各种来源提取结构化数据。

## 概述

爬虫模块提供了一个灵活且可扩展的框架，用于爬取和提取不同网站的数据。它包括针对 ArXiv 和 IEEE 等学术源的专用爬虫，以及适用于任何网站的通用网络爬虫。

- 在__init__.py文件中添加了默认注册

## 功能特点

- **模块化架构**：基础爬虫类与专用实现
- **爬虫注册系统**：基于 URL 模式匹配的自动爬虫选择
- **内置专用爬虫**：
  - ArXiv 爬虫：从 ArXiv 提取学术论文
  - IEEE 爬虫：从 IEEE 网站提取论文
  - Web 爬虫：适用于任何网站的通用爬虫
- **弹性爬取**：自动重试与指数退避机制
- **清洁内容提取**：HTML 清理和文本提取功能
- **命令行界面**：易于使用的 CLI 接口，便于快速爬取任务

## 组件

### 基础爬虫

`BaseCrawler` 是一个抽象基类，定义了所有专用爬虫的通用接口和实用方法。它提供：

- 带错误处理的页面获取
- 由专用爬虫实现的抽象爬取方法
- 数据保存功能

### 爬虫注册系统

注册系统允许基于 URL 模式自动选择适当的爬虫：

- 使用 URL 正则表达式模式注册爬虫
- 自动为给定 URL 选择正确的爬虫
- 当没有匹配的专用爬虫时，回退到通用网络爬虫

### 专用爬虫

- **ArxivCrawler**：从 ArXiv 提取论文、作者、摘要和其他元数据
- **IEEECrawler**：从 IEEE 网站提取论文、作者和元数据
- **WebCrawler**：通用爬虫，具有：
  - HTML 清理
  - 文本提取
  - 链接保留
  - 编码检测

### 实用工具

帮助函数，用于：
- 带指数退避的重试机制
- 目录管理
- 结果合并
- 时间戳生成

## 使用方法

### 命令行界面

该模块提供了简单的命令行界面：

```bash
# 爬取 ArXiv（默认）
python -m src.crawler.cli

# 爬取特定 URL
python -m src.crawler.cli --url https://arxiv.org/list/cs.AI/recent

# 爬取 IEEE
python -m src.crawler.cli --source ieee

# 仅从网页提取文本
python -m src.crawler.cli --source web --url https://example.com --text-only

# 指定输出文件
python -m src.crawler.cli --output results.json
```

### Python API

```python
from src.crawler import ArxivCrawler, WebCrawler, registry

# 使用专用爬虫
arxiv_crawler = ArxivCrawler()
papers = arxiv_crawler.crawl("https://arxiv.org/list/cs.AI/recent")

# 使用网络爬虫
web_crawler = WebCrawler()
content = web_crawler.fetch_and_clean_content("https://example.com")

# 使用注册系统自动选择爬虫
url = "https://arxiv.org/abs/2104.13478"
crawler_class = registry.get_crawler(url)
if crawler_class:
    crawler = crawler_class()
    result = crawler.crawl(url)
```

## 扩展

要添加新的专用爬虫：

1. 创建一个继承自 `BaseCrawler` 的新爬虫类
2. 实现 `crawl` 方法
3. 在注册系统中注册爬虫：

```python
from src.crawler import registry
from .my_crawler import MyCrawler

registry.register(r'https?://example\.com/.*', MyCrawler)
```
