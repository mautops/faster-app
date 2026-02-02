"""
测试 CLI 命令系统
"""

import asyncio
import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from faster_app.commands.base import BaseCommand
from faster_app.commands.builtins.app import AppCommand
from faster_app.commands.builtins.db import DBOperations
from faster_app.commands.builtins.server import ServerOperations
from faster_app.commands.discover import CommandDiscover


# ============ BaseCommand 测试 ============


class TestBaseCommand:
    """测试 BaseCommand 基类"""

    def test_command_name_generation(self):
        """测试命令名称生成"""

        class ServerCommand(BaseCommand):
            pass

        class AppOperations(BaseCommand):
            pass

        class DBHandler(BaseCommand):
            pass

        assert ServerCommand._get_command_name() == "server"
        assert AppOperations._get_command_name() == "app"
        assert DBHandler._get_command_name() == "db"

    def test_command_name_with_custom_suffixes(self):
        """测试自定义后缀的命令名称生成"""

        class CustomCommand(BaseCommand):
            class Meta:
                SUFFIXES = ["Custom"]

        # CustomCommand 会先去掉默认后缀 "Command", 得到 "Custom"
        # 然后去掉自定义后缀 "Custom", 得到 ""
        # 但实际上应该是 "custom" (小写)
        assert CustomCommand._get_command_name() == "custom"

    def test_command_name_with_custom_prefixes(self):
        """测试自定义前缀的命令名称生成"""

        class MyAppCommand(BaseCommand):
            class Meta:
                PREFIXES = ["My"]

        assert MyAppCommand._get_command_name() == "app"

    def test_python_path_setup(self):
        """测试 PYTHONPATH 配置"""
        cmd = BaseCommand()
        current_dir = os.getcwd()

        # 验证当前目录在 sys.path 中
        import sys

        assert current_dir in sys.path

        # 验证 PYTHONPATH 环境变量包含当前目录
        pythonpath = os.environ.get("PYTHONPATH", "")
        assert current_dir in pythonpath


# ============ CommandDiscover 测试 ============


class TestCommandDiscover:
    """测试命令发现系统"""

    def test_discover_builtin_commands(self):
        """测试发现内置命令"""
        with patch("faster_app.commands.builtins.db.Command"):
            discoverer = CommandDiscover()
            commands = discoverer.collect()

            # 验证内置命令被发现
            assert "app" in commands
            assert "db" in commands
            assert "server" in commands

            # 验证命令实例类型（使用类名字符串比较，避免导入问题）
            assert commands["app"].__class__.__name__ == "AppCommand"
            assert commands["db"].__class__.__name__ == "DBOperations"
            assert commands["server"].__class__.__name__ == "ServerOperations"

    def test_command_names_are_lowercase(self):
        """测试命令名称都是小写"""
        discoverer = CommandDiscover()
        commands = discoverer.collect()

        for name in commands.keys():
            assert name.islower(), f"命令名称 {name} 应该是小写"


# ============ AppCommand 测试 ============


class TestAppCommand:
    """测试应用管理命令"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(original_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def app_command(self):
        """创建 AppCommand 实例"""
        return AppCommand()

    def test_env_command_creates_file(self, app_command, temp_dir):
        """测试 env 命令创建 .env 文件"""
        with patch("shutil.copy") as mock_copy:
            app_command.env()
            mock_copy.assert_called_once()
            # 验证目标文件是 .env
            assert mock_copy.call_args[0][1] == ".env"

    def test_env_command_file_exists(self, app_command, temp_dir):
        """测试 env 命令在文件已存在时的行为"""
        # 创建 .env 文件
        Path(".env").touch()

        with patch("shutil.copy", side_effect=FileExistsError):
            # 不应该抛出异常
            app_command.env()

    def test_demo_command_creates_directory(self, app_command, temp_dir):
        """测试 demo 命令创建演示应用"""
        with patch("shutil.copytree") as mock_copytree:
            app_command.demo()
            mock_copytree.assert_called_once()
            # 验证目标目录是 apps/demo
            assert "apps/demo" in mock_copytree.call_args[0][1]

    def test_demo_command_creates_apps_dir(self, app_command, temp_dir):
        """测试 demo 命令创建 apps 目录"""
        with patch("shutil.copytree"):
            app_command.demo()
            assert os.path.exists("apps")

    def test_config_command_creates_directory(self, app_command, temp_dir):
        """测试 config 命令创建配置目录"""
        with patch("shutil.copytree") as mock_copytree:
            app_command.config()
            mock_copytree.assert_called_once()
            # 验证目标目录是 ./config
            assert mock_copytree.call_args[0][1] == "./config"

    def test_middleware_command_creates_directory(self, app_command, temp_dir):
        """测试 middleware 命令创建中间件目录"""
        with patch("shutil.copytree") as mock_copytree:
            app_command.middleware()
            mock_copytree.assert_called_once()
            # 验证目标目录是 ./middleware
            assert mock_copytree.call_args[0][1] == "./middleware"

    def test_docker_command_creates_file(self, app_command, temp_dir):
        """测试 docker 命令创建 Dockerfile"""
        with patch("shutil.copy") as mock_copy:
            app_command.docker()
            mock_copy.assert_called_once()
            # 验证目标文件是 ./Dockerfile
            assert mock_copy.call_args[0][1] == "./Dockerfile"

    def test_launch_command_creates_file(self, app_command, temp_dir):
        """测试 launch 命令创建 launch.json"""
        with patch("shutil.copy") as mock_copy:
            app_command.launch()
            mock_copy.assert_called_once()
            # 验证目标文件是 ./launch.json
            assert mock_copy.call_args[0][1] == "./launch.json"

    def test_makefile_command_creates_file(self, app_command, temp_dir):
        """测试 makefile 命令创建 Makefile"""
        with patch("shutil.copy") as mock_copy:
            app_command.makefile()
            mock_copy.assert_called_once()
            # 验证目标文件是 ./Makefile
            assert mock_copy.call_args[0][1] == "./Makefile"


# ============ DBOperations 测试 ============


class TestDBOperations:
    """测试数据库操作命令"""

    def test_init_command(self):
        """测试 init 命令初始化迁移"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_aerich.__aenter__ = AsyncMock(return_value=mock_aerich)
            mock_aerich.__aexit__ = AsyncMock(return_value=None)
            mock_aerich.init = AsyncMock()
            mock_command.return_value = mock_aerich

            db_command = DBOperations()

            with patch("asyncio.run") as mock_run:
                # 模拟 asyncio.run 的行为
                async def run_coro(coro):
                    return await coro
                mock_run.side_effect = lambda coro: asyncio.get_event_loop().run_until_complete(coro)

                db_command.init()

                # 验证 asyncio.run 被调用
                assert mock_run.called

    def test_init_db_command(self):
        """测试 init_db 命令初始化数据库"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_aerich.__aenter__ = AsyncMock(return_value=mock_aerich)
            mock_aerich.__aexit__ = AsyncMock(return_value=None)
            mock_aerich.init_db = AsyncMock()
            mock_command.return_value = mock_aerich

            db_command = DBOperations()

            with patch("asyncio.run") as mock_run:
                db_command.init_db()
                assert mock_run.called

    def test_init_db_command_file_exists(self):
        """测试 init_db 命令在文件已存在时的行为"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_aerich.__aenter__ = AsyncMock(return_value=mock_aerich)
            mock_aerich.__aexit__ = AsyncMock(return_value=None)
            mock_aerich.init_db = AsyncMock(side_effect=FileExistsError)
            mock_command.return_value = mock_aerich

            db_command = DBOperations()

            with patch("asyncio.run") as mock_run:
                # 不应该抛出异常
                db_command.init_db()
                assert mock_run.called

    def test_migrate_command(self):
        """测试 migrate 命令生成迁移"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_aerich.__aenter__ = AsyncMock(return_value=mock_aerich)
            mock_aerich.__aexit__ = AsyncMock(return_value=None)
            mock_aerich.migrate = AsyncMock()
            mock_command.return_value = mock_aerich

            db_command = DBOperations()

            with patch("asyncio.run") as mock_run:
                db_command.migrate(name="test_migration")
                assert mock_run.called

    def test_migrate_command_empty(self):
        """测试 migrate 命令生成空迁移"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_aerich.__aenter__ = AsyncMock(return_value=mock_aerich)
            mock_aerich.__aexit__ = AsyncMock(return_value=None)
            mock_aerich.migrate = AsyncMock()
            mock_command.return_value = mock_aerich

            db_command = DBOperations()

            with patch("asyncio.run") as mock_run:
                db_command.migrate(name="test_migration", empty=True)
                assert mock_run.called

    def test_upgrade_command(self):
        """测试 upgrade 命令执行迁移"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_aerich.__aenter__ = AsyncMock(return_value=mock_aerich)
            mock_aerich.__aexit__ = AsyncMock(return_value=None)
            mock_aerich.upgrade = AsyncMock()
            mock_command.return_value = mock_aerich

            db_command = DBOperations()

            with patch("asyncio.run") as mock_run:
                db_command.upgrade()
                assert mock_run.called

    def test_upgrade_command_with_fake(self):
        """测试 upgrade 命令使用 fake 参数"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_aerich.__aenter__ = AsyncMock(return_value=mock_aerich)
            mock_aerich.__aexit__ = AsyncMock(return_value=None)
            mock_aerich.upgrade = AsyncMock()
            mock_command.return_value = mock_aerich

            db_command = DBOperations(fake=True)

            with patch("asyncio.run") as mock_run:
                db_command.upgrade()
                assert mock_run.called

    def test_downgrade_command(self):
        """测试 downgrade 命令回滚迁移"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_aerich.__aenter__ = AsyncMock(return_value=mock_aerich)
            mock_aerich.__aexit__ = AsyncMock(return_value=None)
            mock_aerich.downgrade = AsyncMock()
            mock_command.return_value = mock_aerich

            db_command = DBOperations()

            with patch("asyncio.run") as mock_run:
                db_command.downgrade()
                assert mock_run.called

    def test_downgrade_command_with_version(self):
        """测试 downgrade 命令指定版本"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_aerich.__aenter__ = AsyncMock(return_value=mock_aerich)
            mock_aerich.__aexit__ = AsyncMock(return_value=None)
            mock_aerich.downgrade = AsyncMock()
            mock_command.return_value = mock_aerich

            db_command = DBOperations()

            with patch("asyncio.run") as mock_run:
                db_command.downgrade(version=2)
                assert mock_run.called

    def test_history_command(self):
        """测试 history 命令查看迁移历史"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_aerich.__aenter__ = AsyncMock(return_value=mock_aerich)
            mock_aerich.__aexit__ = AsyncMock(return_value=None)
            mock_aerich.history = AsyncMock(
                return_value=["migration_1", "migration_2", "migration_3"]
            )
            mock_command.return_value = mock_aerich

            db_command = DBOperations()

            with patch("asyncio.run") as mock_run:
                db_command.history()
                assert mock_run.called

    def test_heads_command(self):
        """测试 heads 命令查看待应用迁移"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_aerich.__aenter__ = AsyncMock(return_value=mock_aerich)
            mock_aerich.__aexit__ = AsyncMock(return_value=None)
            mock_aerich.heads = AsyncMock(return_value=["migration_4", "migration_5"])
            mock_command.return_value = mock_aerich

            db_command = DBOperations()

            with patch("asyncio.run") as mock_run:
                db_command.heads()
                assert mock_run.called

    @pytest.mark.asyncio
    async def test_clean_command_in_debug_mode(self):
        """测试 clean 命令在调试模式下清理数据"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_command.return_value = mock_aerich

            with patch("faster_app.commands.builtins.db.configs") as mock_configs:
                mock_configs.DEBUG = True

                with tempfile.TemporaryDirectory() as temp_dir:
                    original_dir = os.getcwd()
                    os.chdir(temp_dir)

                    try:
                        # 创建测试文件和目录
                        Path("db.sqlite").touch()
                        Path("migrations").mkdir()
                        Path("migrations/test.py").touch()

                        db_command = DBOperations()
                        await db_command.clean()

                        # 验证文件和目录被删除
                        assert not os.path.exists("db.sqlite")
                        assert not os.path.exists("migrations")
                    finally:
                        os.chdir(original_dir)

    @pytest.mark.asyncio
    async def test_clean_command_not_in_debug_mode(self):
        """测试 clean 命令在生产模式下拒绝执行"""
        with patch("faster_app.commands.builtins.db.Command") as mock_command:
            mock_aerich = MagicMock()
            mock_command.return_value = mock_aerich

            with patch("faster_app.commands.builtins.db.configs") as mock_configs:
                mock_configs.DEBUG = False

                with tempfile.TemporaryDirectory() as temp_dir:
                    original_dir = os.getcwd()
                    os.chdir(temp_dir)

                    try:
                        # 创建测试文件
                        Path("db.sqlite").touch()

                        db_command = DBOperations()
                        await db_command.clean()

                        # 验证文件未被删除
                        assert os.path.exists("db.sqlite")
                    finally:
                        os.chdir(original_dir)


# ============ ServerOperations 测试 ============


class TestServerOperations:
    """测试服务器操作命令"""

    def test_start_command_with_user_main(self):
        """测试 start 命令使用用户自定义 main.py"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            try:
                # 创建用户 main.py
                with open("main.py", "w") as f:
                    f.write("from fastapi import FastAPI\napp = FastAPI()\n")

                server_command = ServerOperations()

                with patch.object(server_command, "_try_run_user_main", return_value=True):
                    with patch.object(server_command, "_run_server") as mock_run:
                        server_command.start()
                        # 不应该调用默认服务器
                        mock_run.assert_not_called()
            finally:
                os.chdir(original_dir)

    def test_start_command_without_user_main(self):
        """测试 start 命令使用框架默认配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            try:
                server_command = ServerOperations()

                with patch.object(server_command, "_run_server") as mock_run:
                    server_command.start()
                    mock_run.assert_called_once_with("faster_app.main:get_app", factory=True)
            finally:
                os.chdir(original_dir)

    def test_try_run_user_main_with_app(self):
        """测试运行用户 main.py 中的 app 实例"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            try:
                # 创建用户 main.py
                with open("main.py", "w") as f:
                    f.write("from fastapi import FastAPI\napp = FastAPI()\n")

                server_command = ServerOperations()

                with patch.object(server_command, "_run_server") as mock_run:
                    result = server_command._try_run_user_main("main.py")
                    assert result is True
                    mock_run.assert_called_once()
            finally:
                os.chdir(original_dir)

    def test_try_run_user_main_with_main_function(self):
        """测试运行用户 main.py 中的 main 函数"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            try:
                # 创建用户 main.py
                with open("main.py", "w") as f:
                    f.write("def main():\n    print('Hello')\n")

                server_command = ServerOperations()
                result = server_command._try_run_user_main("main.py")
                assert result is True
            finally:
                os.chdir(original_dir)

    def test_try_run_user_main_without_app_or_main(self):
        """测试运行用户 main.py 但没有 app 或 main"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            try:
                # 创建用户 main.py
                with open("main.py", "w") as f:
                    f.write("# Empty file\n")

                server_command = ServerOperations()
                result = server_command._try_run_user_main("main.py")
                assert result is False
            finally:
                os.chdir(original_dir)

    def test_try_run_user_main_with_error(self):
        """测试运行用户 main.py 时出错"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_dir = os.getcwd()
            os.chdir(temp_dir)

            try:
                # 创建有语法错误的 main.py
                with open("main.py", "w") as f:
                    f.write("invalid python syntax !!!\n")

                server_command = ServerOperations()
                result = server_command._try_run_user_main("main.py")
                assert result is False
            finally:
                os.chdir(original_dir)

    def test_run_server_in_debug_mode(self):
        """测试在调试模式下运行服务器"""
        with patch("faster_app.commands.builtins.server.configs") as mock_configs:
            mock_configs.DEBUG = True
            mock_configs.SERVER.HOST = "127.0.0.1"
            mock_configs.SERVER.PORT = 8000

            with patch("faster_app.commands.builtins.server.uvicorn.run") as mock_run:
                server_command = ServerOperations()
                server_command._run_server("test:app")

                mock_run.assert_called_once()
                call_kwargs = mock_run.call_args[1]
                assert call_kwargs["reload"] is True
                assert call_kwargs["host"] == "127.0.0.1"
                assert call_kwargs["port"] == 8000

    def test_run_server_in_production_mode(self):
        """测试在生产模式下运行服务器"""
        with patch("faster_app.commands.builtins.server.configs") as mock_configs:
            mock_configs.DEBUG = False
            mock_configs.SERVER.HOST = "0.0.0.0"
            mock_configs.SERVER.PORT = 80

            with patch("faster_app.commands.builtins.server.uvicorn.run") as mock_run:
                server_command = ServerOperations()
                server_command._run_server("test:app")

                mock_run.assert_called_once()
                call_kwargs = mock_run.call_args[1]
                assert call_kwargs["reload"] is False

    def test_run_server_with_factory(self):
        """测试使用工厂模式运行服务器"""
        with patch("faster_app.commands.builtins.server.configs") as mock_configs:
            mock_configs.DEBUG = True
            mock_configs.SERVER.HOST = "127.0.0.1"
            mock_configs.SERVER.PORT = 8000

            with patch("faster_app.commands.builtins.server.uvicorn.run") as mock_run:
                server_command = ServerOperations()
                server_command._run_server("test:get_app", factory=True)

                mock_run.assert_called_once()
                call_kwargs = mock_run.call_args[1]
                assert call_kwargs["factory"] is True


# ============ CLI 集成测试 ============


class TestCLIIntegration:
    """测试 CLI 集成"""

    def test_cli_main_function(self):
        """测试 CLI 主函数"""
        with patch("faster_app.cli.fire.Fire") as mock_fire:
            with patch("faster_app.cli.CommandDiscover") as mock_discover:
                # 模拟命令发现
                mock_instance = MagicMock()
                mock_instance.collect.return_value = {
                    "app": MagicMock(),
                    "db": MagicMock(),
                    "server": MagicMock(),
                }
                mock_discover.return_value = mock_instance

                # 重新导入以触发 main 函数
                import importlib
                import faster_app.cli
                importlib.reload(faster_app.cli)

                faster_app.cli.main()

                # 验证 Fire 被调用
                mock_fire.assert_called_once()

                # 验证传递的命令字典
                commands = mock_fire.call_args[0][0]
                assert isinstance(commands, dict)

    def test_cli_pager_environment(self):
        """测试 CLI 设置 PAGER 环境变量"""
        # 保存原始 PAGER
        original_pager = os.environ.get("PAGER")

        try:
            # 清除 PAGER 环境变量
            if "PAGER" in os.environ:
                del os.environ["PAGER"]

            with patch("faster_app.cli.fire.Fire"):
                with patch("faster_app.cli.CommandDiscover"):
                    import importlib
                    import faster_app.cli
                    importlib.reload(faster_app.cli)

                    faster_app.cli.main()

                    # 验证 PAGER 被设置为 cat
                    assert os.environ.get("PAGER") == "cat"
        finally:
            # 恢复原始 PAGER
            if original_pager is not None:
                os.environ["PAGER"] = original_pager
            elif "PAGER" in os.environ:
                del os.environ["PAGER"]

    def test_cli_pythonpath_setup(self):
        """测试 CLI 设置 PYTHONPATH"""
        with patch("faster_app.cli.fire.Fire"):
            with patch("faster_app.cli.CommandDiscover"):
                import importlib
                import faster_app.cli
                importlib.reload(faster_app.cli)

                faster_app.cli.main()

                # 验证当前目录在 PYTHONPATH 中
                pythonpath = os.environ.get("PYTHONPATH", "")
                current_dir = os.getcwd()
                assert current_dir in pythonpath
