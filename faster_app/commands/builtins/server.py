import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from tortoise import Tortoise
from rich.console import Console
from starlette.staticfiles import StaticFiles
from faster_app.settings import configs
from faster_app.commands.base import CommandBase
from faster_app.db import tortoise_init
import uvicorn
import threading

from faster_app.routes.discover import RoutesDiscover

console = Console()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await tortoise_init()
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
            import os

            static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "statics")
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
        except Exception as e:
            console.print(f"静态文件服务器启动失败: {e}")

        # 添加路由
        routes = RoutesDiscover().discover()
        for route in routes:
            app.include_router(route)

        return app


app = FastAPIAppSingleton()


class ServerOperations(CommandBase):
    """FastAPI Server Operations"""

    def __init__(self, host: str = None, port: int = None):
        self.host = host or configs.HOST
        self.port = port or configs.PORT
        self.configs = configs

    def start(self):
        """start fastapi server"""
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

        reload = True if self.configs.DEBUG else False
        uvicorn.run(
            "faster_app.commands.builtins.fastapi:app",
            host=self.host,
            port=self.port,
            reload=reload,
        )
