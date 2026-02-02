"""
ViewSet 基类

提供 ViewSet 的基础功能,包括查询集管理、序列化器管理、对象获取等。
"""

from abc import ABC
from typing import Any

from fastapi import Request
from pydantic import BaseModel
from tortoise import Model
from tortoise.contrib.pydantic import PydanticModel, pydantic_model_creator

from faster_app.exceptions import ForbiddenError, TooManyRequestsError, UnauthorizedError
from faster_app.viewsets.authentication import BaseAuthentication, NoAuthentication
from faster_app.viewsets.filters import BaseFilterBackend
from faster_app.viewsets.permissions import AllowAny, BasePermission
from faster_app.viewsets.throttling import BaseThrottle, NoThrottle

# 全局组件缓存
_permission_cache: dict[type, Any] = {}
_authenticator_cache: dict[type, Any] = {}
_filter_backend_cache: dict[type, Any] = {}


class ViewSet(ABC):  # noqa: B024
    """
    ViewSet 基类 - 类似 DRF 的 ViewSet

    提供标准的 CRUD 操作基础功能,包括：
    - 查询集管理
    - Schema 管理
    - 对象获取
    - 钩子函数支持
    - 权限和认证
    """

    # 模型和 Schema(子类必须定义)
    model: type[Model] | None = None
    schema: type[PydanticModel] | None = None
    create_schema: type[BaseModel] | None = None
    update_schema: type[BaseModel] | None = None

    # 权限和认证(可选,有默认值)
    permission_classes: list[type[BasePermission]] = [AllowAny]
    authentication_classes: list[type[BaseAuthentication]] = [NoAuthentication]

    # 过滤和排序(可选)
    filter_backends: list[type[BaseFilterBackend]] = []
    search_fields: list[str] = []
    ordering_fields: list[str] = []
    ordering: list[str] = []
    filter_fields: dict[str, str] = {}

    # 限流(可选)
    throttle_classes: list[type[BaseThrottle] | BaseThrottle] = [NoThrottle]
    throttle_scope: str | None = None

    # Schema 缓存(类级别,避免重复生成)
    _schema_cache: dict[str, type[PydanticModel]] = {}

    def __init__(self):
        """初始化 ViewSet"""
        if self.model is None:
            raise ValueError(f"{self.__class__.__name__} 必须定义 model 属性")

        # 如果没有提供 Schema,自动生成(使用缓存避免重复生成)
        if self.schema is None:
            cache_key = f"{self.model.__name__}_Response"
            if cache_key not in self._schema_cache:
                self._schema_cache[cache_key] = pydantic_model_creator(
                    self.model, name=f"{self.model.__name__}Response"
                )
            self.schema = self._schema_cache[cache_key]

        # create_schema 和 update_schema 不自动生成
        # 如果未提供,会在 get_schema 中回退到 schema

    def get_queryset(self) -> Any:
        """
        获取查询集(可被子类重写)

        Returns:
            查询集对象(Tortoise QuerySet)
        """
        assert self.model is not None  # Validated in __init__
        return self.model.all()

    def get_schema(self, action: str) -> type[PydanticModel] | type[BaseModel] | None:
        """
        根据操作获取 Schema 类(可被子类重写)

        Args:
            action: 操作名称(list, create, retrieve, update, destroy)

        Returns:
            Schema 类
        """
        if action == "create":
            return self.create_schema or self.schema
        elif action in ("update", "partial_update"):
            return self.update_schema or self.schema
        else:
            return self.schema

    async def get_object(self, pk: Any, prefetch: list[str] | None = None) -> Model | None:
        """
        根据主键获取对象(可被子类重写)

        Args:
            pk: 主键值
            prefetch: 需要预加载的关联字段列表

        Returns:
            模型实例或 None
        """
        # 处理 UUID 类型主键
        from contextlib import suppress
        from uuid import UUID

        if isinstance(pk, str):
            with suppress(ValueError, AttributeError):
                # 尝试将字符串转换为 UUID
                pk = UUID(pk)

        assert self.model is not None  # Validated in __init__
        if prefetch:
            # 如果需要预加载关联,使用查询集方式
            instance = await self.model.filter(id=pk).prefetch_related(*prefetch).first()
        else:
            # 否则直接使用 get_or_none
            instance = await self.model.get_or_none(id=pk)
        return instance

    def get_object_name(self) -> str:
        """
        获取对象名称(用于错误消息等)

        Returns:
            对象名称
        """
        if self.model:
            return self.model.__name__
        return "对象"

    def get_permissions(self) -> list[BasePermission]:
        """获取权限实例列表(可被子类重写)"""
        return [_permission_cache.setdefault(cls, cls()) for cls in self.permission_classes]

    def get_authenticators(self) -> list[BaseAuthentication]:
        """获取认证实例列表(可被子类重写)"""
        return [_authenticator_cache.setdefault(cls, cls()) for cls in self.authentication_classes]

    async def perform_authentication(self, request: Request) -> None:
        """
        执行认证(可被子类重写)

        Args:
            request: FastAPI 请求对象

        Raises:
            UnauthorizedError: 认证失败
        """
        authenticators = self.get_authenticators()
        for authenticator in authenticators:
            result = await authenticator.authenticate(request)
            if result is not None:
                user, token = result
                # 将用户信息存储到 request.state
                request.state.user = user
                if token:
                    request.state.auth_token = token
                return

        # 如果所有认证类都失败,且不是 NoAuthentication,则抛出异常
        if authenticators and not isinstance(authenticators[0], NoAuthentication):
            raise UnauthorizedError(message="认证失败,请提供有效的认证信息")

    async def check_permissions(self, request: Request, action: str = "") -> None:
        """
        检查权限(可被子类重写)

        Args:
            request: FastAPI 请求对象
            action: 操作名称(可选)

        Raises:
            ForbiddenError: 权限不足
        """
        permissions = self.get_permissions()
        for permission in permissions:
            if not await permission.has_permission(request, self):
                raise ForbiddenError(
                    message="您没有权限执行此操作",
                    data={"action": action},
                )

    async def check_object_permissions(
        self, request: Request, obj: object, action: str = ""
    ) -> None:
        """
        检查对象级权限(可被子类重写)

        Args:
            request: FastAPI 请求对象
            obj: 要操作的对象
            action: 操作名称(可选)

        Raises:
            ForbiddenError: 权限不足
        """
        permissions = self.get_permissions()
        for permission in permissions:
            if not await permission.has_object_permission(request, self, obj):
                object_id = getattr(obj, "id", None)
                # 将 UUID 转换为字符串以便 JSON 序列化
                if object_id is not None:
                    object_id = str(object_id)
                raise ForbiddenError(
                    message="您没有权限操作此对象",
                    data={"action": action, "object_id": object_id},
                )

    def get_filter_backends(self) -> list[BaseFilterBackend]:
        """获取过滤后端实例列表(可被子类重写)"""
        return [_filter_backend_cache.setdefault(cls, cls()) for cls in self.filter_backends]

    async def filter_queryset(self, queryset: Any, request: Request) -> Any:
        """
        过滤查询集(可被子类重写)

        Args:
            queryset: 查询集对象
            request: FastAPI 请求对象

        Returns:
            过滤后的查询集
        """
        for backend in self.get_filter_backends():
            queryset = await backend.filter_queryset(request, queryset, self)
        return queryset

    def get_throttles(self) -> list[BaseThrottle]:
        """
        获取限流实例列表(可被子类重写)

        Returns:
            限流实例列表
        """
        throttles = []
        for throttle in self.throttle_classes:
            # 如果已经是实例,直接使用;如果是类,则实例化
            if isinstance(throttle, BaseThrottle):
                throttles.append(throttle)
            else:
                throttles.append(throttle())
        return throttles

    async def check_throttles(self, request: Request) -> None:
        """
        检查限流(可被子类重写)

        Args:
            request: FastAPI 请求对象

        Raises:
            TooManyRequestsError: 请求频率过高
        """
        for throttle in self.get_throttles():
            if not await throttle.allow_request(request, self):
                wait_time = throttle.wait()
                raise TooManyRequestsError(
                    message="请求频率过高,请稍后再试",
                    data={"wait_time": wait_time} if wait_time else None,
                )
