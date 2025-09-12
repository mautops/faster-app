"""
命令基类, 使用 fire 库管理子命令
"""

import os
import sys


class BaseCommand(object):
    """命令基类"""

    # 默认要去掉的前缀列表（私有属性，避免被 Fire 暴露）
    _DEFAULT_PREFIXES = []

    # 默认要去掉的后缀列表（私有属性，避免被 Fire 暴露）
    _DEFAULT_SUFFIXES = [
        "Command",
        "Commands",
        "Handler",
        "Handlers",
        "Operations",
        "Operation",
    ]

    class Meta:
        """
        PREFIXES = []
        SUFFIXES = []
        """

        PREFIXES = []
        SUFFIXES = []

    def __init__(self):
        """初始化命令基类，自动配置 PYTHONPATH"""
        self._setup_python_path()

    def _setup_python_path(self):
        """配置 Python 路径，确保可以导入项目模块"""
        # 将当前工作目录添加到 Python 路径，确保可以导入项目模块
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        # 设置 PYTHONPATH 环境变量，确保子进程也能找到项目模块
        pythonpath = os.environ.get("PYTHONPATH", "")
        if current_dir not in pythonpath:
            os.environ["PYTHONPATH"] = (
                current_dir + ":" + pythonpath if pythonpath else current_dir
            )

    @classmethod
    def _get_command_name(
        cls, class_name: str = None, prefixes: list = None, suffixes: list = None
    ) -> str:
        """
        自动去除类名中的前缀和后缀，生成简洁的命令名

        Args:
            class_name: 类名，如果不提供则使用当前类的名称
            prefixes: 要去除的前缀列表，如果不提供则使用 _DEFAULT_PREFIXES 和 Meta.PREFIXES
            suffixes: 要去除的后缀列表，如果不提供则使用 _DEFAULT_SUFFIXES 和 Meta.SUFFIXES

        Returns:
            去除前缀和后缀后的命令名（小写）
        """
        if class_name is None:
            class_name = cls.__name__

        # 获取前缀列表，合并默认前缀和 Meta 配置的前缀
        if prefixes is None:
            meta_prefixes = (
                getattr(cls.Meta, "PREFIXES", []) if hasattr(cls, "Meta") else []
            )
            prefixes = cls._DEFAULT_PREFIXES + meta_prefixes

        # 获取后缀列表，合并默认后缀和 Meta 配置的后缀
        if suffixes is None:
            meta_suffixes = (
                getattr(cls.Meta, "SUFFIXES", []) if hasattr(cls, "Meta") else []
            )
            suffixes = cls._DEFAULT_SUFFIXES + meta_suffixes

        # 去除前缀
        # 按照前缀长度从长到短排序，优先匹配较长的前缀
        sorted_prefixes = sorted(prefixes, key=len, reverse=True)
        for prefix in sorted_prefixes:
            if class_name.startswith(prefix):
                class_name = class_name[len(prefix) :]
                break

        # 去除后缀
        # 按照后缀长度从长到短排序，优先匹配较长的后缀
        sorted_suffixes = sorted(suffixes, key=len, reverse=True)
        for suffix in sorted_suffixes:
            if class_name.endswith(suffix):
                class_name = class_name[: -len(suffix)]
                break

        # 返回小写的命令名
        return class_name.lower()
