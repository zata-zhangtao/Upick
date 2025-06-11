import os
from typing import Optional
from .base import BaseAPIClient
from src.log import get_logger
import dashscope
from dashscope.audio.tts_v2 import *
logger = get_logger("services.apis.dashscope")

class DashScopeAPIClient(BaseAPIClient):
    """DashScope API客户端"""
    
    def __init__(self, base_url: str = "https://api.dashscope.com/v1", api_key: Optional[str] = os.getenv("DASH_SCOPE_API_KEY"), timeout: int = 30):
        super().__init__(base_url, api_key, timeout)


    def get_langcahin_llm_model(self, model_name):
        """
        获取LangChain LLM模型对象
        """
        pass

    def get_langcahin_embedding_model(self, model_name):
        """
        获取LangChain Embedding模型对象
        """
        pass

    def get_speech_synthesis_model(self, model_name="cosyvoice-v1",voice="longxiaochun"):
        """
        获取语音合成模型对象

        Args:
            model_name: 模型名称
            voice: 语音类型，指是音色

        Returns:
            audio: 语音数据

        """
        synthesizer = SpeechSynthesizer(model=model_name, voice=voice)
        return synthesizer

        