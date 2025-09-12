"""系统内置命令"""

import os
import shutil
from typing import Optional
from faster_app.commands.base import BaseCommand
from rich.console import Console
from faster_app.utils.config import get_aerich_config
from faster_app.utils.decorators import with_aerich_command
from aerich import Command
from faster_app.settings import configs

console = Console()

# 常量定义
AERICH_APP_NAME = "aerich"
AERICH_MODELS = ["aerich.models"]


class DBOperations(BaseCommand):
    """aerich commands implementation"""

    def __init__(self, fake: bool = False):
        super().__init__()  # 调用父类初始化，自动配置 PYTHONPATH
        self.fake = fake
        self.command = Command(tortoise_config=get_aerich_config(), app=AERICH_APP_NAME)

    @with_aerich_command(tortoise=True)
    async def init(self) -> None:
        """Initialize aerich config and create migrations folder.

        Args:
            location: default ./migrations
            src_folder: source code folder, relative to project root
        """
        await self.command.init()
        console.print("✅ Successfully created migrations folder: {location}")

    @with_aerich_command(tortoise=True)
    async def init_db(self) -> None:
        """Generate schema and generate app migration folder."""
        await self.command.init_db(safe=True)
        console.print("✅ Database initialization successful")

    @with_aerich_command(tortoise=True)
    async def migrate(self, name: Optional[str] = None, empty: bool = False) -> None:
        """Generate a migration file for the current state of the models.

        Args:
            name: migration file name
            empty: whether to generate an empty migration file
        """
        await self.command.migrate(name=name, empty=empty)
        if empty:
            console.print("✅ Empty migration file generated successfully")
        else:
            console.print("✅ Migration file generated successfully")

    @with_aerich_command(tortoise=True)
    async def upgrade(self) -> None:
        """Upgrade to specified migration version."""
        await self.command.upgrade(fake=self.fake)
        console.print("✅ Database migration execution successful")

    @with_aerich_command(tortoise=True)
    async def downgrade(self, version: int = -1) -> None:
        """Downgrade to specified version."""
        await self.command.downgrade(version=version, delete=True, fake=self.fake)
        console.print("✅ Database downgrade successful")

    @with_aerich_command(tortoise=True)
    async def history(self) -> None:
        """List all migrations."""
        history = await self.command.history()
        console.print("✅ Migration history:")
        for record in history:
            console.print(f"  - {record}")

    @with_aerich_command(tortoise=True)
    async def heads(self) -> None:
        """Show currently available heads (unapplied migrations)."""
        heads = await self.command.heads()
        console.print("✅ Current migration heads:")
        for record in heads:
            console.print(f"  - {record}")

    async def dev_clean(self, force: bool = False) -> None:
        """Clean development environment db migrations.

        Args:
            force: whether to force clean, skip confirmation prompt

        Warning:
            This operation will delete all data, please use with caution! Only in development environment!
        """
        # 安全检查：仅在调试模式下允许
        if not configs.DEBUG:
            console.print(
                "❌ This operation is only allowed in development environment (DEBUG=True)!"
            )
            return

        # 确认提示
        if not force:
            console.print(
                "⚠️  [bold red]Warning: This operation will delete all database files and migration records![/bold red]"
            )
            confirm = console.input("Continue? (输入 'yes' 确认): ")
            if confirm.lower() != "yes":
                console.print("❌ Operation cancelled")
                return

        try:
            # 删除数据库文件
            db_file = f"{configs.DB_DATABASE}.db"
            if os.path.exists(db_file):
                os.remove(db_file)
                console.print(f"✅ Database file deleted: {db_file}")

            # 递归删除 migrations 目录
            migrations_dir = "migrations"
            if os.path.exists(migrations_dir):
                shutil.rmtree(migrations_dir)
                console.print(f"✅ Migration directory deleted: {migrations_dir}")

            console.print("✅ Development environment data cleanup successful")
        except Exception as e:
            console.print(f"❌ Cleanup development environment data failed: {e}")
            raise
