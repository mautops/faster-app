"""
默认 Lifespan 实现

提供框架默认的 lifespan 组合和获取函数。
"""

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI

from faster_app.lifespan.apps import apps_lifespan
from faster_app.lifespan.database import database_lifespan
from faster_app.lifespan.discover import LifespanDiscover
from faster_app.lifespan.manager import LifespanManager
from faster_app.settings import configs, logger


@lru_cache(maxsize=1)
def _discover_user_lifespans() -> list:
    """发现用户自定义的 lifespan (带缓存)

    Returns:
        用户自定义的 lifespan 函数列表
    """
    try:
        user_lifespans = LifespanDiscover().discover()
        if user_lifespans:
            logger.info(f"发现 {len(user_lifespans)} 个用户自定义 lifespan")
        return user_lifespans
    except Exception as e:
        logger.warning(f"发现用户自定义 lifespan 失败: {e}, 使用默认配置")
        return []


def get_lifespan(
    *,
    enable_database: bool | None = None,
    enable_apps: bool | None = None,
    enable_user: bool | None = None,
) -> Callable[[FastAPI], AsyncGenerator[None, None]]:
    """获取组合后的 lifespan 函数

    自动组合:
    1. 框架默认的 lifespan (database_lifespan, apps_lifespan)
    2. 用户自定义的 lifespan (从 config/lifespan.py 自动发现)

    启动顺序由优先级决定 (默认: 数据库 -> 应用 -> 用户自定义)
    关闭顺序自动逆序

    通过配置可以控制启用哪些 lifespan:
    - ENABLE_DATABASE_LIFESPAN: 是否启用数据库 lifespan (默认 False)
    - ENABLE_APPS_LIFESPAN: 是否启用应用 lifespan (默认 False)
    - ENABLE_USER_LIFESPANS: 是否启用用户自定义 lifespan (默认 False)

    Args:
        enable_database: 是否启用数据库 lifespan,None 表示从配置读取
        enable_apps: 是否启用应用 lifespan,None 表示从配置读取
        enable_user: 是否启用用户自定义 lifespan,None 表示从配置读取

    Returns:
        组合后的 lifespan 函数
    """
    manager = LifespanManager()

    # 注册内置 lifespan (优先级: 数据库 < 应用 < 用户自定义)
    # 参数优先级高于配置
    if enable_database is None:
        enable_database = configs.LIFESPAN_DATABASE
    if enable_apps is None:
        enable_apps = configs.LIFESPAN_APPS
    if enable_user is None:
        enable_user = configs.LIFESPAN_USER

    manager.register(
        "database",
        database_lifespan,
        enabled=enable_database,
        priority=10,
    )

    manager.register(
        "apps",
        apps_lifespan,
        enabled=enable_apps,
        priority=20,
    )

    # 注册用户自定义的 lifespan
    if enable_user:
        user_lifespans = _discover_user_lifespans()
        for idx, user_lifespan in enumerate(user_lifespans):
            lifespan_name = getattr(user_lifespan, "__name__", f"user_lifespan_{idx}")
            manager.register(
                lifespan_name,
                user_lifespan,
                enabled=True,
                priority=100 + idx,  # 用户 lifespan 优先级最低
            )

    return manager.build()  # type: ignore[return-value]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """组合的生命周期管理

    使用 get_lifespan() 获取组合后的 lifespan, 自动包含:
    1. database_lifespan - 数据库连接生命周期 (可通过 ENABLE_DATABASE_LIFESPAN 控制)
    2. apps_lifespan - 应用生命周期 (可通过 ENABLE_APPS_LIFESPAN 控制)
    3. 用户自定义的 lifespan (可通过 ENABLE_USER_LIFESPANS 控制)

    启动顺序由优先级决定,关闭顺序自动逆序

    Args:
        app: FastAPI application instance

    Yields:
        None during application runtime

    Note:
        Application registry is stored in app.state.app_registry
    """
    combined = get_lifespan()
    async with combined(app):
        yield
