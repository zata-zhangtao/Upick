"""
provide some functions, including speech synthesis, speech recognition, etc.
提供一些常用的功能，包括语音合成、语音识别
"""

import requests
from .dashscope import DashScopeAPIClient
from typing import Optional
def speech_synthesis(text: str, voice: Optional[str] = None, model_name: Optional[str] = None, provider: Optional[str] = "dashscope"):
    """
    语音合成,传入文本\提供商\音色，返回语音数据

    Args:
        text: 文本
        voice: 音色，可选参数
        model_name: 模型名称，可选参数
        provider: 提供商

    Returns:
        audio: 语音数据 
        
    """

    # 初始化参数
    kwargs = {}
    if voice is not None:
        kwargs['voice'] = voice
    if model_name is not None:
        kwargs['model_name'] = model_name



    # region 处理DashScope的语音合成
    try:
        if provider == "dashscope":
            dashscope_client = DashScopeAPIClient()
            # 只传入非None的参数给get_speech_synthesis_model
            synthesizer = dashscope_client.get_speech_synthesis_model(**kwargs)
            audio = synthesizer.call(text)
            # with open('output.mp3', 'wb') as f:
                # f.write(audio)
            return audio
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}") 
    except Exception as e:
        print(f"其他错误: {e}")



        
    # endregion
