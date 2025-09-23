"""
中间件自动发现器 - 极简版本
"""

import importlib
import importlib.util
import inspect
import os
import json
from typing import List, Type, Dict, Any
from faster_app.middleware.base import BaseMiddleware
from faster_app.utils.discover import BaseDiscover


class MiddlewareDiscover(BaseDiscover):
    """
    中间件发现器 - 极简实现

    基于 BaseDiscover，专注核心功能：
    1. 自动发现中间件类
    2. 可选的配置文件支持
    3. 生成最终配置
    """

    INSTANCE_TYPE = BaseMiddleware
    TARGETS = [
        {
            "directory": "middleware",
            "filename": None,
            "skip_dirs": ["__pycache__"],
            "skip_files": ["__init__.py"],
        },
    ]

    def import_and_extract_instances(
        self, file_path: str, module_name: str
    ) -> List[Type[BaseMiddleware]]:
        """
        重写父类方法，返回中间件类而不是实例
        """
        classes = []

        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return classes

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for _, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, self.INSTANCE_TYPE)
                    and obj != self.INSTANCE_TYPE
                    and not inspect.isabstract(obj)
                ):
                    classes.append(obj)

        except Exception as e:
            print(f"Warning: Failed to load middleware from {module_name}: {e}")

        return classes

    def get_configs(self) -> List[Dict[str, Any]]:
        """
        获取中间件配置 - 核心方法

        Returns:
            List[Dict]: 按优先级排序的中间件配置列表
        """
        configs = []

        # 1. 发现所有中间件类
        middleware_classes = self.discover()

        # 2. 加载配置文件（如果存在）
        file_configs = {}
        config_file = os.getenv("MIDDLEWARE_CONFIG")
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for config in data.get("middleware", []):
                        if "class_path" in config:
                            file_configs[config["class_path"]] = config
            except Exception as e:
                print(f"Warning: Failed to load config from {config_file}: {e}")

        # 3. 为每个发现的中间件生成配置
        for cls in middleware_classes:
            # 直接使用类对象，避免 class_path 导入问题
            priority = getattr(cls, "priority", 100)

            # 生成一个简单的标识符用于配置匹配
            class_id = f"middleware.{cls.__module__}.{cls.__name__}"

            # 使用配置文件中的设置（如果有）
            if class_id in file_configs:
                file_config = file_configs[class_id]
                config = {
                    "class": cls,  # 直接存储类对象
                    "priority": file_config.get("priority", priority),
                    "kwargs": file_config.get("kwargs", {}),
                }
            else:
                # 使用默认设置
                config = {
                    "class": cls,  # 直接存储类对象
                    "priority": priority,
                    "kwargs": {},
                }

            configs.append(config)

        # 4. 添加配置文件中的额外中间件（如内置中间件）
        for class_path, file_config in file_configs.items():
            # 检查是否已经在自动发现的配置中
            already_exists = any(
                f"middleware.{c['class'].__module__}.{c['class'].__name__}"
                == class_path
                for c in configs
            )
            if not already_exists:
                # 需要动态导入这个类
                middleware_class = self.import_class(class_path)
                if middleware_class:
                    configs.append(
                        {
                            "class": middleware_class,
                            "priority": file_config.get("priority", 100),
                            "kwargs": file_config.get("kwargs", {}),
                        }
                    )

        # 5. 按优先级排序
        configs.sort(key=lambda c: c["priority"])

        return configs

    def import_class(self, class_path: str) -> Type:
        """
        导入类 - 仅在需要时使用
        """
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except Exception as e:
            print(f"Warning: Failed to import {class_path}: {e}")
            return None
