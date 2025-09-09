"""
路由管理模块

提供了 FastAPI 路由的统一返回格式和自动发现功能
"""

from .base import ApiResponse
from .discover import RoutesDiscover

__all__ = [
    "ApiResponse",
    "RoutesDiscover",
]
