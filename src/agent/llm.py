
# 阿里云

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
# from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatZhipuAI
import os
import os
from dotenv import load_dotenv
import yaml
from src.log import get_logger
logger = get_logger("agent.llm")
load_dotenv()




ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

yaml_path = os.path.join(ROOT_DIR, "config.yaml")

with open(yaml_path, "r", encoding="utf-8") as file:
    config_data = yaml.safe_load(file)

def get_ali_llm(model, base_url):
    """
    获取阿里云的LLM模型
    Args:
        model: 模型名称
    Returns:
        ChatOpenAI: 阿里云的LLM模型
    """

    return ChatOpenAI(
        api_key=os.getenv("API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1" if base_url is None else base_url,
        model=model,
        streaming=True,
        # other params...
    )

# try:
#     ali_llm = get_ali_llm(model=config_data["app"]["model"])
#     logger.info(f"阿里云模型连接成功: {config_data['app']['model']}")
# except Exception as e:
#     logger.error(f"阿里云模型连接失败: {e}")
#     assert False, "阿里云模型连接失败"





def get_zhipu_llm(model, base_url):
    """
    获取智谱的LLM模型
    Args:
        model: 模型名称
    Returns:
        ChatOpenAI: 智谱的LLM模型
    """
    return ChatZhipuAI(
        api_key=os.getenv("API_KEY"),
        base_url="https://open.bigmodel.cn/api/paas/v4/chat/completions" if base_url is None else base_url,
        model=model,
        streaming=True,
    )



