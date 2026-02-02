import importlib.util
import os

import uvicorn
from rich.console import Console

from faster_app.commands.base import BaseCommand
from faster_app.settings import configs
from faster_app.settings.logging import log_config

console = Console()


class ServerOperations(BaseCommand):
    """🚀 服务器操作命令 - 启动和管理 FastAPI 应用服务器"""

    def start(self) -> None:
        """🌟 启动 Web 服务器 - 自动检测用户配置或使用框架默认设置启动 FastAPI 应用"""
        user_main_path = os.path.join(os.getcwd(), "main.py")

        if os.path.exists(user_main_path):
            console.print(
                f"[bold yellow]🔍 发现用户自定义的 main.py: {user_main_path}[/bold yellow]"
            )
            if self._try_run_user_main(user_main_path):
                return None

        console.print("[bold blue]🚀 使用框架默认配置启动服务器[/bold blue]")
        self._run_server("faster_app.main:get_app", factory=True)

    def _try_run_user_main(self, user_main_path: str) -> bool:
        """🔍 尝试运行用户自定义的 main.py - 检测并执行用户的自定义应用配置

        Args:
            user_main_path: 用户 main.py 文件路径

        Returns:
            bool: 是否成功运行用户自定义配置
        """
        try:
            spec = importlib.util.spec_from_file_location("user_main", user_main_path)
            if spec is None or spec.loader is None:
                console.print("[bold yellow]⚠️  无法加载用户的 main.py[/bold yellow]")
                return False

            user_main = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_main)

            if hasattr(user_main, "app"):
                console.print("[bold green]⚙️  使用用户自定义的 FastAPI 应用实例[/bold green]")
                app_target = "main:app" if configs.DEBUG else user_main.app
                self._run_server(app_target)
                return True
            elif hasattr(user_main, "main") and callable(user_main.main):
                console.print("[bold green]▶️  执行用户自定义的 main 方法[/bold green]")
                user_main.main()
                return True
            else:
                console.print(
                    "[bold yellow]⚠️  用户的 main.py 中没有找到 app 实例或 main 方法[/bold yellow]"
                )
                return False
        except Exception as e:
            console.print(f"[bold red]❌ 执行用户自定义 main.py 时出错: {e}[/bold red]")
            return False

    def _run_server(self, app_target, factory: bool = False):
        """⚡ 统一的服务器启动方法 - 使用 Uvicorn 启动 FastAPI 应用

        Args:
            app_target: 应用实例或工厂函数路径
            factory: 是否使用工厂模式
        """
        reload = configs.DEBUG

        # 生产模式下的特殊处理
        if not reload:
            if factory and app_target == "faster_app.main:get_app":
                # 默认框架应用, 直接导入实例
                from faster_app.main import get_app

                app_target = get_app()
                factory = False
            elif isinstance(app_target, str) and not factory:
                # 用户自定义应用字符串, 需要导入为实例
                try:
                    if ":" in app_target:
                        module_name, attr_name = app_target.rsplit(":", 1)
                        if module_name == "main":
                            # 用户的 main.py
                            spec = importlib.util.spec_from_file_location(
                                "user_main", os.path.join(os.getcwd(), "main.py")
                            )
                            if spec is None or spec.loader is None:
                                console.print("[bold red]❌ 无法加载 main.py[/bold red]")
                                return

                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            app_target = getattr(module, attr_name)
                except Exception as e:
                    console.print(f"[bold red]❌ 导入应用实例失败: {e}[/bold red]")

        uvicorn.run(
            app_target,
            factory=factory,
            host=configs.SERVER.HOST,
            port=configs.SERVER.PORT,
            reload=reload,
            log_config=log_config,
        )
