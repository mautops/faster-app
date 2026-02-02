"""
Lifespan 自动发现

自动发现用户自定义的 lifespan 函数。
"""

import logging
from collections.abc import AsyncGenerator, Callable

from fastapi import FastAPI

from faster_app.utils.discover import BaseDiscover

logger = logging.getLogger(__name__)


class LifespanDiscover(BaseDiscover):
    """Lifespan 发现器

    自动发现用户自定义的 lifespan 函数。
    扫描 config/lifespan.py 文件, 查找所有 lifespan 函数。
    """

    INSTANCE_TYPE = None  # 不使用类实例, 直接查找函数

    TARGETS = [
        {
            "directory": "config",
            "filename": "lifespan.py",
            "skip_dirs": ["__pycache__"],
            "skip_files": [],
        },
    ]

    def _is_lifespan_function(self, func) -> bool:
        """检查函数是否符合 lifespan 要求

        Args:
            func: 要检查的函数

        Returns:
            是否符合 lifespan 要求
        """
        import inspect

        from fastapi import FastAPI

        try:
            sig = inspect.signature(func)
            params = list(sig.parameters.values())

            # 必须接受一个参数
            if len(params) != 1:
                return False

            # 参数类型必须是 FastAPI 或未注解
            param_annotation = params[0].annotation
            if param_annotation not in (FastAPI, inspect.Parameter.empty):
                return False

            # 返回类型必须是 AsyncGenerator 或未注解
            return_annotation = sig.return_annotation
            if return_annotation != inspect.Signature.empty:
                return "AsyncGenerator" in str(return_annotation)

            return True
        except (ValueError, TypeError):
            return False

    def discover(self) -> list[Callable[[FastAPI], AsyncGenerator[None, None]]]:
        """发现所有用户自定义的 lifespan 函数

        Returns:
            lifespan 函数列表
        """
        import importlib.util
        import inspect
        import os

        lifespans: list[Callable[[FastAPI], AsyncGenerator[None, None]]] = []

        for target in self.TARGETS:
            directory = target.get("directory")
            filename = target.get("filename")

            # 类型检查：确保 directory 和 filename 不为 None
            if directory is None or filename is None:
                continue

            if not os.path.exists(directory):
                continue

            file_path = os.path.join(directory, filename)
            if not os.path.exists(file_path):
                continue

            try:
                # 动态导入模块
                module_name = "user_lifespan"
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 查找所有 lifespan 函数
                for name, obj in inspect.getmembers(module):
                    # 跳过私有函数
                    if name.startswith("_") or not inspect.isfunction(obj):
                        continue

                    # 检查函数签名是否符合 lifespan 要求
                    if self._is_lifespan_function(obj):
                        lifespans.append(obj)
                        logger.info(f"发现用户自定义 lifespan: {name}")

            except Exception as e:
                logger.warning(f"加载 lifespan 文件失败 {file_path}: {e}")

        return lifespans
