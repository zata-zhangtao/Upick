
# 阿里云

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
load_dotenv()

def get_ali_llm(model="qwen-plus"):

    return ChatOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_BASE_URL"),
        model=model,
        # other params...
    )

try:
    ali_llm = get_ali_llm("qwen-7b-chat")
    print(ali_llm.invoke("现在是测试，你只需要回答：‘阿里云平台api连接成功’"))
except Exception as e:
    # print("阿里云模型连接失败")
    assert False, "阿里云模型连接失败"