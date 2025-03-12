from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from  langchain_community.llms import OpenAI
import os

# 配置 API Key 和 Base URL
api_key = "sk-d714022a9df74f97983fb3e072ca6e47"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 初始化 LangChain 的 ChatOpenAI 模型
# llm = ChatOpenAI(
#     model="qwq-32b",  # 指定模型名称
#     api_key=api_key,
#     base_url=base_url,
#     streaming=True,   # 启用流式输出
# )

llm = OpenAI(api_key=api_key, base_url=base_url,model="qwq-32b",  streaming=True,)

# 定义用户的消息
messages = [HumanMessage(content="9.9和9.11谁大")]

# 调用模型并处理流式输出
print("\n" + "=" * 20 + "模型输出" + "=" * 20 + "\n")
response = llm.stream(messages)

# 流式打印输出
for chunk in response:
    print(chunk.content, end='', flush=True)

print("\n" + "=" * 20 + "输出结束" + "=" * 20 + "\n")