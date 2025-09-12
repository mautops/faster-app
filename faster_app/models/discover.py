"""
自动发现 apps 目录下的 models 模块
"""

from tortoise import Model
from faster_app.utils.discover import DiscoverBase
from faster_app.utils import BASE_DIR


class ModelDiscover(DiscoverBase):
    """模型发现器"""

    INSTANCE_TYPE = Model

    TARGETS = [
        {
            "directory": f"{BASE_DIR}/apps",
            "filename": None,
            "skip_dirs": ["__pycache__"],
            "skip_files": [],
        },
    ]

    def discover(self) -> dict[str, list[str]]:
        """
        发现模型模块路径
        返回按app分组的模块路径字典, 用于Tortoise ORM的apps配置
        """
        apps_models = {}

        # 扫描 TARGETS 中的目录和文件
        for target in self.TARGETS:
            files = self.walk(
                directory=target.get("directory"),
                filename=target.get("filename"),
                skip_files=target.get("skip_files"),
                skip_dirs=target.get("skip_dirs"),
            )

            for file_path in files:
                # 将文件路径转换为模块路径
                # 例如: apps/auth/models.py -> apps.auth.models
                module_path = file_path.replace("/", ".").replace(".py", "")

                # 提取app名称 (例如: apps.auth.models -> auth)
                path_parts = module_path.split(".")
                if len(path_parts) >= 3 and path_parts[0] == "apps":
                    app_name = path_parts[1]  # auth, perm, tenant, project

                    if app_name not in apps_models:
                        apps_models[app_name] = []
                    apps_models[app_name].append(module_path)

        return apps_models
