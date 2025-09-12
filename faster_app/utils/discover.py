import os
import importlib.util
import inspect
from typing import Dict, List


class DiscoverBase(object):
    INSTANCE_TYPE = None
    TARGETS: List[Dict[str, str]] = []

    def discover(self) -> List[type]:
        """
        自动扫描 TARGETS 中的目录和文件，
        导出所有的实例
        """
        instances = []

        # 扫描 TARGETS 中的目录和文件
        for target in self.TARGETS:
            instances.extend(
                self.scan(
                    directory=target.get("directory"),
                    filename=target.get("filename"),
                    skip_files=target.get("skip_files"),
                    skip_dirs=target.get("skip_dirs"),
                )
            )
        return instances

    def walk(
        self,
        directory: str,
        filename: str = None,
        skip_files: List[str] = [],
        skip_dirs: List[str] = [],
    ) -> List[str]:
        """
        遍历目录下的所有文件
        """
        results = []
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return results

        for root, dirs, files in os.walk(directory):
            # 过滤掉需要跳过的目录，直接修改 dirs 列表来影响 os.walk 的遍历
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                if filename is None or file == filename:
                    if file in skip_files:
                        continue
                    # 只处理 .py 文件
                    if file.endswith(".py"):
                        results.append(os.path.join(root, file))
        return results

    def scan(
        self,
        directory: str,
        filename: str = None,
        skip_files: List[str] = [],
        skip_dirs: List[str] = [],
    ) -> List[type]:
        """
        通用扫描方法

        Args:
            directory: 要扫描的目录路径
            filename: 要扫描的具体文件名，如果为 None 则扫描目录下所有 .py 文件
            skip_files: 要跳过的文件列表
            skip_dirs: 要跳过的目录列表
        Returns:
            扫描到的所有实例列表
        """
        instances = []

        files = self.walk(directory, filename, skip_files, skip_dirs)

        for file in files:
            instances.extend(
                self.import_and_extract_instances(file, file.split("/")[-1][:-3])
            )

        return instances

    def import_and_extract_instances(
        self, file_path: str, module_name: str
    ) -> List[type]:
        """
        导入模块并提取实例

        Args:
            file_path: 文件路径
            module_name: 模块名称

        Returns:
            提取到的实例列表
        """
        instances = []

        try:
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return instances

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 查找模块中所有的类并实例化
            for _, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, self.INSTANCE_TYPE)
                    and obj != self.INSTANCE_TYPE
                ):
                    try:
                        # 实例化命令类
                        instance = obj()
                        instances.append(instance)
                    except Exception as e:
                        print(f"Warning: Failed to instantiate {obj.__name__}: {e}")

        except Exception as e:
            # 静默跳过导入失败的模块，避免阻断整个发现过程
            print(f"Warning: Failed to import instances from {module_name}: {e}")

        return instances
