"""
命令基类, 使用 fire 库管理子命令
"""

import os
import sys
import inspect
from functools import wraps
from tortoise import Tortoise
from faster_app.db import tortoise_init


def with_db_init(func):
    """装饰器：为异步方法自动初始化和关闭数据库连接"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 初始化数据库连接
        await tortoise_init()
        try:
            # 执行原方法
            result = await func(*args, **kwargs)
            return result
        finally:
            # 关闭数据库连接
            if Tortoise._inited:
                await Tortoise.close_connections()

    return wrapper


class CommandBase(object):
    """命令基类"""

    BASE_PATH = os.path.dirname(os.path.dirname(__file__))

    # 默认要去掉的后缀列表
    DEFAULT_SUFFIXES = [
        "Command",
        "Commands",
        "Handler",
        "Handlers",
        "Operations",
        "Operation",
    ]

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

    def __getattribute__(self, name):
        """自动为异步方法添加数据库初始化装饰器"""
        attr = object.__getattribute__(self, name)

        # 如果是方法且是异步的，自动添加数据库初始化装饰器
        if (
            inspect.iscoroutinefunction(attr)
            and not name.startswith("_")
            and not hasattr(attr, "_db_wrapped")
        ):
            wrapped_attr = with_db_init(attr)
            wrapped_attr._db_wrapped = True  # 标记已包装，避免重复包装
            return wrapped_attr

        return attr

    @classmethod
    def _get_command_name(cls, class_name: str = None, suffixes: list = None) -> str:
        """
        自动去除类名中的常见后缀，生成简洁的命令名

        Args:
            class_name: 类名，如果不提供则使用当前类的名称
            suffixes: 要去除的后缀列表，如果不提供则使用默认后缀

        Returns:
            去除后缀后的命令名（小写）
        """
        if class_name is None:
            class_name = cls.__name__

        if suffixes is None:
            suffixes = cls.DEFAULT_SUFFIXES

        # 按照后缀长度从长到短排序，优先匹配较长的后缀
        sorted_suffixes = sorted(suffixes, key=len, reverse=True)

        for suffix in sorted_suffixes:
            if class_name.endswith(suffix):
                return class_name[: -len(suffix)].lower()

        # 如果没有匹配的后缀，直接返回小写的类名
        return class_name.lower()
