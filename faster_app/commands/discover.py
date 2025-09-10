"""
自动发现 apps 目录下的 commands 模块和内置命令
"""

from typing import Dict
from faster_app.commands.base import CommandBase
from faster_app.base import DiscoverBase


class CommandDiscover(DiscoverBase):
    INSTANCE_TYPE = CommandBase
    TARGETS = [
        {
            "directory": "apps",
            "filename": "commands.py",
            "skip_dirs": ["__pycache__"],
            "skip_files": [],
        },
        {
            "directory": f"{DiscoverBase.FASTER_APP_PATH}/commands/builtins",
            "filename": None,
            "skip_dirs": ["__pycache__"],
            "skip_files": [],
        },
    ]

    def collect(self) -> Dict[str, CommandBase]:
        commands = {}
        command_instances = self.discover()

        # 将命令实例转换为字典，使用类名作为键
        for instance in command_instances:
            # 使用 CommandBase 的 _get_command_name 方法自动去除后缀
            command_name = instance._get_command_name()
            commands[command_name] = instance

        return commands
