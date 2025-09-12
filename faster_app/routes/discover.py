from fastapi import APIRouter
from faster_app.utils.discover import DiscoverBase
from faster_app.utils import BASE_DIR


class RoutesDiscover(DiscoverBase):
    INSTANCE_TYPE = APIRouter
    TARGETS = [
        {
            "directory": f"{BASE_DIR}/apps",
            "filename": None,
            "skip_dirs": ["__pycache__"],
            "skip_files": [],
        },
        {
            "directory": f"{BASE_DIR}/routes/builtins",
            "filename": None,
            "skip_dirs": ["__pycache__"],
            "skip_files": [],
        },
    ]

    def import_and_extract_instances(
        self, file_path: str, module_name: str
    ) -> list[APIRouter]:
        """
        导入模块并提取路由实例
        对于路由，我们查找已经实例化的 APIRouter 对象
        """
        instances = []

        try:
            # 动态导入模块
            import importlib.util
            import inspect

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return instances

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 查找模块中所有的 APIRouter 实例
            for _, obj in inspect.getmembers(module):
                if isinstance(obj, self.INSTANCE_TYPE):
                    instances.append(obj)

        except Exception as e:
            # 静默跳过导入失败的模块，避免阻断整个发现过程
            print(f"Warning: Failed to import routes from {module_name}: {e}")

        return instances
