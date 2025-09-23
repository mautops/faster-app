"""
自动发现 apps 目录下的 models 模块
"""

from pydantic_settings import BaseSettings
from faster_app.utils.discover import BaseDiscover
from faster_app.settings.builtins.settings import DefaultSettings
from faster_app.utils import BASE_DIR


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

    def merge(self) -> BaseSettings:
        """合并配置: 使用用户配置覆盖内置配置，同时保留DefaultSettings的方法和动态逻辑"""
        configs = self.discover()

        # 分离默认配置和用户配置
        default_settings = DefaultSettings()
        user_settings = []

        for config in configs:
            if type(config).__name__ == "DefaultSettings":
                default_settings = config
            else:
                user_settings.append(config)

        # 如果没有用户配置，直接返回默认配置
        if not user_settings:
            return default_settings

        # 收集所有用户配置的属性
        user_overrides = {}
        for user_setting in user_settings:
            user_dict = user_setting.model_dump()
            user_overrides.update(user_dict)

        # 获取 DefaultSettings 的所有字段和默认值
        default_fields = set(default_settings.model_fields.keys())
        default_values = default_settings.model_dump()

        # 找出用户配置中的新字段
        user_fields = set(user_overrides.keys())
        new_fields = user_fields - default_fields

        if not new_fields:
            # 没有新字段，使用原来的方式
            # 合并默认值和用户覆盖值
            merged_values = {**default_values, **user_overrides}
            return DefaultSettings(**merged_values)

        # 有新字段，需要动态创建类
        from typing import Any, Optional
        from pydantic import ConfigDict

        # 为新字段创建类型注解
        new_annotations = {}
        for field in new_fields:
            value = user_overrides[field]
            if value is not None:
                # 从值推断类型
                field_type = type(value)
                # 如果是基本类型，直接使用；否则使用 Any
                if field_type in (str, int, float, bool, list, dict):
                    new_annotations[field] = field_type
                else:
                    new_annotations[field] = Any
            else:
                # None 值使用 Optional[Any]
                new_annotations[field] = Optional[Any]

        # 创建新的模型配置，允许额外字段
        model_config = ConfigDict(
            extra="allow", env_file=".env", env_file_encoding="utf-8"
        )

        # 动态创建新的配置类
        DynamicSettings = type(
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

        # 创建实例 - 合并默认值和用户覆盖值
        merged_values = {**default_values, **user_overrides}
        merged_settings = DynamicSettings(**merged_values)
        return merged_settings
