import os
import shutil
from faster_app.commands.base import CommandBase
from rich.console import Console

console = Console()


class AppCommand(CommandBase):
    """App Command"""

    async def init(self):
        """Run Init App"""
        # 拷贝项目根路径下的 main.py 文件到项目根路径
        shutil.copy(f"{self.BASE_PATH}/main.py", "main.py")
        console.print("✅ main.py created successfully")

        # 拷贝项目根路径下的 .env.example 文件到项目根路径
        shutil.copy(f"{self.BASE_PATH}/.env.example", ".env")
        console.print("✅ .env created successfully")

    async def demo(self):
        """Run Demo"""
        # 项目根路径下创建 apps 目录，如果存在则跳过
        if not os.path.exists("apps"):
            os.makedirs("apps")
        # 拷贝 templates/apps/demo 目录到 apps 目录
        shutil.copytree(f"{self.BASE_PATH}/templates/apps/demo", "apps/demo")

    async def config(self):
        """Run Config"""
        # 项目根路径下创建 config 目录，如果存在则跳过
        if not os.path.exists("config"):
            os.makedirs("config")
        # 拷贝 templates/config/settings.py 到 config 目录
        shutil.copytree(
            f"{self.BASE_PATH}/templates/config/settings.py", "config/settings.py"
        )
