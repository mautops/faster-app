import logging

from fastapi import APIRouter

from faster_app.routes.validator import RouteConflictError, RouteValidator
from faster_app.settings import configs
from faster_app.utils import BASE_DIR
from faster_app.utils.discover import BaseDiscover

logger = logging.getLogger(__name__)


class RoutesDiscover(BaseDiscover):
    INSTANCE_TYPE = APIRouter
    TARGETS = [
        {"directory": "apps", "skip_dirs": ["__pycache__"]},
        {"directory": f"{BASE_DIR}/routes/builtins", "skip_dirs": ["__pycache__"]},
    ]

    def import_and_extract_instances(self, file_path: str, module_name: str) -> list[APIRouter]:
        """
        导入模块并提取路由实例
        对于路由, 我们查找已经实例化的 APIRouter 对象
        """
        instances: list[APIRouter] = []

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
            # 静默跳过导入失败的模块, 避免阻断整个发现过程
            logger.warning(f"Failed to import routes from {module_name}: {e}")

        return instances

    def discover(self, validate: bool = True) -> list[APIRouter]:
        """
        发现并验证路由

        Args:
            validate: 是否进行路由冲突检测

        Returns:
            路由列表

        Raises:
            RouteConflictError: 如果发现路由冲突且 validate=True
        """
        routes = super().discover()

        if validate and routes:
            validator = RouteValidator()

            # 收集所有路由信息
            for i, router in enumerate(routes):
                # 构建路由来源标识
                source_parts = []
                if router.prefix:
                    source_parts.append(f"prefix='{router.prefix}'")
                if router.tags:
                    tags_str = (
                        ", ".join(router.tags)
                        if isinstance(router.tags, list)
                        else str(router.tags)
                    )
                    source_parts.append(f"tags=[{tags_str}]")

                source = f"Router #{i + 1}"
                if source_parts:
                    source += f" ({', '.join(source_parts)})"

                validator.collect_routes(router, source)

            # 验证路由冲突
            try:
                conflicts = validator.validate(raise_on_conflict=True)
                if conflicts:
                    logger.error(f"发现 {len(conflicts)} 个路由冲突")
            except RouteConflictError as e:
                logger.error(str(e))
                # 在开发模式下允许继续运行, 但记录错误
                if configs.DEBUG:
                    logger.warning("开发模式下允许路由冲突, 应用将继续启动")
                else:
                    # 生产模式下抛出异常
                    raise

            # 记录路由摘要
            summary = validator.get_summary()
            logger.debug(
                f"路由发现完成: 共 {summary['total_routes']} 个路由, "
                f"{summary['unique_paths']} 个唯一路径"
            )

        return routes
