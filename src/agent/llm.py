
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

ali_llm = get_ali_llm("qwen-7b-chat")
print(ali_llm.invoke("2025年的技术趋势是什么？"))