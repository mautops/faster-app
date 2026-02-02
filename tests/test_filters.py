"""
测试过滤系统
"""

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestSearchFilter:
    """测试搜索过滤"""

    @pytest.mark.asyncio
    async def test_no_search_term(self, mock_request: MagicMock):
        """测试无搜索词时返回原始查询集"""
        from faster_app.viewsets.filters import SearchFilter

        mock_request.query_params = {}
        queryset = MagicMock()
        view = MagicMock()
        view.search_fields = ["name", "description"]

        filter_backend = SearchFilter()
        result = await filter_backend.filter_queryset(mock_request, queryset, view)

        assert result is queryset
        queryset.filter.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_with_term(self, mock_request: MagicMock):
        """测试有搜索词时过滤"""
        from faster_app.viewsets.filters import SearchFilter

        mock_request.query_params = {"search": "test"}
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        view = MagicMock()
        view.search_fields = ["name"]

        filter_backend = SearchFilter()
        await filter_backend.filter_queryset(mock_request, queryset, view)

        queryset.filter.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_search_fields(self, mock_request: MagicMock):
        """测试无搜索字段时返回原始查询集"""
        from faster_app.viewsets.filters import SearchFilter

        mock_request.query_params = {"search": "test"}
        queryset = MagicMock()
        view = MagicMock()
        view.search_fields = []

        filter_backend = SearchFilter()
        result = await filter_backend.filter_queryset(mock_request, queryset, view)

        assert result is queryset

    @pytest.mark.asyncio
    async def test_custom_search_param(self, mock_request: MagicMock):
        """测试自定义搜索参数名"""
        from faster_app.viewsets.filters import SearchFilter

        mock_request.query_params = {"q": "test"}
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        view = MagicMock()
        view.search_fields = ["name"]

        filter_backend = SearchFilter(search_param="q")
        await filter_backend.filter_queryset(mock_request, queryset, view)

        queryset.filter.assert_called_once()


class TestOrderingFilter:
    """测试排序过滤"""

    @pytest.mark.asyncio
    async def test_no_ordering_param(self, mock_request: MagicMock):
        """测试无排序参数时使用默认排序"""
        from faster_app.viewsets.filters import OrderingFilter

        mock_request.query_params = {}
        queryset = MagicMock()
        queryset.order_by.return_value = queryset
        view = MagicMock()
        view.ordering_fields = ["name", "created_at"]
        view.ordering = ["-created_at"]

        filter_backend = OrderingFilter()
        await filter_backend.filter_queryset(mock_request, queryset, view)

        queryset.order_by.assert_called_once_with("-created_at")

    @pytest.mark.asyncio
    async def test_ordering_with_param(self, mock_request: MagicMock):
        """测试有排序参数时过滤"""
        from faster_app.viewsets.filters import OrderingFilter

        mock_request.query_params = {"ordering": "name"}
        queryset = MagicMock()
        queryset.order_by.return_value = queryset
        view = MagicMock()
        view.ordering_fields = ["name", "created_at"]
        view.ordering = []

        filter_backend = OrderingFilter()
        await filter_backend.filter_queryset(mock_request, queryset, view)

        queryset.order_by.assert_called_once_with("name")

    @pytest.mark.asyncio
    async def test_descending_ordering(self, mock_request: MagicMock):
        """测试降序排序"""
        from faster_app.viewsets.filters import OrderingFilter

        mock_request.query_params = {"ordering": "-name"}
        queryset = MagicMock()
        queryset.order_by.return_value = queryset
        view = MagicMock()
        view.ordering_fields = ["name"]
        view.ordering = []

        filter_backend = OrderingFilter()
        await filter_backend.filter_queryset(mock_request, queryset, view)

        queryset.order_by.assert_called_once_with("-name")

    @pytest.mark.asyncio
    async def test_multiple_ordering_fields(self, mock_request: MagicMock):
        """测试多字段排序"""
        from faster_app.viewsets.filters import OrderingFilter

        mock_request.query_params = {"ordering": "name,-created_at"}
        queryset = MagicMock()
        queryset.order_by.return_value = queryset
        view = MagicMock()
        view.ordering_fields = ["name", "created_at"]
        view.ordering = []

        filter_backend = OrderingFilter()
        await filter_backend.filter_queryset(mock_request, queryset, view)

        queryset.order_by.assert_called_once_with("name", "-created_at")

    @pytest.mark.asyncio
    async def test_invalid_ordering_field(self, mock_request: MagicMock):
        """测试无效排序字段被忽略"""
        from faster_app.viewsets.filters import OrderingFilter

        mock_request.query_params = {"ordering": "invalid_field"}
        queryset = MagicMock()
        view = MagicMock()
        view.ordering_fields = ["name"]
        view.ordering = []

        filter_backend = OrderingFilter()
        result = await filter_backend.filter_queryset(mock_request, queryset, view)

        # 无效字段被忽略，返回原始查询集
        assert result is queryset


class TestFieldFilter:
    """测试字段过滤"""

    @pytest.mark.asyncio
    async def test_no_filter_fields(self, mock_request: MagicMock):
        """测试无过滤字段时返回原始查询集"""
        from faster_app.viewsets.filters import FieldFilter

        mock_request.query_params = {"name": "test"}
        queryset = MagicMock()
        view = MagicMock()
        view.filter_fields = {}

        filter_backend = FieldFilter()
        result = await filter_backend.filter_queryset(mock_request, queryset, view)

        assert result is queryset

    @pytest.mark.asyncio
    async def test_exact_filter(self, mock_request: MagicMock):
        """测试精确匹配过滤"""
        from faster_app.viewsets.filters import FieldFilter

        mock_request.query_params = {"status": "active"}
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        view = MagicMock()
        view.filter_fields = {"status": "exact"}

        filter_backend = FieldFilter()
        await filter_backend.filter_queryset(mock_request, queryset, view)

        queryset.filter.assert_called_once_with(status="active")

    @pytest.mark.asyncio
    async def test_icontains_filter(self, mock_request: MagicMock):
        """测试包含匹配过滤"""
        from faster_app.viewsets.filters import FieldFilter

        mock_request.query_params = {"name": "test"}
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        view = MagicMock()
        view.filter_fields = {"name": "icontains"}

        filter_backend = FieldFilter()
        await filter_backend.filter_queryset(mock_request, queryset, view)

        queryset.filter.assert_called_once_with(name__icontains="test")

    @pytest.mark.asyncio
    async def test_comparison_filters(self, mock_request: MagicMock):
        """测试比较过滤"""
        from faster_app.viewsets.filters import FieldFilter

        mock_request.query_params = {"price": "100"}
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        view = MagicMock()

        # 测试大于
        view.filter_fields = {"price": "gt"}
        filter_backend = FieldFilter()
        await filter_backend.filter_queryset(mock_request, queryset, view)
        queryset.filter.assert_called_with(price__gt="100")

    @pytest.mark.asyncio
    async def test_in_filter(self, mock_request: MagicMock):
        """测试 in 过滤"""
        from faster_app.viewsets.filters import FieldFilter

        mock_request.query_params = {"status": "active,pending"}
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        view = MagicMock()
        view.filter_fields = {"status": "in"}

        filter_backend = FieldFilter()
        await filter_backend.filter_queryset(mock_request, queryset, view)

        queryset.filter.assert_called_once_with(status__in=["active", "pending"])

    @pytest.mark.asyncio
    async def test_isnull_filter(self, mock_request: MagicMock):
        """测试 isnull 过滤"""
        from faster_app.viewsets.filters import FieldFilter

        mock_request.query_params = {"deleted_at": "true"}
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        view = MagicMock()
        view.filter_fields = {"deleted_at": "isnull"}

        filter_backend = FieldFilter()
        await filter_backend.filter_queryset(mock_request, queryset, view)

        queryset.filter.assert_called_once_with(deleted_at__isnull=True)


class TestDjangoFilterBackend:
    """测试 Django Filter 后端"""

    def test_is_field_filter_subclass(self):
        """测试是 FieldFilter 的子类"""
        from faster_app.viewsets.filters import DjangoFilterBackend, FieldFilter

        assert issubclass(DjangoFilterBackend, FieldFilter)
