# API接口模块

这个模块提供了统一的接口来调用各种外部API服务，目前主要支持DashScope（阿里云）的语音合成等功能。

## 目录结构

```
src/services/apis/
├── __init__.py          # 模块初始化，导出BaseAPIClient和DashScopeAPIClient
├── base.py             # 基础API客户端抽象类
├── dashscope.py        # DashScope API客户端实现
├── functions.py        # 常用功能函数（语音合成等）
└── README.md           # 说明文档
```

## 功能特性

### 🎤 语音合成服务

目前支持的服务提供商：
- **DashScope (阿里云灵积)** - 支持CosyVoice语音合成模型

功能：
- 文本转语音 (TTS)
- 多种音色选择
- 支持自定义模型

### 🏗️ 基础架构

- **BaseAPIClient** - 抽象基类，提供通用的API调用功能
- **统一接口设计** - 便于扩展其他API提供商
- **LangChain集成** - 预留了LangChain LLM和Embedding模型接口

## 快速开始


### 设置环境变量

你可以选择放入环境变量或者创建一个.env文件
```bash
# DashScope API密钥
export DASH_SCOPE_API_KEY="your_dashscope_api_key"
```

### 使用示例

#### 语音合成（推荐方式）

```python
from src.services.apis.functions import speech_synthesis

# 使用默认配置进行语音合成
audio_data = speech_synthesis("你好，这是语音合成测试")

# 自定义音色和模型
audio_data = speech_synthesis(
    text="你好，这是语音合成测试",
    voice="longxiaochun",
    model_name="cosyvoice-v1",
    provider="dashscope"
)

# 保存音频文件
with open("output.mp3", "wb") as f:
    f.write(audio_data)
```

## API参考

### BaseAPIClient

基础API客户端抽象类，提供通用的HTTP请求功能。

#### 初始化参数
- `base_url`: API基础URL
- `api_key`: API密钥（可选）
- `timeout`: 请求超时时间，默认30秒

#### 主要方法
- `get(endpoint, params)`: 发送GET请求
- `post(endpoint, data, files)`: 发送POST请求
- `put(endpoint, data)`: 发送PUT请求
- `delete(endpoint)`: 发送DELETE请求
- `get_langcahin_llm_model(model_name)`: 获取LangChain LLM模型（抽象方法）
- `get_langcahin_embedding_model(model_name)`: 获取LangChain Embedding模型（抽象方法）

### DashScopeAPIClient

DashScope API客户端，继承自BaseAPIClient。

#### 初始化参数
- `base_url`: 默认为"https://api.dashscope.com/v1"
- `api_key`: 默认从环境变量`DASH_SCOPE_API_KEY`获取
- `timeout`: 请求超时时间，默认30秒

#### 主要方法
- `get_speech_synthesis_model(model_name, voice)`: 获取语音合成模型
  - `model_name`: 模型名称，默认"cosyvoice-v1"
  - `voice`: 音色，默认"longxiaochun"

### 功能函数

#### speech_synthesis

语音合成功能函数，提供简化的调用接口。

```python
def speech_synthesis(
    text: str, 
    voice: Optional[str] = None, 
    model_name: Optional[str] = None, 
    provider: Optional[str] = "dashscope"
) -> bytes
```

**参数：**
- `text`: 要合成的文本
- `voice`: 音色（可选）
- `model_name`: 模型名称（可选）
- `provider`: 服务提供商，目前支持"dashscope"

**返回：**
- 音频数据（bytes格式）

## 支持的服务

### 语音合成

| 提供商 | 模型 | 音色 | 状态 |
|--------|------|------|------|
| DashScope | cosyvoice-v1/cosyvoice-v2/Sambert | longxiaochun/[具体参考](https://help.aliyun.com/zh/model-studio/cosyvoice-large-model-for-speech-synthesis/?spm=a2c4g.11186623.0.i25) | ✅ 已实现 |




## 扩展新的API提供商

要添加新的API提供商，请：

1. 继承`BaseAPIClient`类
3. 实现具体的API调用方法
4. 可选：实现LangChain模型获取方法
5. 在`__init__.py`中导出新的客户端类

示例：

```python
from .base import BaseAPIClient

class NewProviderAPIClient(BaseAPIClient):
    def _get_auth_headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}
    
    def get_langcahin_llm_model(self, model_name):
        # 实现具体的LangChain LLM模型获取逻辑
        pass
```

## 注意事项

1. **API密钥安全**: 请妥善保管API密钥，建议使用环境变量
2. **网络超时**: 默认超时时间为30秒，可根据需要调整
3. **依赖管理**: 确保安装了必要的依赖包（requests, dashscope）
4. **日志记录**: 模块使用统一的日志系统记录API调用信息
5. **扩展性**: 基于抽象基类设计，便于扩展新的API提供商

## 许可证

本模块遵循项目的整体许可证。 