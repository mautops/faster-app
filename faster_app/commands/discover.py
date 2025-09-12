"""
自动发现 apps 目录下的 commands 模块和内置命令
"""

from typing import Dict
from faster_app.commands.base import BaseCommand
from faster_app.utils.discover import DiscoverBase
from faster_app.utils import BASE_DIR


class CommandDiscover(DiscoverBase):
    INSTANCE_TYPE = BaseCommand
    TARGETS = [
        {
            "directory": f"{BASE_DIR}/apps",
            "filename": None,
            "skip_dirs": ["__pycache__"],
            "skip_files": [],
        },
        {
            "directory": f"{BASE_DIR}/commands/builtins",
            "filename": None,
            "skip_dirs": ["__pycache__"],
            "skip_files": [],
        },
    ]

    def collect(self) -> Dict[str, BaseCommand]:
        commands = {}
        command_instances = self.discover()

        # 将命令实例转换为字典，使用类名作为键
        for instance in command_instances:
            # 使用 BaseCommand 的 _get_command_name 方法自动去除后缀
            command_name = instance._get_command_name()
            commands[command_name] = instance
        return commands
