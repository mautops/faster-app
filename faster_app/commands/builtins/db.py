"""系统内置命令"""

import os
import shutil
from typing import Optional
from rich.console import Console
from faster_app.commands.base import BaseCommand
from faster_app.utils.decorators import with_aerich_command
from aerich import Command
from faster_app.settings import configs

console = Console()


class DBOperations(BaseCommand):
    """🗄️ 数据库操作命令 - 基于 Aerich 的数据库迁移和管理工具"""

    def __init__(self, fake: bool = False):
        super().__init__()  # 调用父类初始化，自动配置 PYTHONPATH
        self.fake = fake
        self.command = Command(tortoise_config=configs.TORTOISE_ORM)

    @with_aerich_command()
    async def init(self) -> None:
        """🌱 初始化数据库迁移 - 创建 Aerich 配置和迁移目录

        创建 ./migrations 目录用于存放数据库迁移文件
        """
        await self.command.init()
        console.print("[bold green]✅ 数据库迁移目录创建成功[/bold green]")

    @with_aerich_command()
    async def init_db(self) -> None:
        """🛠️ 初始化数据库架构 - 生成数据库表结构和应用迁移目录"""
        await self.command.init_db(safe=True)
        console.print("[bold green]✅ 数据库初始化成功[/bold green]")

    @with_aerich_command()
    async def migrate(self, name: Optional[str] = None, empty: bool = False) -> None:
        """📝 生成迁移文件 - 根据当前模型状态创建数据库迁移

        Args:
            name: 迁移文件名称
            empty: 是否生成空的迁移文件
        """
        await self.command.migrate(name=name, empty=empty)
        if empty:
            console.print("[bold green]✅ 空迁移文件生成成功[/bold green]")
        else:
            console.print("[bold green]✅ 迁移文件生成成功[/bold green]")

    @with_aerich_command()
    async def upgrade(self) -> None:
        """⬆️ 执行数据库迁移 - 升级到最新的迁移版本"""
        await self.command.upgrade(fake=self.fake)
        console.print("[bold green]✅ 数据库迁移执行成功[/bold green]")

    @with_aerich_command()
    async def downgrade(self, version: int = -1) -> None:
        """⬇️ 回滚数据库迁移 - 降级到指定的迁移版本

        Args:
            version: 目标版本号，默认 -1 表示回滚一个版本
        """
        await self.command.downgrade(version=version, delete=True, fake=self.fake)
        console.print("[bold green]✅ 数据库回滚成功[/bold green]")

    @with_aerich_command()
    async def history(self) -> None:
        """📜 查看迁移历史 - 显示所有数据库迁移记录"""
        history = await self.command.history()
        console.print("[bold cyan]📜 迁移历史记录:[/bold cyan]")
        for record in history:
            console.print(f"  [dim]•[/dim] {record}")

    @with_aerich_command()
    async def heads(self) -> None:
        """🔍 查看待应用迁移 - 显示当前可用的未应用迁移"""
        heads = await self.command.heads()
        console.print("[bold cyan]🔍 当前迁移头部:[/bold cyan]")
        for record in heads:
            console.print(f"  [dim]•[/dim] {record}")

    async def clean(self, force: bool = False) -> None:
        """🧹 清理开发环境数据 - 删除数据库和迁移文件

        Args:
            force: 是否强制清理，跳过确认提示

        ⚠️ 警告:
            此操作将删除所有数据，请谨慎使用！仅在开发环境中使用！
        """
        # 安全检查：仅在调试模式下允许
        if not configs.DEBUG:
            console.print(
                "[bold red]❌ 此操作仅允许在开发环境中执行 (DEBUG=True)![/bold red]"
            )
            return

        try:
            # 删除数据库文件
            db_file = f"{configs._normalize_db_name(configs.PROJECT_NAME)}.db"
            if os.path.exists(db_file):
                os.remove(db_file)
                console.print(
                    f"[bold green]✅ 数据库文件已删除: {db_file}[/bold green]"
                )

            # 递归删除 migrations 目录
            migrations_dir = "migrations"
            if os.path.exists(migrations_dir):
                shutil.rmtree(migrations_dir)
                console.print(
                    f"[bold green]✅ 迁移目录已删除: {migrations_dir}[/bold green]"
                )

            console.print("[bold green]✅ 开发环境数据清理成功[/bold green]")
        except Exception as e:
            console.print(f"[bold red]❌ 清理开发环境数据失败: {e}[/bold red]")
            raise
