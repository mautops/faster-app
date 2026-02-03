"""
Faster APP - A lightweight Python web framework built on FastAPI.

Faster APP provides Django-style project structure and conventions for FastAPI,
including automatic discovery of routes, models, commands, and middleware.

Core Features:
    - Auto-discovery of routes, models, commands, and middleware
    - Base model classes (UUIDModel, DateTimeModel, StatusModel, ScopeModel)
    - Django-style command-line interface
    - Standardized API responses
    - Convention over configuration approach

Example:
    >>> from faster_app import UUIDModel, DateTimeModel
    >>> from faster_app import ApiResponse
    >>> from faster_app import BaseCommand

Author: peizhenfei
Email: peizhenfei@hotmail.com
License: MIT
"""

__version__ = "0.1.9"
__author__ = "peizhenfei"
__email__ = "peizhenfei@hotmail.com"

# 导出主要的类和函数
from faster_app.commands.base import BaseCommand
from faster_app.commands.discover import CommandDiscover
from faster_app.models.base import (
    DateTimeModel,
    ScopeModel,
    StatusModel,
    UUIDModel,
)

# 导出发现器
from faster_app.models.discover import ModelDiscover
from faster_app.routes.base import ApiResponse
from faster_app.routes.discover import RoutesDiscover

# 导出配置
from faster_app.settings.builtins.settings import DefaultSettings
from faster_app.utils.discover import BaseDiscover

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # 基础类
    "BaseDiscover",
    "BaseCommand",
    "ApiResponse",
    # 模型基类
    "UUIDModel",
    "DateTimeModel",
    "StatusModel",
    "ScopeModel",
    # 发现器
    "ModelDiscover",
    "CommandDiscover",
    "RoutesDiscover",
    # 配置
    "DefaultSettings",
]
