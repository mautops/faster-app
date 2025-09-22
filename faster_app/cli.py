import fire
from faster_app.commands.discover import CommandDiscover


def main():
    """Faster-App 命令行工具主入口"""
    commands = CommandDiscover().collect()
    fire.Fire(commands)


if __name__ == "__main__":
    main()
