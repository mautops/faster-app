import os
import shutil
from faster_app.commands.base import CommandBase
from rich.console import Console

console = Console()


class AppCommand(CommandBase):
    """App Command"""

    async def env(self):
        """Create .env file"""
        # 拷贝项目根路径下的 .env.example 文件到项目根路径
        try:
            shutil.copy(f"{self.BASE_PATH}/.env.example", ".env")
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
            # 拷贝 templates/apps/demo 目录到 apps 目录
            shutil.copytree(f"{self.BASE_PATH}/templates/apps/demo", "apps/demo")
            console.print("✅ apps/demo created successfully")
        except FileExistsError:
            console.print("✅ apps/demo already exists")
        except Exception as e:
            console.print(f"❌ apps/demo created failed: {e}")

    async def config(self):
        """create config"""
        # 拷贝 templates/config 到 . 目录
        try:
            shutil.copytree(f"{self.BASE_PATH}/templates/config", "./config")
            console.print("✅ config created successfully")
        except FileExistsError:
            console.print("✅ config already exists")
        except Exception as e:
            console.print(f"❌ config created failed: {e}")
