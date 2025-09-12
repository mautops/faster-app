"""
配置模块

提供基于 pydantic-settings 的配置管理
"""

from .discover import SettingsDiscover
from .logging import logger, log_config
from faster_app.models import ModelDiscover

# 创建默认配置实例
configs = SettingsDiscover().merge()

# 确保 TORTOISE_ORM 配置正确
if hasattr(configs, "TORTOISE_ORM") and configs.TORTOISE_ORM:
    models = []
    # 自动发现模型并添加到配置中
    # {app_name: [model_path, ...]}
    models_discover = ModelDiscover().discover()
    for _, value in models_discover.items():
        models.extend(value)

    # 确保 aerich.models 被包含
    if "aerich.models" not in models:
        models.append("aerich.models")

    configs.TORTOISE_ORM["apps"]["models"]["models"] = models


__all__ = [
    "configs",
    "logger",
    "log_config",
]
