"""
自动发现 apps 目录下的 commands 模块和内置命令
"""

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
