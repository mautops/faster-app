"""
中间件自动发现器 - 极简版本
"""

import importlib
import importlib.util
from typing import Any

from faster_app.settings import logger
from faster_app.utils import BASE_DIR
from faster_app.utils.discover import BaseDiscover

# 中间件优先级常量
# 1-10: 日志和监控, 11-20: 安全, 21-30: 优化, 31+: 业务
PRIORITY_CORS = 12
PRIORITY_TRUSTED_HOST = 13
PRIORITY_GZIP = 21
PRIORITY_DEFAULT = 999

# 模块导入缓存
_module_cache: dict[str, Any] = {}


class MiddlewareDiscover(BaseDiscover):
    """
    中间件发现器 - 极简实现

    基于 BaseDiscover, 专注核心功能:
    1. 自动发现中间件类
    2. 可选的配置文件支持
    3. 生成最终配置
    """

    INSTANCE_TYPE = dict[str, Any]
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
    ) -> list[dict[str, Any]]:
        """
        导入模块并提取 MIDDLEWARES 实例

        Args:
            file_path: 文件路径
            module_name: 模块名称

        Returns:
            提取到的中间件配置列表
        """
        instances: list[dict[str, Any]] = []

        try:
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return instances

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 查找模块中的 MIDDLEWARES 变量
            if hasattr(module, "MIDDLEWARES"):
                middlewares = module.MIDDLEWARES
                # 确保 MIDDLEWARES 是一个列表
                if isinstance(middlewares, list):
                    instances.extend(middlewares)

        except Exception as e:
            logger.warning(f"Failed to import instances from {module_name}: {e}")

        return instances

    def discover(self) -> list[dict[str, Any]]:
        """
        自动扫描 TARGETS 中的目录和文件,
        导出所有的实例

        新增特性：
        1. 支持优先级排序（priority 字段）
        2. 支持动态启用/禁用（enabled 字段）
        3. 自动过滤禁用的中间件
        """
        middlewares = []
        instances = super().discover()
        middlewares_imported = []  # 已导入的中间件, 避免重复导入

        for instance in instances:
            # 检查是否启用（默认启用）
            enabled = instance.get("enabled", True)
            if not enabled:
                logger.debug(f"[中间件发现] 跳过禁用的中间件: {instance.get('class', 'unknown')}")
                continue

            if instance["class"] not in middlewares_imported:
                middlewares_imported.append(instance["class"])
                # 从字符串导入中间件类: "fastapi.middleware.cors.CORSMiddleware"
                try:
                    # 分离模块路径和类名
                    module_path, class_name = instance["class"].rsplit(".", 1)

                    # 从缓存中获取模块,或导入并缓存
                    if module_path not in _module_cache:
                        _module_cache[module_path] = importlib.import_module(module_path)
                    module = _module_cache[module_path]

                    # 从模块中获取类
                    instance["class"] = getattr(module, class_name)

                    # 保留优先级信息（如果有）
                    if "priority" not in instance:
                        instance["priority"] = PRIORITY_DEFAULT

                    middlewares.append(instance)
                except (ValueError, ImportError, AttributeError) as e:
                    logger.warning(f"Failed to import class {instance['class']}: {e}")

        # 按优先级排序（数字越小越先执行）
        middlewares.sort(key=lambda x: x.get("priority", PRIORITY_DEFAULT))

        # 记录中间件加载顺序
        if middlewares:
            logger.debug("[中间件发现] 中间件加载顺序（按优先级）:")
            for idx, mw in enumerate(middlewares, 1):
                logger.debug(
                    f"  {idx}. {mw['class'].__name__} (priority: {mw.get('priority', 999)})"
                )

        return middlewares
