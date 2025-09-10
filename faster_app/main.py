"""
Faster APP 命令行入口
"""

import fire
from faster_app.commands.discover import CommandDiscover


def main():
    """
    Faster APP 命令行入口点
    """
    commands = CommandDiscover().collect()
    fire.Fire(commands)


if __name__ == "__main__":
    main()
