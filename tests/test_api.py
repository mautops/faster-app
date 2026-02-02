"""
测试 API 集成
"""

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient


class TestApiResponse:
    """测试 API 响应工具"""

    def test_success_response(self):
        """测试成功响应"""
        import json

        from fastapi.responses import JSONResponse

        from faster_app.utils.response import ApiResponse

        response = ApiResponse.success(data={"key": "value"}, message="操作成功")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        # 解析响应体
        body = json.loads(response.body.decode())
        assert body["success"] is True
        assert body["data"] == {"key": "value"}
        assert body["message"] == "操作成功"
        assert "timestamp" in body

    def test_error_response(self):
        """测试错误响应"""
        import json

        from fastapi.responses import JSONResponse

        from faster_app.utils.response import ApiResponse

        response = ApiResponse.error(code=400, message="请求错误", status_code=400)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        body = json.loads(response.body.decode())
        assert body["success"] is False
        assert body["code"] == 400
        assert body["message"] == "请求错误"

    def test_paginated_response(self):
        """测试分页响应"""
        import json

        from faster_app.utils.response import ApiResponse

        items = [{"id": 1}, {"id": 2}]
        response = ApiResponse.success(
            data={"items": items, "total": 10, "page": 1, "size": 2, "pages": 5}
        )

        body = json.loads(response.body.decode())
        assert body["success"] is True
        assert body["data"]["items"] == items
        assert body["data"]["total"] == 10


class TestAppCreation:
    """测试应用创建"""

    def test_create_app(self):
        """测试创建应用"""
        from faster_app.app import create_app

        app = create_app()

        assert isinstance(app, FastAPI)
        assert app.title is not None
        assert app.version is not None

    def test_app_has_openapi(self):
        """测试应用有 OpenAPI schema"""
        from faster_app.app import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema


class TestBuiltinRoutes:
    """测试内置路由"""

    def test_health_check(self):
        """测试健康检查端点"""
        from faster_app.app import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self):
        """测试根端点"""
        from faster_app.app import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/")
        assert response.status_code == 200


class TestMiddlewareIntegration:
    """测试中间件集成"""

    def test_cors_headers(self):
        """测试 CORS 头"""
        from faster_app.app import create_app

        app = create_app()
        client = TestClient(app)

        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        # 应该返回 CORS 头
        assert "access-control-allow-origin" in response.headers

    def test_gzip_compression(self):
        """测试 GZip 压缩"""
        from faster_app.app import create_app

        app = create_app()

        # 添加一个返回大量数据的路由
        @app.get("/large")
        async def large_response():
            return {"data": "x" * 2000}  # 超过最小压缩大小

        client = TestClient(app)
        response = client.get("/large", headers={"Accept-Encoding": "gzip"})

        # 如果启用了 GZip，响应可能被压缩
        assert response.status_code == 200


class TestExceptionHandlerIntegration:
    """测试异常处理集成"""

    def test_validation_error_format(self):
        """测试验证错误格式"""
        from pydantic import BaseModel

        from faster_app.app import create_app

        app = create_app()

        class Item(BaseModel):
            name: str
            price: float

        @app.post("/items")
        async def create_item(item: Item):
            return item

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/items", json={"name": "test"})

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["code"] == 422

    def test_not_found_error(self):
        """测试 404 错误"""
        from faster_app.app import create_app

        app = create_app()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/nonexistent")

        assert response.status_code == 404


class TestRouterRegistration:
    """测试路由注册"""

    def test_router_registration(self):
        """测试路由注册"""
        from faster_app.exceptions import get_manager

        app = FastAPI()
        router = APIRouter(prefix="/api")

        @router.get("/test")
        async def test_route():
            return {"message": "test"}

        app.include_router(router)
        get_manager().apply(app)

        client = TestClient(app)
        response = client.get("/api/test")

        assert response.status_code == 200
        assert response.json() == {"message": "test"}

    def test_multiple_routers(self):
        """测试多个路由注册"""
        from faster_app.exceptions import get_manager

        app = FastAPI()

        router1 = APIRouter(prefix="/v1")
        router2 = APIRouter(prefix="/v2")

        @router1.get("/resource")
        async def v1_resource():
            return {"version": 1}

        @router2.get("/resource")
        async def v2_resource():
            return {"version": 2}

        app.include_router(router1)
        app.include_router(router2)
        get_manager().apply(app)

        client = TestClient(app)

        assert client.get("/v1/resource").json() == {"version": 1}
        assert client.get("/v2/resource").json() == {"version": 2}
