"""
自动发现 apps 目录下的 models 模块
"""

from pydantic_settings import BaseSettings
from faster_app.utils.discover import DiscoverBase
from faster_app.settings.builtins.settings import DefaultSettings
from faster_app.utils import BASE_DIR


class SettingsDiscover(DiscoverBase):
    """配置发现器"""

    INSTANCE_TYPE = BaseSettings

    TARGETS = [
        {
            "directory": f"{BASE_DIR}/config",
            "filename": None,
            "skip_dirs": ["__pycache__"],
            "skip_files": [],
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

        # 直接创建 DefaultSettings 实例，传入用户覆盖的参数
        # 这样可以确保DefaultSettings的__init__方法正确执行，并且避免Pydantic类型注解问题
        merged_settings = DefaultSettings(**user_overrides)

        return merged_settings
