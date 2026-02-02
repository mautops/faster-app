"""
测试异常处理系统
"""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient


class TestFasterAppError:
    """测试 FasterAppError 基类"""

    def test_default_values(self):
        """测试默认值"""
        from faster_app.exceptions import FasterAppError

        error = FasterAppError()
        assert error.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert error.code == 500
        assert error.message == "操作失败"
        assert error.data is None

    def test_custom_values(self):
        """测试自定义值"""
        from faster_app.exceptions import FasterAppError

        error = FasterAppError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=1001,
            message="自定义错误",
            data={"field": "value"},
        )
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.code == 1001
        assert error.message == "自定义错误"
        assert error.data == {"field": "value"}


class TestBuiltinErrors:
    """测试内置异常类"""

    def test_bad_request_error(self):
        """测试 BadRequestError"""
        from faster_app.exceptions import BadRequestError

        error = BadRequestError(message="请求无效")
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.message == "请求无效"

    def test_unauthorized_error(self):
        """测试 UnauthorizedError"""
        from faster_app.exceptions import UnauthorizedError

        error = UnauthorizedError()
        assert error.status_code == status.HTTP_401_UNAUTHORIZED

    def test_forbidden_error(self):
        """测试 ForbiddenError"""
        from faster_app.exceptions import ForbiddenError

        error = ForbiddenError()
        assert error.status_code == status.HTTP_403_FORBIDDEN

    def test_not_found_error(self):
        """测试 NotFoundError"""
        from faster_app.exceptions import NotFoundError

        error = NotFoundError()
        assert error.status_code == status.HTTP_404_NOT_FOUND

    def test_validation_error(self):
        """测试 ValidationError"""
        from faster_app.exceptions import ValidationError

        error = ValidationError(message="验证失败")
        assert error.status_code == status.HTTP_400_BAD_REQUEST

    def test_too_many_requests_error(self):
        """测试 TooManyRequestsError"""
        from faster_app.exceptions import TooManyRequestsError

        error = TooManyRequestsError()
        assert error.status_code == status.HTTP_429_TOO_MANY_REQUESTS


class TestExceptionManager:
    """测试异常管理器"""

    def test_register_handler(self):
        """测试注册异常处理器"""
        from faster_app.exceptions.manager import ExceptionManager

        manager = ExceptionManager()

        async def custom_handler(request, exc):
            pass

        manager.register(ValueError, custom_handler)
        assert manager.get_handler(ValueError) is custom_handler

    def test_register_duplicate_handler(self):
        """测试重复注册抛出错误"""
        from faster_app.exceptions.manager import ExceptionManager

        manager = ExceptionManager()

        async def handler1(request, exc):
            pass

        async def handler2(request, exc):
            pass

        manager.register(ValueError, handler1)

        with pytest.raises(ValueError, match="已注册"):
            manager.register(ValueError, handler2)

    def test_unregister_handler(self):
        """测试取消注册"""
        from faster_app.exceptions.manager import ExceptionManager

        manager = ExceptionManager()

        async def handler(request, exc):
            pass

        manager.register(ValueError, handler)
        manager.unregister(ValueError)

        assert manager.get_handler(ValueError) is None

    def test_unregister_nonexistent_handler(self):
        """测试取消注册不存在的处理器"""
        from faster_app.exceptions.manager import ExceptionManager

        manager = ExceptionManager()

        with pytest.raises(KeyError, match="未注册"):
            manager.unregister(ValueError)

    def test_register_defaults(self):
        """测试注册默认处理器"""
        from faster_app.exceptions.manager import ExceptionManager

        manager = ExceptionManager()
        manager.register_defaults()

        # 应该注册了 FasterAppError 处理器
        from faster_app.exceptions import FasterAppError

        assert manager.get_handler(FasterAppError) is not None
        assert manager.get_handler(Exception) is not None

    def test_register_defaults_idempotent(self):
        """测试多次注册默认处理器是幂等的"""
        from faster_app.exceptions.manager import ExceptionManager

        manager = ExceptionManager()
        manager.register_defaults()
        manager.register_defaults()  # 第二次应该被跳过

    def test_list_handlers(self):
        """测试列出所有处理器"""
        from faster_app.exceptions.manager import ExceptionManager

        manager = ExceptionManager()

        async def handler(request, exc):
            pass

        manager.register(ValueError, handler)
        handlers = manager.list_handlers()

        assert len(handlers) == 1
        assert handlers[0] == (ValueError, handler)

    def test_clear(self):
        """测试清空处理器"""
        from faster_app.exceptions.manager import ExceptionManager

        manager = ExceptionManager()
        manager.register_defaults()
        manager.clear()

        assert len(manager.list_handlers()) == 0

    def test_apply_to_app(self):
        """测试应用处理器到 FastAPI 应用"""
        from faster_app.exceptions import FasterAppError, get_manager
        from faster_app.exceptions.manager import reset_manager

        reset_manager()
        app = FastAPI()
        manager = get_manager()
        manager.apply(app)

        # 添加一个会抛出异常的路由
        @app.get("/error")
        async def raise_error():
            raise FasterAppError(message="测试错误")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/error")

        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "测试错误"


class TestGlobalManager:
    """测试全局管理器"""

    def test_get_manager_singleton(self):
        """测试获取单例管理器"""
        from faster_app.exceptions import get_manager
        from faster_app.exceptions.manager import reset_manager

        reset_manager()
        manager1 = get_manager()
        manager2 = get_manager()

        assert manager1 is manager2

    def test_reset_manager(self):
        """测试重置管理器"""
        from faster_app.exceptions import get_manager
        from faster_app.exceptions.manager import reset_manager

        manager1 = get_manager()
        reset_manager()
        manager2 = get_manager()

        assert manager1 is not manager2


class TestExceptionHandlers:
    """测试异常处理器"""

    def test_faster_app_exception_handler(self):
        """测试 FasterAppError 处理器"""
        from faster_app.exceptions import FasterAppError, get_manager
        from faster_app.exceptions.manager import reset_manager

        reset_manager()
        app = FastAPI()
        get_manager().apply(app)

        @app.get("/test")
        async def test_route():
            raise FasterAppError(
                status_code=400,
                code=1001,
                message="测试错误",
                data={"key": "value"},
            )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test")

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == 1001
        assert data["message"] == "测试错误"
        assert data["data"] == {"key": "value"}

    def test_validation_exception_handler(self):
        """测试验证异常处理器"""
        from pydantic import BaseModel

        from faster_app.exceptions import get_manager
        from faster_app.exceptions.manager import reset_manager

        reset_manager()
        app = FastAPI()
        get_manager().apply(app)

        class Item(BaseModel):
            name: str
            price: float

        @app.post("/items")
        async def create_item(item: Item):
            return item

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/items", json={"name": "test"})  # 缺少 price

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["code"] == 422
