"""
Lifespan 组合器

支持组合多个独立的 lifespan 上下文管理器。
"""

from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager

from fastapi import FastAPI

__all__ = ["combine_lifespans"]

# Lifespan 函数类型
LifespanFunc = Callable[[FastAPI], AbstractAsyncContextManager[None]]


def combine_lifespans(*lifespans: LifespanFunc) -> LifespanFunc:
    """组合多个 lifespan 上下文管理器

    将多个独立的 lifespan 函数组合成一个, 按顺序执行启动和关闭逻辑。

    Args:
        *lifespans: 多个 lifespan 函数

    Returns:
        组合后的 lifespan 函数

    Example:
        >>> @asynccontextmanager
        ... async def db_lifespan(app: FastAPI):
        ...     await init_db()
        ...     yield
        ...     await close_db()
        ...
        >>> @asynccontextmanager
        ... async def cache_lifespan(app: FastAPI):
        ...     await init_cache()
        ...     yield
        ...     await close_cache()
        ...
        >>> combined = combine_lifespans(db_lifespan, cache_lifespan)
        >>> app = FastAPI(lifespan=combined)
    """
    if not lifespans:
        # 如果没有提供任何 lifespan, 返回一个空的
        @asynccontextmanager
        async def empty_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            yield

        return empty_lifespan

    @asynccontextmanager
    async def combined_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """组合后的 lifespan"""
        async with AsyncExitStack() as stack:
            # 按顺序进入所有上下文管理器 (启动)
            for lifespan_func in lifespans:
                await stack.enter_async_context(lifespan_func(app))

            # 所有启动完成, 应用运行
            yield

            # AsyncExitStack 会自动按相反顺序退出所有上下文管理器 (关闭)

    return combined_lifespan
