"""
配置实例模块

提供全局配置实例, 避免循环导入
"""

from typing import TYPE_CHECKING

from .discover import SettingsDiscover

if TYPE_CHECKING:
    from .builtins.settings import DefaultSettings

# 创建默认配置实例
configs: "DefaultSettings" = SettingsDiscover().merge()
