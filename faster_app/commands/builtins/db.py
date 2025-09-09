"""系统内置命令"""

import os
import shutil
from faster_app.commands.base import CommandBase
from rich.console import Console
from faster_app.settings.builtins.settings import DefaultSettings
from faster_app.models.discover import ModelDiscover
from aerich import Command

console = Console()


class DBOperations(CommandBase):
    """数据库操作命令 - 使用Aerich管理数据库迁移"""

    def __init__(self, fake: bool = False):
        self.fake = fake
        self.command = Command(
            tortoise_config=self._get_tortoise_config(), app="aerich"
        )

    def _get_tortoise_config(self):
        """获取Tortoise ORM配置"""
        apps_models = ModelDiscover().discover()
        # print("--->", apps_models)  # 注释掉调试输出
        configs = DefaultSettings()
        tortoise_config = configs.TORTOISE_ORM.copy()

        # 清空原有的apps配置
        tortoise_config["apps"] = {}

        # 为每个app创建配置
        for app_name, models in apps_models.items():
            tortoise_config["apps"][app_name] = {
                "models": models,
                "default_connection": "development" if configs.DEBUG else "production",
            }

        # 添加aerich模型到一个单独的app中
        tortoise_config["apps"]["aerich"] = {
            "models": ["aerich.models"],
            "default_connection": "development" if configs.DEBUG else "production",
        }

        return tortoise_config

    async def init_db(self):
        """初始化数据库（首次创建表）"""
        try:
            await self.command.init_db(safe=True)
            console.print("✅ 数据库初始化成功")
        except Exception as e:
            console.print(f"❌ 数据库初始化失败: {e}")
        finally:
            await self.command.close()

    async def migrate(self):
        """执行数据库迁移"""
        try:
            await self.command.init()
            await self.command.migrate()
            console.print("✅ 数据库迁移执行成功")
        except Exception as e:
            console.print(f"❌ 数据库迁移执行失败: {e}")
        finally:
            await self.command.close()

    async def upgrade(self):
        """执行数据库迁移"""
        try:
            await self.command.init()
            await self.command.upgrade(fake=self.fake)
            console.print("✅ 数据库迁移执行成功")
        except Exception as e:
            console.print(f"❌ 数据库迁移执行失败: {e}")
        finally:
            await self.command.close()

    async def downgrade(self, version: int = -1):
        """回滚数据库迁移"""
        try:
            await self.command.init()
            await self.command.downgrade(version=version, delete=True, fake=self.fake)
            console.print("✅ 数据库回滚成功")
        except Exception as e:
            console.print(f"❌ 数据库回滚失败: {e}")
        finally:
            await self.command.close()

    async def history(self):
        """查看迁移历史"""
        try:
            await self.command.init()
            history = await self.command.history()
            console.print("✅ 迁移历史:")
            for record in history:
                console.print(f"  - {record}")

        except Exception as e:
            console.print(f"❌ 查看迁移历史失败: {e}")
        finally:
            await self.command.close()

    async def heads(self):
        """查看当前迁移头部"""
        try:
            await self.command.init()
            heads = await self.command.heads()
            console.print("✅ 当前迁移头部:")
            for record in heads:
                console.print(f"  - {record}")
        except Exception as e:
            console.print(f"❌ 查看当前迁移头部失败: {e}")
        finally:
            await self.command.close()

    async def dev_clean(self):
        """清理开发环境数据
        1. 移除 sqlite 数据库文件
        2. 移除 aerich 迁移记录
        """
        try:
            # 删除数据库文件
            db_file = f"{configs.DB_DATABASE}.db"
            if os.path.exists(db_file):
                os.remove(db_file)
                console.print(f"✅ 已删除数据库文件: {db_file}")

            # 递归删除 migrations 目录
            if os.path.exists("migrations"):
                shutil.rmtree("migrations")
                console.print("✅ 已删除迁移目录: migrations")

            console.print("✅ 开发环境数据清理成功")
        except Exception as e:
            console.print(f"❌ 清理开发环境数据失败: {e}")
