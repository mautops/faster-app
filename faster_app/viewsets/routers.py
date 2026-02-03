"""
ViewSet 路由注册

提供将 ViewSet 转换为 FastAPI Router 的功能。
"""

from collections.abc import Callable
from functools import lru_cache
from typing import Any

from fastapi import APIRouter, Depends, Query, Request, Security
from fastapi.security import HTTPBearer
from fastapi_pagination import Params
from pydantic import BaseModel

from faster_app.viewsets.authentication import JWTAuthentication
from faster_app.viewsets.base import ViewSet
from faster_app.viewsets.filters import FieldFilter, OrderingFilter, SearchFilter
from faster_app.viewsets.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)

# 模块级别的默认实例,用于避免在函数参数默认值中调用函数
_DEFAULT_PAGINATION = Params()

# HTTPBearer 实例缓存，避免重复创建
_HTTP_BEARER = HTTPBearer(auto_error=False)


@lru_cache(maxsize=128)
def _check_needs_jwt_auth(viewset_class: type[ViewSet]) -> bool:
    """
    检查 ViewSet 是否需要 JWT 认证

    使用 lru_cache 缓存结果，因为 authentication_classes 是类级别属性，
    同一个 ViewSet 类的认证需求不会改变。

    Args:
            viewset: ViewSet 实例（单例）

    Returns:
        是否需要 JWT 认证（用于 Swagger UI 的 Authorize 按钮）
    """
    auth_classes = getattr(viewset_class, "authentication_classes", [])
    return any(
        (isinstance(auth_class, type) and issubclass(auth_class, JWTAuthentication))
        or isinstance(auth_class, JWTAuthentication)
        for auth_class in auth_classes
    )


def _get_security_dependencies(viewset_class: type[ViewSet]) -> list[Callable[..., Any]] | None:
    """
    获取安全依赖项

    Args:
            viewset: ViewSet 实例（单例）

    Returns:
        安全依赖项列表，如果不需要认证则返回 None
    """
    if _check_needs_jwt_auth(viewset_class):
        return [Security(_HTTP_BEARER)]
    return None


class ViewSetRouter:
    """
    ViewSet 路由注册器

    将 ViewSet 转换为 FastAPI Router
    """

    def __init__(
        self,
        viewset_class: type[ViewSet],
        prefix: str = "",
        tags: list[str] | None = None,
        operations: str = "CRUDL",
    ):
        """
        初始化路由注册器

        Args:
            viewset: ViewSet 实例（单例）
            prefix: 路由前缀
            tags: OpenAPI 标签
            operations: 支持的操作 (C=Create, R=Retrieve, U=Update, D=Destroy, L=List)
        """
        self.viewset_class = viewset_class
        self.prefix = prefix
        self.tags = tags or []
        self.operations = operations.upper()

    def get_router(self) -> APIRouter:
        """
        生成 FastAPI Router

        Returns:
            APIRouter 实例

        Note:
            ViewSet 使用单例模式，避免重复实例化开销。
            ViewSet 设计为无状态，所有请求共享同一实例是安全的。
        """
        router = APIRouter(prefix=self.prefix, tags=list(self.tags))

        # 创建单例实例（所有请求共享）
        viewset_instance = self.viewset_class()

        # 先注册自定义 action 路由(更具体的路由先注册,避免被通配路由捕获)
        self._register_custom_actions(router, self.viewset_class)

        # 注册标准 CRUD 路由(每次请求创建新实例)
        if "L" in self.operations and isinstance(viewset_instance, ListModelMixin):
            self._register_list_route(router, viewset_instance)

        if "C" in self.operations and isinstance(viewset_instance, CreateModelMixin):
            self._register_create_route(router, viewset_instance)

        if "R" in self.operations and isinstance(viewset_instance, RetrieveModelMixin):
            self._register_retrieve_route(router, viewset_instance)

        if "U" in self.operations and isinstance(viewset_instance, UpdateModelMixin):
            self._register_update_route(router, viewset_instance)
            self._register_partial_update_route(router, viewset_instance)

        if "D" in self.operations and isinstance(viewset_instance, DestroyModelMixin):
            self._register_destroy_route(router, viewset_instance)

        return router

    def _get_filter_query_params(self, viewset_instance: ViewSet) -> dict[str, Any]:
        """
        根据 ViewSet 的过滤配置生成查询参数

        Args:
            viewset_instance: ViewSet 实例

        Returns:
            查询参数字典,用于 FastAPI 路由
        """
        query_params = {}
        filter_backends = getattr(viewset_instance, "filter_backends", [])

        for backend in filter_backends:
            # 如果 backend 是类,需要实例化以获取属性
            backend_instance = backend() if isinstance(backend, type) else backend

            # 处理 SearchFilter
            if isinstance(backend_instance, SearchFilter) or (
                isinstance(backend, type) and issubclass(backend, SearchFilter)
            ):
                search_fields = getattr(viewset_instance, "search_fields", [])
                if search_fields:
                    search_param = backend_instance.search_param
                    query_params[search_param] = Query(
                        None,
                        description=f"搜索关键词,将在以下字段中搜索: {', '.join(search_fields)}",
                    )

            # 处理 OrderingFilter
            if isinstance(backend_instance, OrderingFilter) or (
                isinstance(backend, type) and issubclass(backend, OrderingFilter)
            ):
                ordering_fields = getattr(viewset_instance, "ordering_fields", [])
                if ordering_fields:
                    ordering_param = backend_instance.ordering_param
                    query_params[ordering_param] = Query(
                        None,
                        description=f"排序字段,支持: {', '.join(ordering_fields)}。使用 - 前缀表示降序,例如: -created_at",
                    )

            # 处理 FieldFilter
            if isinstance(backend_instance, FieldFilter) or (
                isinstance(backend, type) and issubclass(backend, FieldFilter)
            ):
                filter_fields = getattr(viewset_instance, "filter_fields", {})
                if filter_fields:
                    for field_name, filter_type in filter_fields.items():
                        # 根据过滤类型生成描述
                        type_descriptions = {
                            "exact": "精确匹配",
                            "icontains": "包含匹配(不区分大小写)",
                            "gt": "大于",
                            "gte": "大于等于",
                            "lt": "小于",
                            "lte": "小于等于",
                            "in": "在列表中(逗号分隔)",
                            "isnull": "是否为空(true/false)",
                        }
                        description = type_descriptions.get(filter_type, f"过滤类型: {filter_type}")
                        query_params[field_name] = Query(
                            None, description=f"{field_name}: {description}"
                        )

        return query_params

    def _register_list_route(self, router: APIRouter, viewset: ViewSet) -> None:
        """注册列表路由"""
        viewset_instance = viewset
        security = _get_security_dependencies(viewset.__class__)

        # 获取过滤查询参数配置
        filter_params = self._get_filter_query_params(viewset_instance)

        # 构建函数参数：request, pagination, 以及所有过滤参数
        # 使用 functools.partial 或者直接构建函数签名
        import inspect
        from functools import wraps

        # 创建基础函数
        # 使用 Depends() 让 FastAPI 自动注入 Params 实例
        async def base_list_view(request: Request, pagination: Params = Depends()):  # noqa: B008
            viewset = self.viewset_class()
            return await viewset.list(request, pagination)  # type: ignore[attr-defined]

        # 如果有过滤参数,需要动态添加
        if filter_params:
            # 构建新的函数签名
            sig = inspect.signature(base_list_view)
            params = list(sig.parameters.values())

            # 添加过滤查询参数
            for param_name, query_default in filter_params.items():
                params.append(
                    inspect.Parameter(
                        param_name,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=query_default,
                        annotation=str | None,
                    )
                )

            # 创建包装函数
            @wraps(base_list_view)
            async def list_view(*args, **kwargs):
                # 提取 request 和 pagination,忽略过滤参数(ViewSet 会从 request.query_params 读取)
                request_arg = None
                pagination_arg = Params()

                # 从位置参数中查找
                for arg in args:
                    if isinstance(arg, Request):
                        request_arg = arg
                    elif isinstance(arg, Params):
                        pagination_arg = arg

                # 从关键字参数中查找
                if not request_arg and "request" in kwargs:
                    request_arg = kwargs["request"]
                if "pagination" in kwargs:
                    pagination_arg = kwargs["pagination"]

                if request_arg:
                    viewset = self.viewset_class()
                    return await viewset.list(request_arg, pagination_arg)  # type: ignore[attr-defined]

                # 回退到原始调用
                return await base_list_view(*args, **kwargs)

            list_view.__signature__ = inspect.Signature(params)  # type: ignore[attr-defined]
        else:
            list_view = base_list_view  # type: ignore[assignment]

        # 直接注册 list_view,保持其函数签名
        router.get("/", dependencies=security)(list_view)  # type: ignore[arg-type]

    def _get_schema(
        self, viewset: ViewSet, schema_type: str = "create"
    ) -> type[BaseModel] | None:
        """
        获取 Schema 类

        Args:
            viewset: ViewSet 实例（单例）
            schema_type: Schema 类型 ('create' 或 'update')

        Returns:
            Schema 类
        """
        viewset_instance = viewset
        if schema_type == "create":
            return viewset_instance.create_schema or viewset_instance.schema
        else:  # update
            return viewset_instance.update_schema or viewset_instance.schema

    def _register_create_route(self, router: APIRouter, viewset: ViewSet) -> None:
        """注册创建路由"""
        schema = self._get_schema(viewset, "create")
        security = _get_security_dependencies(viewset.__class__)

        @router.post("/", dependencies=security)  # type: ignore[arg-type]
        async def create_view(request: Request, create_data: schema):  # type: ignore[valid-type]
            viewset_instance = self.viewset_class()
            return await viewset_instance.create(request, create_data)  # type: ignore[attr-defined]

    def _register_retrieve_route(self, router: APIRouter, viewset: ViewSet) -> None:
        """注册单个查询路由"""
        security = _get_security_dependencies(viewset.__class__)

        @router.get("/{pk}", dependencies=security)  # type: ignore[arg-type]
        async def retrieve_view(request: Request, pk: str):
            viewset_instance = self.viewset_class()
            return await viewset_instance.retrieve(request, pk)  # type: ignore[attr-defined]

    def _register_update_route(self, router: APIRouter, viewset: ViewSet) -> None:
        """注册完整更新路由"""
        schema = self._get_schema(viewset, "update")
        security = _get_security_dependencies(viewset.__class__)

        @router.put("/{pk}", dependencies=security)  # type: ignore[arg-type]
        async def update_view(request: Request, pk: str, update_data: schema):  # type: ignore[valid-type]
            viewset_instance = self.viewset_class()
            return await viewset_instance.update(request, pk, update_data)  # type: ignore[attr-defined]

    def _register_partial_update_route(
        self, router: APIRouter, viewset: ViewSet
    ) -> None:
        """注册部分更新路由"""
        schema = self._get_schema(viewset, "update")
        security = _get_security_dependencies(viewset.__class__)

        @router.patch("/{pk}", dependencies=security)  # type: ignore[arg-type]
        async def partial_update_view(request: Request, pk: str, update_data: schema):  # type: ignore[valid-type]
            viewset_instance = self.viewset_class()
            return await viewset_instance.partial_update(request, pk, update_data)  # type: ignore[attr-defined]

    def _register_destroy_route(self, router: APIRouter, viewset: ViewSet) -> None:
        """注册删除路由"""
        security = _get_security_dependencies(viewset.__class__)

        @router.delete("/{pk}", dependencies=security)  # type: ignore[arg-type]
        async def destroy_view(request: Request, pk: str):
            viewset_instance = self.viewset_class()
            return await viewset_instance.destroy(request, pk)  # type: ignore[attr-defined]

    def _register_custom_actions(self, router: APIRouter, viewset: ViewSet) -> None:
        """注册自定义 action 路由"""
        viewset_class = viewset.__class__
        # 获取 ViewSet 类的方法(不是实例方法)
        for attr_name in dir(viewset_class):
            # 跳过私有方法和特殊方法
            if attr_name.startswith("_") or attr_name in [
                "get_queryset",
                "get_object",
                "get_schema",
                "get_object_name",
                "list",
                "create",
                "retrieve",
                "update",
                "partial_update",
                "destroy",
            ]:
                continue

            attr = getattr(viewset_class, attr_name)
            if not callable(attr) or not hasattr(attr, "action"):
                continue

            methods = getattr(attr, "action_methods", ["GET"])
            detail = getattr(attr, "action_detail", False)
            url_path = getattr(attr, "action_url_path", attr_name.replace("_", "-"))
            action_kwargs = getattr(attr, "action_kwargs", {})

            # 构建路由路径
            route_path = f"/{{pk}}/{url_path}" if detail else f"/{url_path}"

            # 为每个方法创建独立的处理函数
            # 使用默认参数来避免闭包问题
            for method in methods:
                # 检查 action 方法的签名
                import inspect

                sig = inspect.signature(attr)
                # 获取原始方法的参数(不包括 self)
                original_params = list(sig.parameters.values())[1:]  # 跳过 self

                # 创建新的参数列表(用于 handler 函数)
                handler_params = []
                action_call_params = []

                for param in original_params:
                    if param.name in ("request", "pk"):
                        # request 和 pk 是固定参数
                        handler_params.append(param)
                        action_call_params.append(param.name)
                    else:
                        # 其他参数需要传递给 action
                        handler_params.append(param)
                        action_call_params.append(param.name)

                # 使用默认参数来捕获当前循环的值
                # 在外层先复制,避免在默认参数中调用函数
                captured_call_params = action_call_params.copy()
                captured_func_params = handler_params.copy()

                def make_handler(
                    action_method=attr,
                    is_detail=detail,
                    vs_class=viewset_class,
                    action_name=attr_name,
                    call_params=captured_call_params,
                    func_params=captured_func_params,
                ):
                    async def base_handler(**kwargs):
                        # 每次请求创建新的 ViewSet 实例,确保无状态
                        viewset = vs_class()
                        request = kwargs.get("request")

                        # 检查限流
                        await viewset.check_throttles(request)
                        # 执行认证和权限检查
                        await viewset.perform_authentication(request)
                        await viewset.check_permissions(request, action_name)

                        # 如果是对象级操作,获取对象并检查对象权限
                        if is_detail:
                            pk = kwargs.get("pk")
                            instance = await viewset.get_object(pk)
                            if instance:
                                await viewset.check_object_permissions(
                                    request, instance, action_name
                                )

                        # 准备调用参数
                        call_args = [viewset]
                        for param_name in call_params:
                            call_args.append(kwargs.get(param_name))

                        return await action_method(*call_args)

                    # 设置正确的函数签名
                    base_handler.__signature__ = inspect.Signature(parameters=func_params)  # type: ignore[attr-defined]
                    return base_handler

                handler = make_handler()

                # 获取安全依赖
                security = _get_security_dependencies(viewset.__class__)

                # 合并安全依赖到 action_kwargs
                route_kwargs = action_kwargs.copy()
                if security:
                    existing_deps = route_kwargs.get("dependencies", [])
                    if isinstance(existing_deps, list):
                        route_kwargs["dependencies"] = existing_deps + security
                    else:
                        route_kwargs["dependencies"] = security

                router.add_api_route(
                    route_path,
                    handler,
                    methods=[method],
                    **route_kwargs,
                )


def as_router(
    viewset_class: type[ViewSet],
    prefix: str = "",
    tags: list[str] | None = None,
    operations: str = "CRUDL",
) -> APIRouter:
    """
    将 ViewSet 转换为 FastAPI Router

    Args:
            viewset: ViewSet 实例（单例）
        prefix: 路由前缀
        tags: OpenAPI 标签
        operations: 支持的操作 (C=Create, R=Retrieve, U=Update, D=Destroy, L=List)

    Returns:
        APIRouter 实例

    Example:
        class DemoViewSet(ModelViewSet):
            model = DemoModel

        router = as_router(DemoViewSet, prefix="/demos", tags=["Demo"])
    """
    router_builder = ViewSetRouter(
        viewset_class=viewset_class,
        prefix=prefix,
        tags=tags,
        operations=operations,
    )
    return router_builder.get_router()
