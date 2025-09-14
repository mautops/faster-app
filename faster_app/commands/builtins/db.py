"""系统内置命令"""

import os
import shutil
from typing import Optional
from faster_app.commands.base import BaseCommand
from faster_app.utils.decorators import with_aerich_command
from aerich import Command
from faster_app.settings import configs
from faster_app.utils.project import project_config
from faster_app.settings import logger  



class DBOperations(BaseCommand):
    """aerich commands implementation"""

    def __init__(self, fake: bool = False):
        super().__init__()  # 调用父类初始化，自动配置 PYTHONPATH
        self.fake = fake
        self.command = Command(tortoise_config=configs.TORTOISE_ORM)

    @with_aerich_command()
    async def init(self) -> None:
        """initialize aerich config and create migrations folder.

        Args:
            location: default ./migrations
            src_folder: source code folder, relative to project root
        """
        await self.command.init()
        logger.info("✅ Successfully created migrations folder")

    @with_aerich_command()
    async def init_db(self) -> None:
        """generate schema and generate app migration folder."""
        await self.command.init_db(safe=True)
        logger.info("✅ Database initialization successful")

    @with_aerich_command()
    async def migrate(self, name: Optional[str] = None, empty: bool = False) -> None:
        """generate a migration file for the current state of the models.

        Args:
            name: migration file name
            empty: whether to generate an empty migration file
        """
        await self.command.migrate(name=name, empty=empty)
        if empty:
            logger.info("✅ Empty migration file generated successfully")
        else:
            logger.info("✅ Migration file generated successfully")

    @with_aerich_command()
    async def upgrade(self) -> None:
        """upgrade to specified migration version."""
        await self.command.upgrade(fake=self.fake)
        logger.info("✅ Database migration execution successful")

    @with_aerich_command()
    async def downgrade(self, version: int = -1) -> None:
        """downgrade to specified version."""
        await self.command.downgrade(version=version, delete=True, fake=self.fake)
        logger.info("✅ Database downgrade successful")

    @with_aerich_command()
    async def history(self) -> None:
        """list all migrations."""
        history = await self.command.history()
        logger.info("✅ Migration history:")
        for record in history:
            logger.info(f"  - {record}")

    @with_aerich_command()
    async def heads(self) -> None:
        """show currently available heads (unapplied migrations)."""
        heads = await self.command.heads()
        logger.info("✅ Current migration heads:")
        for record in heads:
            logger.info(f"  - {record}")

    async def dev_clean(self, force: bool = False) -> None:
        """clean development environment db migrations.

        Args:
            force: whether to force clean, skip confirmation prompt

        Warning:
            This operation will delete all data, please use with caution! Only in development environment!
        """
        # 安全检查：仅在调试模式下允许
        if not configs.DEBUG:
            logger.error(
                "❌ This operation is only allowed in development environment (DEBUG=True)!"
            )
            return

        try:
            # 删除数据库文件
            db_file = f"{project_config.name}.db"
            if os.path.exists(db_file):
                os.remove(db_file)
                logger.info(f"✅ Database file deleted: {db_file}")

            # 递归删除 migrations 目录
            migrations_dir = "migrations"
            if os.path.exists(migrations_dir):
                shutil.rmtree(migrations_dir)
                logger.info(f"✅ Migration directory deleted: {migrations_dir}")

            logger.info("✅ Development environment data cleanup successful")
        except Exception as e:
            logger.error(f"❌ Cleanup development environment data failed: {e}")
            raise
