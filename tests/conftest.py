"""
测试配置和共享 fixtures
"""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel
from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator

# 设置测试环境变量
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("DB_URL", "sqlite://:memory:")


# ============ 测试模型 ============


class TestModel(Model):
    """测试用模型"""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "test_model"


TestModelSchema = pydantic_model_creator(TestModel, name="TestModelSchema")


class TestCreateSchema(BaseModel):
    """测试创建 Schema"""

    name: str
    description: str | None = None
    is_active: bool = True


class TestUpdateSchema(BaseModel):
    """测试更新 Schema"""

    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


# ============ Fixtures ============


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app() -> FastAPI:
    """创建测试用 FastAPI 应用"""
    from faster_app.exceptions import get_manager

    app = FastAPI(title="Test App")
    get_manager().apply(app)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """创建同步测试客户端"""
    return TestClient(app)


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """创建异步测试客户端"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
def mock_request() -> MagicMock:
    """创建模拟请求对象"""
    request = MagicMock()
    request.headers = {}
    request.query_params = {}
    request.state = MagicMock()
    request.state.user = None
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    return request


@pytest.fixture
def mock_user() -> MagicMock:
    """创建模拟用户对象"""
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    user.is_admin = False
    user.is_superuser = False
    return user


@pytest.fixture
def admin_user() -> MagicMock:
    """创建模拟管理员用户"""
    user = MagicMock()
    user.id = 1
    user.username = "admin"
    user.is_admin = True
    user.is_superuser = True
    return user


@pytest.fixture
def auth_request(mock_request: MagicMock, mock_user: MagicMock) -> MagicMock:
    """创建已认证的请求"""
    mock_request.state.user = mock_user
    return mock_request


@pytest.fixture
def jwt_token() -> str:
    """创建测试用 JWT token"""
    try:
        import jwt

        payload = {
            "user_id": 1,
            "username": "testuser",
            "is_admin": False,
        }
        return jwt.encode(payload, "test-secret-key", algorithm="HS256")
    except ImportError:
        pytest.skip("PyJWT not installed")


@pytest.fixture
def auth_headers(jwt_token: str) -> dict[str, str]:
    """创建带认证的请求头"""
    return {"Authorization": f"Bearer {jwt_token}"}


# ============ 数据库 Fixtures ============


@pytest.fixture
async def init_db() -> AsyncGenerator[None, None]:
    """初始化测试数据库"""
    from tortoise import Tortoise

    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["tests.conftest"]},
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture
async def test_instance(init_db: None) -> TestModel:
    """创建测试模型实例"""
    return await TestModel.create(name="Test Item", description="Test Description")


# ============ ViewSet Fixtures ============


@pytest.fixture
def test_viewset_class() -> type:
    """创建测试用 ViewSet 类"""
    from faster_app.viewsets import ModelViewSet

    class TestViewSet(ModelViewSet):
        model = TestModel
        schema = TestModelSchema
        create_schema = TestCreateSchema
        update_schema = TestUpdateSchema

    return TestViewSet


@pytest.fixture
def test_viewset(test_viewset_class: type) -> Any:
    """创建测试用 ViewSet 实例"""
    return test_viewset_class()
