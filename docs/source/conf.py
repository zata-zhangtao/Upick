# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))  # 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('../../src/'))  # 添加src目录到路径


project = 'fainitgleam'
copyright = '2025, zata'
author = 'zata'
release = '1.3.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = [
    'sphinx.ext.autodoc',      # 自动从docstrings生成文档
    'sphinx.ext.viewcode',     # 添加查看源码的链接
    'sphinx.ext.napoleon',     # 支持Google风格的文档字符串
]

# 配置autodoc扩展
autodoc_member_order = 'bysource'  # 按源码顺序记录成员
add_module_names = False  # 不在API文档中添加模块名

templates_path = ['_templates']
exclude_patterns = []

language = 'zh'


html_theme = 'sphinx_rtd_theme'  # 使用ReadTheDocs主题
html_static_path = ['_static']
