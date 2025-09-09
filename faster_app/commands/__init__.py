"""
命令行工具模块

提供了基于 Fire 的命令行工具基类和自动发现功能
"""

from .base import CommandBase, with_db_init
from .discover import CommandDiscover

__all__ = [
    "CommandBase",
    "with_db_init",
    "CommandDiscover",
]
