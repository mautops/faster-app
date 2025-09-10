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
        shutil.copy(f"{self.BASE_PATH}/.env.example", ".env")
        console.print("✅ .env created successfully")

    async def demo(self):
        """create demo app"""
        # 项目根路径下创建 apps 目录，如果存在则跳过
        if not os.path.exists("apps"):
            os.makedirs("apps")
        # 拷贝 templates/apps/demo 目录到 apps 目录
        shutil.copytree(f"{self.BASE_PATH}/templates/apps/demo", "apps/demo")

    async def config(self):
        """create config"""
        # 拷贝 templates/config 到 . 目录
        shutil.copytree(f"{self.BASE_PATH}/templates/config", ".")
