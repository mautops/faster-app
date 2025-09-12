"""Utility functions and decorators"""

import os

# 先定义 BASE_DIR，避免循环导入
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# 延迟导入 decorators，避免循环导入
def _import_decorators():
    from .decorators import with_aerich_command

    return with_aerich_command


# 使用属性访问来延迟导入
def __getattr__(name):
    if name == "with_aerich_command":
        return _import_decorators()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "with_aerich_command",
    "BASE_DIR",
]
