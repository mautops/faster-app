import importlib.util
import inspect
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class BaseDiscover:
    """
    自动发现基类

    扫描目录和文件，导入模块，提取指定类型的实例。
    """

    INSTANCE_TYPE: type | None = None
    TARGETS: list[dict[str, Any]] = []

    def discover(self) -> list[Any]:
        """扫描 TARGETS 中的目录和文件，提取所有 INSTANCE_TYPE 实例"""
        instances: list[Any] = []
        for target in self.TARGETS:
            instances.extend(
                self.scan(
                    directory=target.get("directory", ""),
                    filename=target.get("filename"),
                    skip_files=target.get("skip_files"),
                    skip_dirs=target.get("skip_dirs"),
                )
            )
        return instances

    def walk(
        self,
        directory: str,
        filename: str | None = None,
        skip_files: list[str] | None = None,
        skip_dirs: list[str] | None = None,
    ) -> list[str]:
        """
        Recursively walk through a directory and collect Python file paths.

        Args:
            directory: The directory path to walk through
            filename: Optional specific filename to look for
            skip_files: List of filenames to skip (default: empty list)
            skip_dirs: List of directory names to skip (default: empty list)

        Returns:
            List of absolute paths to Python files
        """
        skip_files = skip_files or []
        skip_dirs = skip_dirs or []
        results: list[str] = []

        if not os.path.exists(directory) or not os.path.isdir(directory):
            return results

        for root, dirs, files in os.walk(directory):
            # 过滤掉需要跳过的目录, 直接修改 dirs 列表来影响 os.walk 的遍历
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
        filename: str | None = None,
        skip_files: list[str] | None = None,
        skip_dirs: list[str] | None = None,
    ) -> list[Any]:
        """扫描目录中的 Python 文件，提取实例"""
        instances: list[Any] = []
        files = self.walk(directory, filename, skip_files or [], skip_dirs or [])
        for file in files:
            instances.extend(self.import_and_extract_instances(file, file.split("/")[-1][:-3]))
        return instances

    def import_and_extract_instances(self, file_path: str, module_name: str) -> list[Any]:
        """导入模块并提取 INSTANCE_TYPE 实例"""
        instances: list[Any] = []
        if self.INSTANCE_TYPE is None:
            return instances

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
                    and obj is not self.INSTANCE_TYPE
                    and not inspect.isabstract(obj)  # 跳过抽象类
                ):
                    try:
                        # 实例化命令类
                        instance = obj()
                        instances.append(instance)
                    except TypeError as e:
                        # 类型错误：可能是初始化参数不匹配
                        logger.warning(
                            f"Failed to instantiate {obj.__name__}: {e}. "
                            "Check if the class requires initialization parameters."
                        )
                    except Exception as e:
                        # 其他实例化错误
                        logger.warning(
                            f"Failed to instantiate {obj.__name__}: {type(e).__name__}: {e}"
                        )

        except ImportError as e:
            # 导入错误：模块不存在或依赖缺失
            logger.warning(
                f"Failed to import module {module_name}: {e}. "
                "Check if the module exists and all dependencies are installed."
            )
        except SyntaxError as e:
            # 语法错误：代码有问题
            logger.error(
                f"Syntax error in {module_name} at line {e.lineno}: {e}. "
                "Please fix the syntax error before using this module."
            )
        except Exception as e:
            # 其他异常：记录详细信息以便调试
            logger.warning(
                f"Unexpected error importing instances from {module_name}: {type(e).__name__}: {e}"
            )

        return instances
