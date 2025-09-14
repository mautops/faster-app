"""
配置模块

提供基于 pydantic-settings 的配置管理
"""

from .logging import logger, log_config
from .config import configs

__all__ = [
    "configs",
    "logger",
    "log_config",
]
