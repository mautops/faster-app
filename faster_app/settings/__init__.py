"""
配置模块

提供基于 pydantic-settings 的配置管理
"""

from faster_app.settings.builtins.settings import DefaultSettings

# 创建默认配置实例
configs = DefaultSettings()
