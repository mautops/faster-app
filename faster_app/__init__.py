"""
Faster API - 一个轻量级的 Python Web 框架

提供了以下核心功能：
- 自动发现和加载模块 (DiscoverBase)
- 数据库模型基类 (UUIDModel, DateTimeModel, StatusModel, ScopeModel)
- 命令行工具基类 (CommandBase)
- 路由管理 (ApiResponse)
- 数据库连接管理 (tortoise_init)
"""

__version__ = "0.0.1"
__author__ = "peizhenfei"
__email__ = "peizhenfei@hotmail.com"

# 导出主要的类和函数
from faster_app.base import DiscoverBase
from faster_app.models.base import (
    UUIDModel,
    DateTimeModel,
    StatusModel,
    ScopeModel,
    SyncTimeModel,
    SyncCrontabModel,
)
from faster_app.commands.base import CommandBase, with_db_init
from faster_app.routes.base import ApiResponse
from faster_app.db import tortoise_init

# 导出发现器
from faster_app.models.discover import ModelDiscover
from faster_app.commands.discover import CommandDiscover
from faster_app.routes.discover import RoutesDiscover

# 导出配置
from faster_app.settings.builtins.settings import DefaultSettings

__all__ = [
    # 基础类
    "DiscoverBase",
    "CommandBase",
    "with_db_init",
    "ApiResponse",
    "tortoise_init",
    # 模型基类
    "UUIDModel",
    "DateTimeModel",
    "StatusModel",
    "ScopeModel",
    "SyncTimeModel",
    "SyncCrontabModel",
    # 发现器
    "ModelDiscover",
    "CommandDiscover",
    "RoutesDiscover",
    # 配置
    "DefaultSettings",
]
