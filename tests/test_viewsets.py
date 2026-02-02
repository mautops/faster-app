"""
测试 ViewSet 系统
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel


class TestViewSetBase:
    """测试 ViewSet 基类"""

    def test_viewset_requires_model(self):
        """测试 ViewSet 必须定义 model"""
        from faster_app.viewsets.base import ViewSet

        class InvalidViewSet(ViewSet):
            model = None

        with pytest.raises(ValueError, match="必须定义 model"):
            InvalidViewSet()

    def test_auto_generate_schema(self):
        """测试自动生成 schema"""
        from tortoise import Model, fields
        from tortoise.contrib.pydantic import PydanticModel

        from faster_app.viewsets.base import ViewSet

        class TestModel(Model):
            id = fields.IntField(pk=True)
            name = fields.CharField(max_length=100)

            class Meta:
                table = "test_viewset_model"

        class TestViewSet(ViewSet):
            model = TestModel

        viewset = TestViewSet()
        assert viewset.schema is not None
        assert issubclass(viewset.schema, PydanticModel)

    def test_get_queryset(self):
        """测试获取查询集方法存在且可调用"""
        from tortoise import Model, fields

        from faster_app.viewsets.base import ViewSet

        class TestModel(Model):
            id = fields.IntField(pk=True)

            class Meta:
                table = "test_viewset_qs"

        class TestViewSet(ViewSet):
            model = TestModel

        viewset = TestViewSet()

        # 验证 get_queryset 方法存在且可调用
        assert hasattr(viewset, "get_queryset")
        assert callable(viewset.get_queryset)
        # 注: 实际调用需要数据库连接,在集成测试中测试

    def test_get_schema(self):
        """测试获取 schema"""
        from tortoise import Model, fields

        from faster_app.viewsets.base import ViewSet

        class TestModel(Model):
            id = fields.IntField(pk=True)

            class Meta:
                table = "test_viewset_schema"

        class CreateSchema(BaseModel):
            name: str

        class UpdateSchema(BaseModel):
            name: str | None = None

        class TestViewSet(ViewSet):
            model = TestModel
            create_schema = CreateSchema
            update_schema = UpdateSchema

        viewset = TestViewSet()

        assert viewset.get_schema("create") is CreateSchema
        assert viewset.get_schema("update") is UpdateSchema
        assert viewset.get_schema("list") is viewset.schema

    def test_get_object_name(self):
        """测试获取对象名称"""
        from tortoise import Model, fields

        from faster_app.viewsets.base import ViewSet

        class TestModel(Model):
            id = fields.IntField(pk=True)

            class Meta:
                table = "test_viewset_name"

        class TestViewSet(ViewSet):
            model = TestModel

        viewset = TestViewSet()
        assert viewset.get_object_name() == "TestModel"


class TestViewSetPermissions:
    """测试 ViewSet 权限相关方法"""

    def test_get_permissions(self):
        """测试获取权限实例"""
        from tortoise import Model, fields

        from faster_app.viewsets.base import ViewSet
        from faster_app.viewsets.permissions import AllowAny, IsAuthenticated

        class TestModel(Model):
            id = fields.IntField(pk=True)

            class Meta:
                table = "test_viewset_perm"

        class TestViewSet(ViewSet):
            model = TestModel
            permission_classes = [AllowAny, IsAuthenticated]

        viewset = TestViewSet()
        permissions = viewset.get_permissions()

        assert len(permissions) == 2
        assert isinstance(permissions[0], AllowAny)
        assert isinstance(permissions[1], IsAuthenticated)

    def test_get_authenticators(self):
        """测试获取认证实例"""
        from tortoise import Model, fields

        from faster_app.viewsets.authentication import JWTAuthentication, NoAuthentication
        from faster_app.viewsets.base import ViewSet

        class TestModel(Model):
            id = fields.IntField(pk=True)

            class Meta:
                table = "test_viewset_auth"

        class TestViewSet(ViewSet):
            model = TestModel
            authentication_classes = [NoAuthentication, JWTAuthentication]

        viewset = TestViewSet()
        authenticators = viewset.get_authenticators()

        assert len(authenticators) == 2
        assert isinstance(authenticators[0], NoAuthentication)
        assert isinstance(authenticators[1], JWTAuthentication)


class TestViewSetThrottling:
    """测试 ViewSet 限流相关方法"""

    def test_get_throttles(self):
        """测试获取限流实例"""
        from tortoise import Model, fields

        from faster_app.viewsets.base import ViewSet
        from faster_app.viewsets.throttling import NoThrottle, UserRateThrottle

        class TestModel(Model):
            id = fields.IntField(pk=True)

            class Meta:
                table = "test_viewset_throttle"

        class TestViewSet(ViewSet):
            model = TestModel
            throttle_classes = [UserRateThrottle, NoThrottle]

        viewset = TestViewSet()
        throttles = viewset.get_throttles()

        assert len(throttles) == 2
        assert isinstance(throttles[0], UserRateThrottle)
        assert isinstance(throttles[1], NoThrottle)

    @pytest.mark.asyncio
    async def test_check_throttles_allowed(self, mock_request: MagicMock):
        """测试限流检查通过"""
        from tortoise import Model, fields

        from faster_app.viewsets.base import ViewSet
        from faster_app.viewsets.throttling import NoThrottle

        class TestModel(Model):
            id = fields.IntField(pk=True)

            class Meta:
                table = "test_viewset_throttle_ok"

        class TestViewSet(ViewSet):
            model = TestModel
            throttle_classes = [NoThrottle]

        viewset = TestViewSet()
        # 不应该抛出异常
        await viewset.check_throttles(mock_request)

    @pytest.mark.asyncio
    async def test_check_throttles_denied(self, mock_request: MagicMock):
        """测试限流检查被拒绝"""
        from tortoise import Model, fields

        from faster_app.exceptions import TooManyRequestsError
        from faster_app.viewsets.base import ViewSet
        from faster_app.viewsets.throttling import BaseThrottle

        class AlwaysDenyThrottle(BaseThrottle):
            async def allow_request(self, request, view):
                return False

        class TestModel(Model):
            id = fields.IntField(pk=True)

            class Meta:
                table = "test_viewset_throttle_deny"

        class TestViewSet(ViewSet):
            model = TestModel
            throttle_classes = [AlwaysDenyThrottle]

        viewset = TestViewSet()

        with pytest.raises(TooManyRequestsError):
            await viewset.check_throttles(mock_request)


class TestModelViewSet:
    """测试 ModelViewSet"""

    def test_model_viewset_has_all_mixins(self):
        """测试 ModelViewSet 包含所有 mixin"""
        from faster_app.viewsets import ModelViewSet
        from faster_app.viewsets.mixins import (
            CreateModelMixin,
            DestroyModelMixin,
            ListModelMixin,
            RetrieveModelMixin,
            UpdateModelMixin,
        )

        assert issubclass(ModelViewSet, ListModelMixin)
        assert issubclass(ModelViewSet, CreateModelMixin)
        assert issubclass(ModelViewSet, RetrieveModelMixin)
        assert issubclass(ModelViewSet, UpdateModelMixin)
        assert issubclass(ModelViewSet, DestroyModelMixin)


class TestReadOnlyModelViewSet:
    """测试 ReadOnlyModelViewSet"""

    def test_readonly_viewset_has_list_retrieve(self):
        """测试 ReadOnlyModelViewSet 只有 list 和 retrieve"""
        from faster_app.viewsets import ReadOnlyModelViewSet
        from faster_app.viewsets.mixins import (
            CreateModelMixin,
            DestroyModelMixin,
            ListModelMixin,
            RetrieveModelMixin,
            UpdateModelMixin,
        )

        assert issubclass(ReadOnlyModelViewSet, ListModelMixin)
        assert issubclass(ReadOnlyModelViewSet, RetrieveModelMixin)
        assert not issubclass(ReadOnlyModelViewSet, CreateModelMixin)
        assert not issubclass(ReadOnlyModelViewSet, UpdateModelMixin)
        assert not issubclass(ReadOnlyModelViewSet, DestroyModelMixin)


class TestAsRouter:
    """测试 as_router 函数"""

    def test_as_router_creates_router(self):
        """测试 as_router 创建路由"""
        from fastapi import APIRouter
        from tortoise import Model, fields

        from faster_app.viewsets import ModelViewSet
        from faster_app.viewsets.routers import as_router

        class TestModel(Model):
            id = fields.IntField(pk=True)
            name = fields.CharField(max_length=100)

            class Meta:
                table = "test_as_router"

        class TestViewSet(ModelViewSet):
            model = TestModel

        router = as_router(TestViewSet, prefix="/test", tags=["Test"])

        assert isinstance(router, APIRouter)
        assert router.prefix == "/test"
        assert "Test" in router.tags

    def test_as_router_operations_filter(self):
        """测试 as_router 操作过滤"""
        from fastapi import APIRouter
        from tortoise import Model, fields

        from faster_app.viewsets import ModelViewSet
        from faster_app.viewsets.routers import as_router

        class TestModel(Model):
            id = fields.IntField(pk=True)

            class Meta:
                table = "test_as_router_ops"

        class TestViewSet(ModelViewSet):
            model = TestModel

        # 只包含 List 和 Retrieve
        router = as_router(TestViewSet, prefix="/test", operations="LR")

        assert isinstance(router, APIRouter)


class TestJWTAuthCheck:
    """测试 JWT 认证检查辅助函数"""

    def test_check_needs_jwt_auth_true(self):
        """测试需要 JWT 认证"""
        from tortoise import Model, fields

        from faster_app.viewsets.authentication import JWTAuthentication
        from faster_app.viewsets.base import ViewSet
        from faster_app.viewsets.routers import _check_needs_jwt_auth

        class TestModel(Model):
            id = fields.IntField(pk=True)

            class Meta:
                table = "test_jwt_check_true"

        class TestViewSet(ViewSet):
            model = TestModel
            authentication_classes = [JWTAuthentication]

        assert _check_needs_jwt_auth(TestViewSet) is True

    def test_check_needs_jwt_auth_false(self):
        """测试不需要 JWT 认证"""
        from tortoise import Model, fields

        from faster_app.viewsets.authentication import NoAuthentication
        from faster_app.viewsets.base import ViewSet
        from faster_app.viewsets.routers import _check_needs_jwt_auth

        class TestModel(Model):
            id = fields.IntField(pk=True)

            class Meta:
                table = "test_jwt_check_false"

        class TestViewSet(ViewSet):
            model = TestModel
            authentication_classes = [NoAuthentication]

        assert _check_needs_jwt_auth(TestViewSet) is False
