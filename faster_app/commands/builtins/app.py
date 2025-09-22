import os
import shutil
from rich.console import Console
from faster_app.commands.base import BaseCommand
from faster_app.utils import BASE_DIR

console = Console()


class AppCommand(BaseCommand):
    """🛠️ 应用管理命令 - 快速创建和配置应用组件"""

    def env(self):
        """🔧 创建环境配置文件 (.env) - 从模板文件复制环境变量配置"""
        # 拷贝项目根路径下的 .env.example 文件到项目根路径
        try:
            shutil.copy(f"{BASE_DIR}/.env.example", ".env")
            console.print("[bold green]✅ .env 文件创建成功[/bold green]")
        except FileExistsError:
            console.print("[bold yellow]ℹ️  .env 文件已存在[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ .env 文件创建失败: {e}[/bold red]")

    def demo(self):
        """🎯 创建演示应用 - 生成完整的示例应用代码结构"""
        # 项目根路径下创建 apps 目录，如果存在则跳过
        try:
            if not os.path.exists("apps"):
                os.makedirs("apps")
            # 拷贝 /apps/demo 目录到 apps 目录
            shutil.copytree(f"{BASE_DIR}//apps/demo", "apps/demo")
            console.print("[bold green]✅ apps/demo 目录创建成功[/bold green]")
        except FileExistsError:
            console.print("[bold yellow]ℹ️  apps/demo 目录已存在[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ apps/demo 目录创建失败: {e}[/bold red]")

    def config(self):
        """⚙️ 创建配置目录 - 生成应用配置文件和设置"""
        # 拷贝 /config 到 . 目录
        try:
            shutil.copytree(f"{BASE_DIR}//config", "./config")
            console.print("[bold green]✅ config 目录创建成功[/bold green]")
        except FileExistsError:
            console.print("[bold yellow]ℹ️  config 目录已存在[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ config 目录创建失败: {e}[/bold red]")

    def main(self):
        """🚀 创建主程序文件 (main.py) - 生成应用入口点"""
        # 拷贝 /main.py 到 . 目录
        try:
            shutil.copy(f"{BASE_DIR}/main.py", "./main.py")
            console.print("[bold green]✅ main.py 文件创建成功[/bold green]")
        except FileExistsError:
            console.print("[bold yellow]ℹ️  main.py 文件已存在[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ main.py 文件创建失败: {e}[/bold red]")

    def middleware(self):
        """🔗 创建中间件目录 - 生成请求处理中间件组件"""
        # 拷贝 /middleware 到 . 目录
        try:
            shutil.copytree(f"{BASE_DIR}/middleware/builtins", "./middleware")
            console.print("[bold green]✅ middleware 目录创建成功[/bold green]")
        except FileExistsError:
            console.print("[bold yellow]ℹ️  middleware 目录已存在[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ middleware 目录创建失败: {e}[/bold red]")

    def docker(self):
        """🐳 创建 Docker 配置文件 - 生成容器化部署配置"""
        # 拷贝 /runtime/Dockerfile 到 . 目录
        try:
            shutil.copy(f"{BASE_DIR}/runtime/Dockerfile", "./Dockerfile")
            console.print("[bold green]✅ Dockerfile 文件创建成功[/bold green]")
        except FileExistsError:
            console.print("[bold yellow]ℹ️  Dockerfile 文件已存在[/bold yellow]")
        except Exception as e:
            console.print(f"[bold red]❌ Dockerfile 文件创建失败: {e}[/bold red]")
