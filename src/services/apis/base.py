"""
基础API客户端类
提供通用的API调用功能
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


from src.log import get_logger
logger = get_logger("services.apis.base")

class BaseAPIClient(ABC):
    """基础API客户端抽象类"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """
        初始化API客户端
        
        Args:
            base_url: API基础URL
            api_key: API密钥
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'UPick-API-Client/1.0'
        })
        
        if api_key:
            self.session.headers.update(self._get_auth_headers())


    def get_langcahin_llm_model(self, model_name):
        """
        获取LangChain LLM模型对象
        
        Args:
            model_name: 模型名称
            
        Returns:
            LangChain LLM对象，用于与语言模型进行交互
            
        Note:
            此方法应在子类中实现，返回对应提供商的LangChain LLM实例
        """
        # 这是一个抽象方法，子类应该重写此方法来返回具体的LangChain LLM对象
        # 例如: return ChatOpenAI(model=model_name, api_key=self.api_key)
        pass

    def get_langcahin_embedding_model(self, model_name):
        """
        获取LangChain Embedding模型对象
        
        Args:
            model_name: 模型名称
            
        Returns:
            LangChain Embedding对象，用于与Embedding模型进行交互
            
        Note:
            此方法应在子类中实现，返回对应提供商的LangChain Embedding实例
        """
        pass
    
   
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取认证请求头"""
        pass
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            **kwargs: 其他请求参数
            
        Returns:
            响应对象
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {method} {url} - {str(e)}")
            raise
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET请求"""
        response = self._make_request('GET', endpoint, params=params)
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict[str, Any]:
        """POST请求"""
        if files:
            # 文件上传时不设置Content-Type，让requests自动设置
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            response = self._make_request('POST', endpoint, data=data, files=files, headers=headers)
        else:
            response = self._make_request('POST', endpoint, json=data)
        return response.json()
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT请求"""
        response = self._make_request('PUT', endpoint, json=data)
        return response.json()
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE请求"""
        response = self._make_request('DELETE', endpoint)
        return response.json() if response.content else {} 