"""
Faster APP 命令行入口
"""

import os
import sys
import fire
from faster_app.commands.discover import CommandDiscover
from faster_app.settings import logger


def setup_python_path():
    """
    自动将当前工作目录添加到 Python 模块搜索路径中
    这样可以确保用户项目中的模块能够被正确导入
    """
    current_dir = os.getcwd()
    
    # 检查当前目录是否已经在 sys.path 中
    if current_dir not in sys.path:
        # 将当前目录插入到 sys.path 的开头，确保优先级最高
        sys.path.insert(0, current_dir)
        logger.debug(f"✅ 已将当前目录添加到 Python 模块搜索路径: {current_dir}")
    
    # 同时设置 PYTHONPATH 环境变量（可选，主要用于子进程）
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if current_dir not in current_pythonpath.split(os.pathsep):
        if current_pythonpath:
            os.environ['PYTHONPATH'] = f"{current_dir}{os.pathsep}{current_pythonpath}"
        else:
            os.environ['PYTHONPATH'] = current_dir


def main():
    """
    Faster APP 命令行入口点
    """
    # 在执行任何命令之前，先设置 Python 路径
    setup_python_path()
    
    commands = CommandDiscover().collect()
    fire.Fire(commands)


if __name__ == "__main__":
    main()
