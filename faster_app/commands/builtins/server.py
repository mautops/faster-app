import os
import uvicorn
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from tortoise import Tortoise
from starlette.staticfiles import StaticFiles
from faster_app.settings import configs
from faster_app.commands.base import BaseCommand
from faster_app.settings import log_config, logger


from faster_app.routes.discover import RoutesDiscover


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(config=configs.TORTOISE_ORM)
    yield
    await Tortoise.close_connections()


class FastAPIAppSingleton:
    """线程安全的FastAPI应用单例类"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # 双重检查锁定模式
                if cls._instance is None:
                    cls._instance = cls._create_app()
        return cls._instance

    @classmethod
    def _create_app(cls):
        """创建FastAPI应用实例"""
        # 创建FastAPI应用实例
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
            static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "statics")
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
        except Exception as e:
            logger.error(f"静态文件服务器启动失败: {e}")

        # 添加路由
        routes = RoutesDiscover().discover()
        for route in routes:
            app.include_router(route)

        return app


app = FastAPIAppSingleton()


class ServerOperations(BaseCommand):
    """FastAPI Server Operations"""

    def __init__(self, host: str = None, port: int = None):
        super().__init__()  # 调用父类初始化，自动配置 PYTHONPATH
        self.host = host or configs.HOST
        self.port = port or configs.PORT
        self.configs = configs

    def start(self):
        """start fastapi server"""
        reload = True if self.configs.DEBUG else False
        uvicorn.run(
            "faster_app.commands.builtins.server:app",
            host=self.host,
            port=self.port,
            reload=reload,
            log_config=log_config,
        )
