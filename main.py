"""
Faster APP 命令行入口
"""

import fire
from faster_app.commands.discover import CommandDiscover


if __name__ == "__main__":
    command_instances = CommandDiscover().discover()

    # 将命令实例转换为字典，使用类名作为键
    commands = {}
    for instance in command_instances:
        # 使用 CommandBase 的 get_command_name 方法自动去除后缀
        command_name = instance.get_command_name()
        commands[command_name] = instance

    # 直接传递命令字典给 Fire
    fire.Fire(commands)
