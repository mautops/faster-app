"""
路由冲突检测器

检测路由注册时的冲突, 包括:
- 相同路径和HTTP方法的冲突
- 路径参数冲突
- 前缀冲突
"""

import re
from collections import defaultdict
from typing import Any

from fastapi import APIRouter
from fastapi.routing import APIRoute
from starlette.routing import Route


class RouteConflictError(Exception):
    """路由冲突异常"""

    def __init__(self, conflicts: list[dict[str, Any]]):
        self.conflicts = conflicts
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """格式化错误消息"""
        if not self.conflicts:
            return "发现路由冲突"

        lines = ["\n路由冲突检测失败! 发现以下冲突:\n"]
        for i, conflict in enumerate(self.conflicts, 1):
            lines.append(f"{i}. {conflict['type']}: {conflict['message']}")
            for route_info in conflict["routes"]:
                lines.append(f"   - {route_info['method']} {route_info['path']}")
                lines.append(f"     来源: {route_info['source']}")
            lines.append("")

        return "\n".join(lines)


class RouteValidator:
    """路由验证器"""

    def __init__(self):
        self.routes: list[dict[str, Any]] = []

    def collect_routes(self, router: APIRouter, source: str = "") -> None:
        """
        收集路由信息

        Args:
            router: APIRouter 实例
            source: 路由来源标识 (用于错误报告)
        """
        prefix = router.prefix or ""
        tags = router.tags or []

        # 遍历路由器的所有路由
        for route in router.routes:
            # FastAPI 使用 APIRoute, Starlette 使用 Route
            if isinstance(route, (Route, APIRoute)):
                path = prefix + route.path
                # 获取 HTTP 方法
                methods: set[str]
                if isinstance(route, APIRoute):
                    # FastAPI 的 APIRoute 有 methods 属性
                    methods = route.methods if hasattr(route, "methods") else set()
                else:
                    # Starlette 的 Route
                    methods = route.methods if hasattr(route, "methods") and route.methods else {"GET"}

                # 如果没有方法, 跳过 (可能是 WebSocket 或其他类型)
                if not methods:
                    continue

                for method in methods:
                    self.routes.append(
                        {
                            "method": method,
                            "path": path,
                            "normalized_path": self._normalize_path(path),
                            "source": source or f"Router(prefix='{prefix}', tags={tags})",
                            "router": router,
                        }
                    )

    def validate(self, raise_on_conflict: bool = True) -> list[dict[str, Any]]:
        """
        验证路由冲突

        Args:
            raise_on_conflict: 是否在发现冲突时抛出异常

        Returns:
            冲突列表
        """
        conflicts = []

        # 按方法和标准化路径分组
        route_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

        for route in self.routes:
            key = (route["method"], route["normalized_path"])
            route_groups[key].append(route)

        # 检测完全相同的路由
        for (method, normalized_path), routes in route_groups.items():
            if len(routes) > 1:
                conflicts.append(
                    {
                        "type": "完全冲突",
                        "message": f"方法 {method} 和路径 {normalized_path} 存在多个定义",
                        "routes": [
                            {
                                "method": r["method"],
                                "path": r["path"],
                                "source": r["source"],
                            }
                            for r in routes
                        ],
                    }
                )

        # 检测路径参数冲突 (例如: /users/{id} 和 /users/{name})
        path_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for route in self.routes:
            # 移除路径参数名称, 只保留位置
            pattern_path = self._pattern_path(route["path"])
            path_groups[pattern_path].append(route)

        for pattern_path, routes in path_groups.items():
            if len(routes) > 1:
                # 检查是否有不同的路径参数名称
                param_names = set()
                for route in routes:
                    params = self._extract_params(route["path"])
                    param_names.add(tuple(sorted(params)))

                # 如果参数名称不同, 但位置相同, 这是冲突
                if len(param_names) > 1:
                    # 按方法分组检查
                    method_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
                    for route in routes:
                        method_groups[route["method"]].append(route)

                    for method, method_routes in method_groups.items():
                        if len(method_routes) > 1:
                            conflicts.append(
                                {
                                    "type": "路径参数冲突",
                                    "message": f"方法 {method} 和路径模式 {pattern_path} 存在路径参数名称冲突",
                                    "routes": [
                                        {
                                            "method": r["method"],
                                            "path": r["path"],
                                            "source": r["source"],
                                        }
                                        for r in method_routes
                                    ],
                                }
                            )

        if conflicts and raise_on_conflict:
            raise RouteConflictError(conflicts)

        return conflicts

    def _normalize_path(self, path: str) -> str:
        """
        标准化路径, 将路径参数统一为 {param}

        Args:
            path: 原始路径

        Returns:
            标准化后的路径
        """
        # 将 {param} 或 {param:type} 统一为 {param}
        normalized = re.sub(r"\{([^:}]+)(:[^}]+)?\}", r"{\1}", path)
        return normalized

    def _pattern_path(self, path: str) -> str:
        """
        生成路径模式, 移除路径参数名称

        Args:
            path: 原始路径

        Returns:
            路径模式 (路径参数用 * 代替)
        """
        # 将路径参数替换为 *
        pattern = re.sub(r"\{[^}]+\}", "*", path)
        return pattern

    def _extract_params(self, path: str) -> list[str]:
        """
        提取路径中的参数名称

        Args:
            path: 路径字符串

        Returns:
            参数名称列表
        """
        params = re.findall(r"\{([^:}]+)", path)
        return params

    def get_summary(self) -> dict[str, Any]:
        """
        获取路由摘要信息

        Returns:
            包含路由统计信息的字典
        """
        total_routes = len(self.routes)
        methods_count: dict[str, int] = defaultdict(int)
        paths_count: dict[str, int] = defaultdict(int)

        for route in self.routes:
            methods_count[route["method"]] += 1
            paths_count[route["normalized_path"]] += 1

        return {
            "total_routes": total_routes,
            "methods": dict(methods_count),
            "unique_paths": len(paths_count),
            "paths": dict(paths_count),
        }
