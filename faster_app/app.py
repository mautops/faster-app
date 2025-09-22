"""
Faster APP 应用实例模块
"""

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from faster_app.routes.discover import RoutesDiscover
from faster_app.middleware.discover import MiddlewareDiscover
from faster_app.settings import logger
from faster_app.settings import configs
from faster_app.utils import BASE_DIR
from faster_app.utils.db import lifespan


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    app = FastAPI(
        title=configs.PROJECT_NAME,
        version=configs.VERSION,
        debug=configs.DEBUG,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )

    # 添加静态文件服务器
    try:
        app.mount(
            "/static", StaticFiles(directory=f"{BASE_DIR}/statics"), name="static"
        )
    except Exception as e:
        logger.error(f"静态文件服务器启动失败: {e}")

    # 添加中间件
    try:
        middleware_discover = MiddlewareDiscover()
        middleware_configs = middleware_discover.get_configs()

        # 按优先级顺序添加中间件（使用 FastAPI 推荐的 add_middleware 方法）
        for config in middleware_configs:
            middleware_class = config["class"]
            app.add_middleware(middleware_class, **config["kwargs"])
            logger.info(
                f"已注册中间件: {middleware_class.__name__} (优先级: {config['priority']})"
            )

    except Exception as e:
        logger.error(f"中间件注册失败: {e}")

    # 添加路由
    routes = RoutesDiscover().discover()
    for route in routes:
        app.include_router(route)

    return app


def get_app() -> FastAPI:
    """获取应用实例（单例模式）"""
    if not hasattr(get_app, "_app"):
        get_app._app = create_app()
    return get_app._app
