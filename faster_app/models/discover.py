"""
自动发现 apps 目录下的 models 模块
"""

import os

from tortoise import Model

from faster_app.utils import BASE_DIR
from faster_app.utils.discover import BaseDiscover


class ModelDiscover(BaseDiscover):
    """模型发现器"""

    INSTANCE_TYPE = Model

    TARGETS = [
        {
            "directory": "apps",
            "filename": "models.py",
            "skip_dirs": ["__pycache__", "utils", "tests"],
            "skip_files": [],
        },
        {
            "directory": f"{BASE_DIR}/apps",
            "filename": "models.py",
            "skip_dirs": ["__pycache__", "utils", "tests"],
            "skip_files": [],
        },
    ]

    def discover(self) -> dict[str, list[str]]:  # type: ignore[override]
        """
        发现模型模块路径
        返回按app分组的模块路径字典, 用于Tortoise ORM的apps配置
        """
        apps_models: dict[str, list[str]] = {}

        # 扫描 TARGETS 中的目录和文件
        for target in self.TARGETS:
            directory = target.get("directory", "")
            files = self.walk(
                directory=directory,
                filename=target.get("filename"),
                skip_files=target.get("skip_files"),
                skip_dirs=target.get("skip_dirs"),
            )

            for file_path in files:
                # 将绝对路径转换为模块路径
                # 例如: /path/to/faster_app/apps/demo/models.py -> faster_app.apps.demo.models
                # 或者: apps/demo/models.py -> apps.demo.models

                # 如果是绝对路径,需要转换为相对模块路径
                if os.path.isabs(file_path):
                    # 找到 faster_app 目录的位置
                    if "faster_app" in file_path:
                        # 提取 faster_app 之后的部分
                        parts = file_path.split("faster_app")
                        if len(parts) > 1:
                            relative_path = "faster_app" + parts[1]
                            module_path = relative_path.replace(os.sep, ".").replace(".py", "")
                        else:
                            continue
                    else:
                        # 如果不是 faster_app 路径,跳过
                        continue
                else:
                    # 相对路径直接转换
                    module_path = file_path.replace(os.sep, ".").replace(".py", "")

                # 提取app名称 (例如: faster_app.apps.demo.models -> demo)
                path_parts = module_path.split(".")
                # 查找 apps 在路径中的位置
                if "apps" in path_parts:
                    apps_index = path_parts.index("apps")
                    if apps_index + 1 < len(path_parts):
                        app_name = path_parts[apps_index + 1]  # demo, auth, etc.

                        if app_name not in apps_models:
                            apps_models[app_name] = []
                        apps_models[app_name].append(module_path)

        return apps_models


def discover_models() -> list[str]:
    """发现模型模块路径"""
    aerich_models = ["aerich.models"]
    models_discover = ModelDiscover().discover()
    for _, value in models_discover.items():
        aerich_models.extend(value)

    # print("aerich_models", aerich_models)

    return aerich_models
