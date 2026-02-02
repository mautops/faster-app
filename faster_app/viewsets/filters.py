"""
过滤系统

提供灵活的查询过滤功能,支持搜索、排序、字段过滤等。
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from fastapi import Request

if TYPE_CHECKING:
    from faster_app.viewsets.base import ViewSet


class BaseFilterBackend(ABC):
    """
    过滤后端基类

    所有过滤后端都应继承此类,实现过滤逻辑。
    """

    @abstractmethod
    async def filter_queryset(self, request: Request, queryset: Any, view: "ViewSet") -> Any:
        """
        过滤查询集

        Args:
            request: FastAPI 请求对象
            queryset: 查询集对象
            view: ViewSet 实例

        Returns:
            过滤后的查询集
        """
        pass


class SearchFilter(BaseFilterBackend):
    """
    搜索过滤

    支持在多个字段中进行搜索,类似 DRF 的 SearchFilter。
    """

    search_param = "search"
    search_fields: list[str] = []

    def __init__(self, search_param: str | None = None, search_fields: list[str] | None = None):
        """
        初始化搜索过滤

        Args:
            search_param: 搜索参数名,默认 "search"
            search_fields: 搜索字段列表,如果为 None 则从 view.search_fields 获取
        """
        if search_param is not None:
            self.search_param = search_param
        if search_fields is not None:
            self.search_fields = search_fields

    async def filter_queryset(self, request: Request, queryset: Any, view: "ViewSet") -> Any:
        """
        执行搜索过滤

        Args:
            request: FastAPI 请求对象
            queryset: 查询集对象
            view: ViewSet 实例

        Returns:
            过滤后的查询集
        """
        search_term = request.query_params.get(self.search_param)
        if not search_term:
            return queryset

        # 获取搜索字段
        search_fields = self.search_fields
        if not search_fields and hasattr(view, "search_fields"):
            search_fields = view.search_fields

        if not search_fields:
            return queryset

        # 构建搜索条件(使用 OR 连接)
        # Tortoise ORM 使用 Q 对象进行复杂查询
        from tortoise.expressions import Q

        search_conditions = Q()
        for field in search_fields:
            # 支持字段前缀：^ 表示精确匹配,= 表示相等,@ 表示全文搜索
            if field.startswith("^"):
                # 精确匹配
                field_name = field[1:]
                search_conditions |= Q(**{field_name: search_term})
            elif field.startswith("="):
                # 相等匹配
                field_name = field[1:]
                search_conditions |= Q(**{f"{field_name}__exact": search_term})
            elif field.startswith("@"):
                # 全文搜索(需要数据库支持)
                field_name = field[1:]
                search_conditions |= Q(**{f"{field_name}__icontains": search_term})
            else:
                # 默认：包含匹配(不区分大小写)
                search_conditions |= Q(**{f"{field}__icontains": search_term})

        return queryset.filter(search_conditions)


class OrderingFilter(BaseFilterBackend):
    """
    排序过滤

    支持按多个字段排序,类似 DRF 的 OrderingFilter。
    """

    ordering_param = "ordering"
    ordering_fields: list[str] = []
    ordering: list[str] = []  # 默认排序

    def __init__(
        self,
        ordering_param: str | None = None,
        ordering_fields: list[str] | None = None,
        ordering: list[str] | None = None,
    ):
        """
        初始化排序过滤

        Args:
            ordering_param: 排序参数名,默认 "ordering"
            ordering_fields: 允许排序的字段列表,如果为 None 则从 view.ordering_fields 获取
            ordering: 默认排序字段列表,如果为 None 则从 view.ordering 获取
        """
        if ordering_param is not None:
            self.ordering_param = ordering_param
        if ordering_fields is not None:
            self.ordering_fields = ordering_fields
        if ordering is not None:
            self.ordering = ordering

    async def filter_queryset(self, request: Request, queryset: Any, view: "ViewSet") -> Any:
        """
        执行排序过滤

        Args:
            request: FastAPI 请求对象
            queryset: 查询集对象
            view: ViewSet 实例

        Returns:
            排序后的查询集
        """
        # 获取排序字段
        ordering_fields = self.ordering_fields
        if not ordering_fields and hasattr(view, "ordering_fields"):
            ordering_fields = view.ordering_fields

        # 获取默认排序
        default_ordering = self.ordering
        if not default_ordering and hasattr(view, "ordering"):
            default_ordering = view.ordering

        # 从请求参数获取排序
        ordering_param = request.query_params.get(self.ordering_param)
        if ordering_param:
            # 解析排序参数(支持多个字段,用逗号分隔)
            ordering_list = [field.strip() for field in ordering_param.split(",")]

            # 验证排序字段
            valid_ordering = []
            for field in ordering_list:
                # 处理降序(- 前缀)
                if field.startswith("-"):
                    field_name = field[1:]
                    if not ordering_fields or field_name in ordering_fields:
                        valid_ordering.append(f"-{field_name}")
                else:
                    if not ordering_fields or field in ordering_fields:
                        valid_ordering.append(field)

            if valid_ordering:
                return queryset.order_by(*valid_ordering)

        # 使用默认排序
        if default_ordering:
            return queryset.order_by(*default_ordering)

        return queryset


class FieldFilter(BaseFilterBackend):
    """
    字段过滤

    支持按字段精确匹配、范围查询等。
    """

    def __init__(self, filter_fields: dict[str, str] | None = None):
        """
        初始化字段过滤

        Args:
            filter_fields: 字段过滤配置,格式：{"字段名": "查询类型"}
                查询类型支持：exact, icontains, gt, gte, lt, lte, in, isnull
        """
        self.filter_fields = filter_fields or {}

    async def filter_queryset(self, request: Request, queryset: Any, view: "ViewSet") -> Any:
        """
        执行字段过滤

        Args:
            request: FastAPI 请求对象
            queryset: 查询集对象
            view: ViewSet 实例

        Returns:
            过滤后的查询集
        """
        # 获取过滤字段配置
        filter_fields = self.filter_fields
        if not filter_fields and hasattr(view, "filter_fields"):
            filter_fields = view.filter_fields

        if not filter_fields:
            return queryset

        # 构建过滤条件
        filter_kwargs = {}
        for field_name, filter_type in filter_fields.items():
            param_value = request.query_params.get(field_name)
            if param_value is None:
                continue

            # 根据过滤类型构建查询条件
            if filter_type == "exact":
                filter_kwargs[field_name] = param_value
            elif filter_type == "icontains":
                filter_kwargs[f"{field_name}__icontains"] = param_value
            elif filter_type == "gt":
                filter_kwargs[f"{field_name}__gt"] = param_value
            elif filter_type == "gte":
                filter_kwargs[f"{field_name}__gte"] = param_value
            elif filter_type == "lt":
                filter_kwargs[f"{field_name}__lt"] = param_value
            elif filter_type == "lte":
                filter_kwargs[f"{field_name}__lte"] = param_value
            elif filter_type == "in":
                # 支持逗号分隔的多个值
                values: list[str] = [v.strip() for v in param_value.split(",")]
                filter_kwargs[f"{field_name}__in"] = values  # type: ignore[assignment]
            elif filter_type == "isnull":
                is_null: bool = param_value.lower() == "true"
                filter_kwargs[f"{field_name}__isnull"] = is_null  # type: ignore[assignment]
            else:
                # 默认使用精确匹配
                filter_kwargs[field_name] = param_value

        if filter_kwargs:
            return queryset.filter(**filter_kwargs)

        return queryset


class DjangoFilterBackend(FieldFilter):
    """Django Filter 风格的过滤后端（FieldFilter 的别名）"""

    pass
