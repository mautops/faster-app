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

        # 获取默认配置的所有值
        default_values = default_settings.model_dump()

        # 合并：用户配置覆盖默认配置
        merged_values = {**default_values, **user_overrides}

        # 返回合并后的配置实例
        return DefaultSettings(**merged_values)
