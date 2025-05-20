Welcome to FaintGleam Research API's documentation!
==============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

Introduction
------------

FaintGleam Research API 是一个强大的网络搜索和内容抓取工具，它结合了 Tavily API 的强大搜索能力和自定义的内容抓取功能。这个工具可以帮助你：

* 使用 Tavily API 进行智能网络搜索
* 获取搜索结果的相关内容摘要
* 自动抓取和解析网页内容
* 提供结构化的搜索结果

Installation
------------

你可以通过 pip 安装所需的依赖：

.. code-block:: bash

   pip install -r requirements.txt

Configuration
-------------

在使用之前，你需要设置 Tavily API 密钥。你可以通过以下两种方式之一来设置：

1. 环境变量：
   .. code-block:: bash

      export TAVILY_API_KEY='your-api-key-here'

2. 直接在代码中设置：
   .. code-block:: python

      TAVILY_API_KEY = 'your-api-key-here'

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 