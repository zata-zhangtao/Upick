
# 阿里云

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
from src.log import get_logger
logger = get_logger("agent.llm")
load_dotenv()

def get_ali_llm(model="qwq-32b"):

    return ChatOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_BASE_URL"),
        model=model,
        streaming=True,
        # other params...
    )

try:
    ali_llm = get_ali_llm("qwq-32b")
    logger.info("阿里云模型连接成功")
except Exception as e:
    logger.error(f"阿里云模型连接失败: {e}")
    assert False, "阿里云模型连接失败"