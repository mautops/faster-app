"""
自动发现 config 目录下的配置模块
"""

from pydantic_settings import BaseSettings

from faster_app.settings.builtins.settings import DefaultSettings
from faster_app.utils import BASE_DIR
from faster_app.utils.discover import BaseDiscover


class SettingsDiscover(BaseDiscover):
    """配置发现器"""

    INSTANCE_TYPE = BaseSettings

    TARGETS = [
        {
            "directory": "config",
            "filename": None,
            "skip_dirs": ["__pycache__"],
            "skip_files": ["__init__.py"],
        },
        {
            "directory": f"{BASE_DIR}/settings/builtins",
            "filename": "settings.py",
            "skip_dirs": ["__pycache__"],
            "skip_files": [],
        },
    ]

    def merge(self) -> DefaultSettings:
        """
        合并配置: 使用用户配置覆盖内置配置

        简化逻辑：
        1. 发现所有配置实例
        2. 分离默认配置和用户配置
        3. 简单合并（用户配置覆盖默认配置）
        """
        configs: list[BaseSettings] = self.discover()

        # 分离默认配置和用户配置
        default_settings = None
        user_settings = []

        for config in configs:
            if type(config).__name__ == "DefaultSettings":
                default_settings = config
            else:
                user_settings.append(config)

        # 如果没有找到默认配置，创建一个
        if default_settings is None:
            default_settings = DefaultSettings()

        # 如果没有用户配置，直接返回默认配置
        if not user_settings:
            return default_settings  # type: ignore[return-value]

        # 收集所有用户配置的属性
        user_overrides = {}
        for user_setting in user_settings:
            user_dict = user_setting.model_dump()
            user_overrides.update(user_dict)

        # 获取 DefaultSettings 的所有字段和默认值
        default_fields = set(DefaultSettings.model_fields.keys())
        default_values = default_settings.model_dump()

        # 找出用户配置中的新字段（自定义环境变量）
        user_fields = set(user_overrides.keys())
        new_fields = user_fields - default_fields

        # 合并：用户配置覆盖默认配置
        merged_values = {**default_values, **user_overrides}

        if not new_fields:
            # 没有新字段，直接返回 DefaultSettings 实例
            return DefaultSettings(**merged_values)

        # 有用户自定义字段，动态创建子类以保留这些字段（与 0.1.7 行为一致）
        from typing import Any

        from pydantic import ConfigDict

        # 为新字段创建类型注解
        new_annotations = {}
        for field in new_fields:
            value = user_overrides[field]
            if value is not None:
                field_type = type(value)
                if field_type in (str, int, float, bool, list, dict):
                    new_annotations[field] = field_type
                else:
                    new_annotations[field] = Any
            else:
                new_annotations[field] = Any | None

        # 动态子类允许额外字段，避免 extra="ignore" 丢弃自定义配置
        model_config = ConfigDict(extra="allow", env_file=".env", env_file_encoding="utf-8")
        dynamic_settings_class = type(
            "DynamicSettings",
            (DefaultSettings,),
            {
                "__annotations__": {
                    **getattr(DefaultSettings, "__annotations__", {}),
                    **new_annotations,
                },
                "__module__": DefaultSettings.__module__,
                "model_config": model_config,
            },
        )
        return dynamic_settings_class(**merged_values)
