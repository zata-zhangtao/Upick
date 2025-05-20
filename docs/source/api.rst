API Reference
=============

Search Functions
--------------

.. automodule:: src.research.research
   :members:
   :undoc-members:
   :show-inheritance:

get_page_content
~~~~~~~~~~~~~~~

.. autofunction:: src.research.research.get_page_content

search_and_list_results_tavily
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: src.research.research.search_and_list_results_tavily

Usage Examples
-------------

Basic Search
~~~~~~~~~~~

.. code-block:: python

    from src.research.research import search_and_list_results_tavily
    import os

    # 从环境变量获取API密钥
    api_key = os.getenv("TAVILY_API_KEY")
    
    # 执行搜索
    search_and_list_results_tavily(
        api_key=api_key,
        query="Python programming",
        num_results=3,
        time_range='day'
    )

Advanced Search
~~~~~~~~~~~~~~

.. code-block:: python

    from src.research.research import search_and_list_results_tavily
    import os

    # 从环境变量获取API密钥
    api_key = os.getenv("TAVILY_API_KEY")
    
    # 执行高级搜索
    search_and_list_results_tavily(
        api_key=api_key,
        query="Machine learning news",
        num_results=5,
        time_range='week',
        exclude_domains=['example.com', 'test.com']
    )

Parameters
---------

search_and_list_results_tavily
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **api_key** (str): Tavily API密钥
* **query** (str): 搜索查询字符串
* **num_results** (int, optional): 返回结果数量，默认为5
* **time_range** (str, optional): 搜索时间范围，可选值：'day', 'week', 'month', 'year'，默认为'day'
* **exclude_domains** (list, optional): 要排除的域名列表，默认为空列表

get_page_content
~~~~~~~~~~~~~~~

* **url** (str): 要获取内容的网页URL

Returns
-------

search_and_list_results_tavily
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

该函数会打印搜索结果，包括：
* Tavily的总结性回答（如果有）
* 每个搜索结果的标题、链接和内容摘要
* 原始页面内容（如果可用）

get_page_content
~~~~~~~~~~~~~~~

* 返回网页的文本内容（最多2000字符）
* 如果发生错误，返回错误信息字符串 