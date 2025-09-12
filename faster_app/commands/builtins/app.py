import os
import shutil
from faster_app.commands.base import BaseCommand
from rich.console import Console
from faster_app.utils import BASE_DIR

console = Console()


class AppCommand(BaseCommand):
    """App Command"""

    async def env(self):
        """create .env file"""
        # 拷贝项目根路径下的 .env.example 文件到项目根路径
        try:
            shutil.copy(f"{BASE_DIR}/.env.example", ".env")
            console.print("✅ .env created successfully")
        except FileExistsError:
            console.print("✅ .env already exists")
        except Exception as e:
            console.print(f"❌ .env created failed: {e}")

    async def demo(self):
        """create demo app"""
        # 项目根路径下创建 apps 目录，如果存在则跳过
        try:
            if not os.path.exists("apps"):
                os.makedirs("apps")
            # 拷贝 /apps/demo 目录到 apps 目录
            shutil.copytree(f"{BASE_DIR}//apps/demo", "apps/demo")
            console.print("✅ apps/demo created successfully")
        except FileExistsError:
            console.print("✅ apps/demo already exists")
        except Exception as e:
            console.print(f"❌ apps/demo created failed: {e}")

    async def config(self):
        """create config"""
        # 拷贝 /config 到 . 目录
        try:
            shutil.copytree(f"{BASE_DIR}//config", "./config")
            console.print("✅ config created successfully")
        except FileExistsError:
            console.print("✅ config already exists")
        except Exception as e:
            console.print(f"❌ config created failed: {e}")
