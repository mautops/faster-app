"""
中间件自动发现器 - 极简版本
"""

import importlib
import importlib.util
from typing import List, Dict, Any
from faster_app.utils.discover import BaseDiscover

from faster_app.utils import BASE_DIR
from faster_app.settings import logger


class MiddlewareDiscover(BaseDiscover):
    """
    中间件发现器 - 极简实现

    基于 BaseDiscover，专注核心功能：
    1. 自动发现中间件类
    2. 可选的配置文件支持
    3. 生成最终配置
    """

    INSTANCE_TYPE = Dict[str, Any]
    TARGETS = [
        {
            "directory": "middleware",
            "filename": None,
            "skip_dirs": ["__pycache__"],
            "skip_files": ["__init__.py"],
        },
        {
            "directory": f"{BASE_DIR}/middleware/builtins",
            "filename": None,
            "skip_dirs": ["__pycache__"],
            "skip_files": ["__init__.py"],
        },
    ]

    def import_and_extract_instances(
        self, file_path: str, module_name: str
    ) -> List[Dict[str, Any]]:
        """
        导入模块并提取 MIDDLEWARES 实例

        Args:
            file_path: 文件路径
            module_name: 模块名称

        Returns:
            提取到的中间件配置列表
        """
        instances = []

        try:
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return instances

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 查找模块中的 MIDDLEWARES 变量
            if hasattr(module, "MIDDLEWARES"):
                middlewares = getattr(module, "MIDDLEWARES")
                # 确保 MIDDLEWARES 是一个列表
                if isinstance(middlewares, list):
                    instances.extend(middlewares)

        except Exception as e:
            logger.warning(f"Failed to import instances from {module_name}: {e}")

        return instances

    def discover(self) -> List[Dict[str, Any]]:
        """
        自动扫描 TARGETS 中的目录和文件，
        导出所有的实例
        """
        middlewares = []
        instances = super().discover()
        middlewares_imported = []  # 已导入的中间件，避免重复导入

        for instance in instances:
            if instance["class"] not in middlewares_imported:
                middlewares_imported.append(instance["class"])
                # 从字符串导入中间件类: "fastapi.middleware.cors.CORSMiddleware"
                try:
                    # 分离模块路径和类名
                    module_path, class_name = instance["class"].rsplit(".", 1)

                    # 导入模块
                    module = importlib.import_module(module_path)

                    # 从模块中获取类
                    instance["class"] = getattr(module, class_name)

                    middlewares.append(instance)
                except (ValueError, ImportError, AttributeError) as e:
                    logger.warning(f"Failed to import class {instance['class']}: {e}")

        return middlewares
