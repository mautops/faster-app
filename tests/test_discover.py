"""
测试自动发现系统
"""

import os
import tempfile

import pytest


class TestBaseDiscover:
    """测试基础发现器"""

    def test_walk_directory(self):
        """测试目录遍历"""
        from faster_app.utils.discover import BaseDiscover

        discover = BaseDiscover()

        # 创建临时目录结构
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建文件
            os.makedirs(os.path.join(tmpdir, "subdir"))
            with open(os.path.join(tmpdir, "test.py"), "w") as f:
                f.write("# test")
            with open(os.path.join(tmpdir, "subdir", "sub.py"), "w") as f:
                f.write("# sub")
            with open(os.path.join(tmpdir, "not_python.txt"), "w") as f:
                f.write("text")

            # 遍历目录
            files = discover.walk(tmpdir)

            assert len(files) == 2
            assert any("test.py" in f for f in files)
            assert any("sub.py" in f for f in files)

    def test_walk_with_skip(self):
        """测试跳过文件和目录"""
        from faster_app.utils.discover import BaseDiscover

        discover = BaseDiscover()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "__pycache__"))
            with open(os.path.join(tmpdir, "test.py"), "w") as f:
                f.write("# test")
            with open(os.path.join(tmpdir, "__init__.py"), "w") as f:
                f.write("# init")
            with open(os.path.join(tmpdir, "__pycache__", "cached.py"), "w") as f:
                f.write("# cached")

            files = discover.walk(
                tmpdir,
                skip_dirs=["__pycache__"],
                skip_files=["__init__.py"],
            )

            assert len(files) == 1
            assert "test.py" in files[0]

    def test_walk_nonexistent_directory(self):
        """测试不存在的目录"""
        from faster_app.utils.discover import BaseDiscover

        discover = BaseDiscover()
        files = discover.walk("/nonexistent/directory")
        assert files == []


class TestRoutesDiscover:
    """测试路由发现器"""

    def test_discover_routes(self):
        """测试发现路由"""
        from faster_app.routes.discover import RoutesDiscover

        discover = RoutesDiscover()
        # 不验证，避免路由冲突错误
        routes = discover.discover(validate=False)

        # 应该发现一些路由
        assert isinstance(routes, list)

    def test_routes_are_api_routers(self):
        """测试发现的是 APIRouter 实例"""
        from fastapi import APIRouter

        from faster_app.routes.discover import RoutesDiscover

        discover = RoutesDiscover()
        routes = discover.discover(validate=False)

        for route in routes:
            assert isinstance(route, APIRouter)


class TestMiddlewareDiscover:
    """测试中间件发现器"""

    def test_discover_middlewares(self):
        """测试发现中间件"""
        from faster_app.middleware.discover import MiddlewareDiscover

        discover = MiddlewareDiscover()
        middlewares = discover.discover()

        assert isinstance(middlewares, list)
        assert len(middlewares) > 0

    def test_middleware_has_required_fields(self):
        """测试中间件配置包含必需字段"""
        from faster_app.middleware.discover import MiddlewareDiscover

        discover = MiddlewareDiscover()
        middlewares = discover.discover()

        for mw in middlewares:
            assert "class" in mw
            assert "kwargs" in mw
            assert "priority" in mw

    def test_middleware_sorted_by_priority(self):
        """测试中间件按优先级排序"""
        from faster_app.middleware.discover import MiddlewareDiscover

        discover = MiddlewareDiscover()
        middlewares = discover.discover()

        priorities = [mw["priority"] for mw in middlewares]
        assert priorities == sorted(priorities)


class TestMiddlewarePriority:
    """测试中间件优先级常量"""

    def test_priority_constants(self):
        """测试优先级常量值"""
        from faster_app.middleware.discover import (
            PRIORITY_CORS,
            PRIORITY_DEFAULT,
            PRIORITY_GZIP,
            PRIORITY_TRUSTED_HOST,
        )

        assert PRIORITY_CORS == 12
        assert PRIORITY_TRUSTED_HOST == 13
        assert PRIORITY_GZIP == 21
        assert PRIORITY_DEFAULT == 999

    def test_priority_order(self):
        """测试优先级顺序正确"""
        from faster_app.middleware.discover import (
            PRIORITY_CORS,
            PRIORITY_DEFAULT,
            PRIORITY_GZIP,
            PRIORITY_TRUSTED_HOST,
        )

        # 安全中间件应该在压缩之前
        assert PRIORITY_CORS < PRIORITY_GZIP
        assert PRIORITY_TRUSTED_HOST < PRIORITY_GZIP

        # 默认优先级最低
        assert PRIORITY_DEFAULT > PRIORITY_GZIP
