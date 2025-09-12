"""
Faster APP - 一个轻量级的 Python Web 框架

提供了以下核心功能：
- 自动发现和加载模块 (DiscoverBase)
- 数据库模型基类 (UUIDModel, DateTimeModel, StatusModel, ScopeModel)
- 命令行工具基类 (BaseCommand)
- 路由管理 (ApiResponse)
"""

__version__ = "0.0.17"
__author__ = "peizhenfei"
__email__ = "peizhenfei@hotmail.com"

# 导出主要的类和函数
from faster_app.utils.discover import DiscoverBase
from faster_app.models.base import (
    UUIDModel,
    DateTimeModel,
    StatusModel,
    ScopeModel,
)
from faster_app.commands.base import BaseCommand
from faster_app.routes.base import ApiResponse

# 导出发现器
from faster_app.models.discover import ModelDiscover
from faster_app.commands.discover import CommandDiscover
from faster_app.routes.discover import RoutesDiscover

# 导出配置
from faster_app.settings.builtins.settings import DefaultSettings

__all__ = [
    # 基础类
    "DiscoverBase",
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
