"""
依赖图分析工具

分析应用之间的依赖关系, 检测循环依赖, 生成依赖图。
"""

import ast
import logging
import os
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """依赖关系分析器"""

    def __init__(self, apps_dir: str = "apps"):
        """
        初始化依赖分析器

        Args:
            apps_dir: 应用目录路径
        """
        self.apps_dir = apps_dir
        self.dependencies: dict[str, set[str]] = defaultdict(set)
        self.app_modules: dict[str, str] = {}  # app_name -> module_path

    def analyze(self) -> dict[str, Any]:
        """
        分析所有应用的依赖关系

        Returns:
            包含依赖信息和循环依赖的字典
        """
        # 扫描所有应用
        self._scan_apps()

        # 分析每个应用的依赖
        for app_name, module_path in self.app_modules.items():
            self._analyze_app_dependencies(app_name, module_path)

        # 检测循环依赖
        cycles = self._detect_cycles()

        return {
            "dependencies": {app: list(deps) for app, deps in self.dependencies.items()},
            "cycles": cycles,
            "apps": list(self.app_modules.keys()),
        }

    def _scan_apps(self) -> None:
        """扫描应用目录, 收集所有应用模块"""
        if not os.path.exists(self.apps_dir):
            logger.warning(f"应用目录不存在: {self.apps_dir}")
            return

        for item in os.listdir(self.apps_dir):
            app_path = os.path.join(self.apps_dir, item)
            # 检查是否有 models.py 或 routes.py, 有则认为是应用
            if (
                os.path.isdir(app_path)
                and not item.startswith("__")
                and (
                    os.path.exists(os.path.join(app_path, "models.py"))
                    or os.path.exists(os.path.join(app_path, "routes.py"))
                )
            ):
                self.app_modules[item] = app_path

    def _analyze_app_dependencies(self, app_name: str, app_path: str) -> None:
        """
        分析单个应用的依赖关系

        Args:
            app_name: 应用名称
            app_path: 应用路径
        """
        # 分析所有 Python 文件
        for root, dirs, files in os.walk(app_path):
            # 跳过 __pycache__ 目录
            dirs[:] = [d for d in dirs if not d.startswith("__")]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._analyze_file_dependencies(app_name, file_path)

    def _analyze_file_dependencies(self, app_name: str, file_path: str) -> None:
        """
        分析单个文件的依赖关系

        Args:
            app_name: 应用名称
            file_path: 文件路径
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dep_app = self._extract_app_from_import(alias.name)
                        if dep_app and dep_app != app_name:
                            self.dependencies[app_name].add(dep_app)

                elif isinstance(node, ast.ImportFrom) and node.module:
                    dep_app = self._extract_app_from_import(node.module)
                    if dep_app and dep_app != app_name:
                        self.dependencies[app_name].add(dep_app)

        except Exception as e:
            logger.warning(f"分析文件依赖失败 {file_path}: {e}")

    def _extract_app_from_import(self, import_path: str) -> str | None:
        """
        从导入路径中提取应用名称

        Args:
            import_path: 导入路径, 如 "apps.demo.models" 或 "faster_app.apps.demo.models"

        Returns:
            应用名称, 如果不在 apps 目录下则返回 None
        """
        parts = import_path.split(".")

        # 查找 "apps" 在路径中的位置
        if "apps" in parts:
            apps_index = parts.index("apps")
            if apps_index + 1 < len(parts):
                app_name = parts[apps_index + 1]
                # 验证这个应用确实存在
                if app_name in self.app_modules:
                    return app_name

        return None

    def _detect_cycles(self) -> list[list[str]]:
        """
        检测循环依赖

        Returns:
            循环依赖列表, 每个循环是一个应用名称列表
        """
        cycles: list[list[str]] = []
        visited = set()
        rec_stack = set()

        def dfs(app: str, path: list[str]) -> None:
            """深度优先搜索检测循环"""
            if app in rec_stack:
                # 找到循环
                cycle_start = path.index(app)
                cycle = path[cycle_start:] + [app]
                # 规范化循环(从最小应用名开始)
                if len(cycle) > 1:  # 确保循环至少有两个节点
                    min_index = min(range(len(cycle) - 1), key=lambda i: cycle[i])
                    normalized_cycle = cycle[min_index:-1] + [cycle[min_index]]
                    # 检查是否已存在相同的循环(考虑顺序)
                    cycle_set = set(normalized_cycle)
                    if not any(set(c) == cycle_set for c in cycles):
                        cycles.append(normalized_cycle)
                return

            if app in visited:
                return

            visited.add(app)
            rec_stack.add(app)

            for dep in self.dependencies.get(app, set()):
                dfs(dep, path + [app])

            rec_stack.remove(app)

        # 对每个应用进行 DFS
        for app in self.dependencies:
            if app not in visited:
                dfs(app, [])

        return cycles

    def get_dependency_graph(self) -> dict[str, Any]:
        """
        获取依赖图数据

        Returns:
            依赖图数据字典
        """
        analysis = self.analyze()

        # 构建节点和边
        nodes = []
        edges = []

        for app in analysis["apps"]:
            nodes.append({"id": app, "label": app})

        for app, deps in analysis["dependencies"].items():
            for dep in deps:
                edges.append({"source": app, "target": dep})

        return {
            "nodes": nodes,
            "edges": edges,
            "cycles": analysis["cycles"],
        }

    def format_text_output(self) -> str:
        """
        格式化文本输出

        Returns:
            格式化的文本字符串
        """
        analysis = self.analyze()
        lines = []

        lines.append("=" * 60)
        lines.append("依赖关系分析报告")
        lines.append("=" * 60)
        lines.append("")

        # 应用列表
        lines.append(f"发现 {len(analysis['apps'])} 个应用:")
        for app in sorted(analysis["apps"]):
            lines.append(f"  - {app}")
        lines.append("")

        # 依赖关系
        lines.append("依赖关系:")
        if analysis["dependencies"]:
            for app in sorted(analysis["dependencies"].keys()):
                deps = analysis["dependencies"][app]
                if deps:
                    deps_str = ", ".join(sorted(deps))
                    lines.append(f"  {app} -> [{deps_str}]")
                else:
                    lines.append(f"  {app} -> []")
        else:
            lines.append("  无依赖关系")
        lines.append("")

        # 循环依赖
        if analysis["cycles"]:
            lines.append("⚠️  检测到循环依赖:")
            for i, cycle in enumerate(analysis["cycles"], 1):
                cycle_str = " -> ".join(cycle) + " -> " + cycle[0]
                lines.append(f"  循环 {i}: {cycle_str}")
        else:
            lines.append("✅ 未检测到循环依赖")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)
