"""
API接口模块
包含各种外部API的调用接口
"""

from .base import BaseAPIClient
from .dashscope import DashScopeAPIClient

__all__ = [
    "BaseAPIClient",
    "DashScopeAPIClient"
] 