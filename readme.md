# 具有增量学习能力的订阅管理器

这个应用提供了一个订阅管理系统，具有增量学习能力，可以生成高质量的内容摘要。

## 功能特点

### 订阅管理
- 添加和跟踪内容订阅
- 根据时间间隔自动刷新内容
- 生成内容变更的摘要

### 增量学习系统
- 收集用户对生成摘要的反馈
- 利用反馈改进未来的摘要
- 在生成新摘要时优先考虑高质量的示例
- 可视化学习性能

## 工作原理

该系统结合使用了：

1. **内容跟踪**：监控订阅内容的变化
2. **自然语言处理**：生成重要变更的摘要
3. **增量学习**：基于反馈随时间改进摘要质量
4. **TF-IDF向量化**：寻找相似示例以指导摘要生成
5. **反馈循环**：允许用户对摘要进行评分并持续改进质量

## 模块

- `src/agent/summary.py`：主要的摘要生成代理
- `src/agent/incremental_learning.py`：增量学习系统
- `src/db`：用于存储订阅、内容和反馈的数据库函数
- `src/pages/gradio_page.py`：管理系统的Web界面

## 使用说明

应用程序提供了Gradio Web界面，包含以下标签页：

1. **添加/刷新**：添加新订阅或刷新现有订阅
2. **更新**：查看内容更新并对摘要提供反馈
3. **学习统计**：查看学习统计数据和性能指标
4. **计划设置**：配置自动刷新计划
5. **配置**：设置应用程序配置

## 反馈系统

反馈系统是一个关键组件，它：

1. 允许用户对摘要进行0.0到1.0的评分
2. 存储带有摘要和反馈的原始内容
3. 使用高评分示例（0.8+）来指导未来的摘要
4. 自动构建有效摘要模式的知识库


<h2 id="install">安装使用</h2>

### conda安装

进入项目路径，然后使用一些命令进行安装(需要提前安装conda, 3.10 <= python version <= 3.12)
```bash
conda create -n Upick python=3.11

conda activate Upick

# 跳过安装失败的依赖，使用清华源
while read requirement; do
    pip install "$requirement" -i https://pypi.tuna.tsinghua.edu.cn/simple || echo "Failed to install $requirement, continuing..."
done < requirements.txt

python run.py
```

### uv安装

```sh
pip install uv 
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
while read requirement; do
    uv pip install "$requirement" -i https://pypi.tuna.tsinghua.edu.cn/simple || echo "Failed to install $requirement, continuing..."
done < requirements.txt
python run.py
```

### windows exe安装

### 使用建议

1. 如果使用智谱AI免费模型，建议使用GLM-Z1-Flash，其他的几个我试了，几乎处于不可用状态
2. 如果配置文件yaml中想要设置为None，直接空着就行，如果填None反而是字符串的'None'
3. 通过如下命令创建并打开api文档 (linux/mac)
    ```bash
    cd docs/
    make html 
    open build/html/index.html
    ```