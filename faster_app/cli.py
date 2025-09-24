import os
import sys
import fire
from faster_app.commands.discover import CommandDiscover


def main():
    """Faster-App 命令行工具主入口"""
    # 将当前工作目录添加到 Python 路径，确保可以导入项目模块
    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # 设置 PYTHONPATH 环境变量，确保子进程也能找到项目模块
    pythonpath = os.environ.get("PYTHONPATH", "")
    if current_dir not in pythonpath:
        os.environ["PYTHONPATH"] = (
            current_dir + ":" + pythonpath if pythonpath else current_dir
        )

    # 收集命令
    commands = CommandDiscover().collect()
    fire.Fire(commands)


if __name__ == "__main__":
    main()
