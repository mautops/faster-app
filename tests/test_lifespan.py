"""
测试生命周期管理
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI


class TestLifespanManager:
    """测试 Lifespan 管理器"""

    def test_register_lifespan(self):
        """测试注册 lifespan"""
        from faster_app.lifespan.manager import LifespanManager

        manager = LifespanManager()

        @asynccontextmanager
        async def test_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            yield

        manager.register("test", test_lifespan)
        assert manager.is_enabled("test") is True

    def test_register_duplicate(self):
        """测试重复注册抛出错误"""
        from faster_app.lifespan.manager import LifespanManager

        manager = LifespanManager()

        @asynccontextmanager
        async def test_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            yield

        manager.register("test", test_lifespan)

        with pytest.raises(ValueError, match="已注册"):
            manager.register("test", test_lifespan)

    def test_enable_disable(self):
        """测试启用和禁用"""
        from faster_app.lifespan.manager import LifespanManager

        manager = LifespanManager()

        @asynccontextmanager
        async def test_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            yield

        manager.register("test", test_lifespan, enabled=False)
        assert manager.is_enabled("test") is False

        manager.enable("test")
        assert manager.is_enabled("test") is True

        manager.disable("test")
        assert manager.is_enabled("test") is False

    def test_enable_nonexistent(self):
        """测试启用不存在的 lifespan"""
        from faster_app.lifespan.manager import LifespanManager

        manager = LifespanManager()

        with pytest.raises(KeyError, match="不存在"):
            manager.enable("nonexistent")

    def test_list_enabled(self):
        """测试列出启用的 lifespan"""
        from faster_app.lifespan.manager import LifespanManager

        manager = LifespanManager()

        @asynccontextmanager
        async def ls1(app: FastAPI) -> AsyncGenerator[None, None]:
            yield

        @asynccontextmanager
        async def ls2(app: FastAPI) -> AsyncGenerator[None, None]:
            yield

        @asynccontextmanager
        async def ls3(app: FastAPI) -> AsyncGenerator[None, None]:
            yield

        manager.register("ls1", ls1, priority=2)
        manager.register("ls2", ls2, priority=1, enabled=False)
        manager.register("ls3", ls3, priority=0)

        enabled = manager.list_enabled()
        assert enabled == ["ls3", "ls1"]  # 按优先级排序，不包含禁用的

    def test_build_empty(self):
        """测试构建空 lifespan"""
        from faster_app.lifespan.manager import LifespanManager

        manager = LifespanManager()
        lifespan = manager.build()

        # 应该返回一个空的 lifespan 函数
        assert callable(lifespan)

    def test_clear(self):
        """测试清空"""
        from faster_app.lifespan.manager import LifespanManager

        manager = LifespanManager()

        @asynccontextmanager
        async def test_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            yield

        manager.register("test", test_lifespan)
        manager.clear()

        assert manager.list_enabled() == []


class TestGlobalLifespanManager:
    """测试全局 Lifespan 管理器"""

    def test_get_manager_singleton(self):
        """测试获取单例管理器"""
        from faster_app.lifespan.manager import get_manager, reset_manager

        reset_manager()
        manager1 = get_manager()
        manager2 = get_manager()

        assert manager1 is manager2

    def test_reset_manager(self):
        """测试重置管理器"""
        from faster_app.lifespan.manager import get_manager, reset_manager

        manager1 = get_manager()
        reset_manager()
        manager2 = get_manager()

        assert manager1 is not manager2


class TestCombineLifespans:
    """测试组合 lifespan"""

    @pytest.mark.asyncio
    async def test_combine_multiple(self):
        """测试组合多个 lifespan"""
        from faster_app.lifespan.combine import combine_lifespans

        order = []

        @asynccontextmanager
        async def ls1(app: FastAPI) -> AsyncGenerator[None, None]:
            order.append("ls1_start")
            yield
            order.append("ls1_end")

        @asynccontextmanager
        async def ls2(app: FastAPI) -> AsyncGenerator[None, None]:
            order.append("ls2_start")
            yield
            order.append("ls2_end")

        combined = combine_lifespans(ls1, ls2)
        app = FastAPI()

        async with combined(app):
            order.append("middle")

        # 验证执行顺序
        assert order == ["ls1_start", "ls2_start", "middle", "ls2_end", "ls1_end"]

    @pytest.mark.asyncio
    async def test_combine_single(self):
        """测试单个 lifespan"""
        from faster_app.lifespan.combine import combine_lifespans

        called = []

        @asynccontextmanager
        async def single_ls(app: FastAPI) -> AsyncGenerator[None, None]:
            called.append("start")
            yield
            called.append("end")

        combined = combine_lifespans(single_ls)
        app = FastAPI()

        async with combined(app):
            pass

        assert called == ["start", "end"]

    @pytest.mark.asyncio
    async def test_combine_empty(self):
        """测试空 lifespan 列表"""
        from faster_app.lifespan.combine import combine_lifespans

        combined = combine_lifespans()
        app = FastAPI()

        # 应该不会抛出错误
        async with combined(app):
            pass
