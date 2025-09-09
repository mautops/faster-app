"""
数据库模型模块

提供了基于 Tortoise ORM 的模型基类和自动发现功能
"""

from .base import (
    UUIDModel,
    DateTimeModel,
    StatusModel,
    ScopeModel,
)
from .discover import ModelDiscover

__all__ = [
    "UUIDModel",
    "DateTimeModel",
    "StatusModel",
    "ScopeModel",
    "ModelDiscover",
]
