"""Decorators for common functionality"""

import asyncio
from functools import wraps
from typing import Any

from tortoise import Tortoise


def with_tortoise_orm():
    """Tortoise ORM 装饰器, 自动管理数据库连接生命周期。

    假设:
    1. 只用于异步函数
    2. self 对象有 configs 属性或可以访问 configs
    3. 使用 asyncio.run 执行
    """

    def decorator(func: Any) -> Any:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            async def execute() -> Any:
                # 获取配置
                from faster_app.settings.builtins.orm import TORTOISE_ORM

                # 初始化 Tortoise ORM - 使用 TORTOISE_ORM 而不是 configs.TORTOISE_ORM
                await Tortoise.init(config=TORTOISE_ORM)

                try:
                    return await func(self, *args, **kwargs)
                finally:
                    # 关闭 Tortoise ORM 连接
                    await Tortoise.close_connections()

            return asyncio.run(execute())

        return wrapper

    return decorator


def with_aerich_command():
    """精简的 aerich 命令装饰器, 确保正确的资源管理。

    假设:
    1. 只用于异步函数
    2. self.command 是 aerich.Command 实例
    3. 使用 asyncio.run 执行
    """

    def decorator(func: Any) -> Any:
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            async def execute() -> Any:
                # 使用 aerich Command 作为异步上下文管理器
                async with self.aerich:
                    return await func(self, *args, **kwargs)

            return asyncio.run(execute())

        return wrapper

    return decorator
