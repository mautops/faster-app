"""
配置模块

提供基于 pydantic-settings 的配置管理
"""

from .discover import SettingsDiscover

# 创建默认配置实例
configs = SettingsDiscover().merge()
