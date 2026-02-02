"""
测试权限系统
"""

from unittest.mock import MagicMock

import pytest


class TestAllowAny:
    """测试允许所有权限"""

    @pytest.mark.asyncio
    async def test_allows_any_request(self, mock_request: MagicMock):
        """测试允许任何请求"""
        from faster_app.viewsets.permissions import AllowAny

        permission = AllowAny()
        view = MagicMock()

        assert await permission.has_permission(mock_request, view) is True

    @pytest.mark.asyncio
    async def test_allows_any_object(self, mock_request: MagicMock):
        """测试允许任何对象操作"""
        from faster_app.viewsets.permissions import AllowAny

        permission = AllowAny()
        view = MagicMock()
        obj = MagicMock()

        assert await permission.has_object_permission(mock_request, view, obj) is True


class TestIsAuthenticated:
    """测试已认证权限"""

    @pytest.mark.asyncio
    async def test_denies_unauthenticated(self, mock_request: MagicMock):
        """测试拒绝未认证用户"""
        from faster_app.viewsets.permissions import IsAuthenticated

        mock_request.state.user = None
        permission = IsAuthenticated()
        view = MagicMock()

        assert await permission.has_permission(mock_request, view) is False

    @pytest.mark.asyncio
    async def test_allows_authenticated(self, auth_request: MagicMock):
        """测试允许已认证用户"""
        from faster_app.viewsets.permissions import IsAuthenticated

        permission = IsAuthenticated()
        view = MagicMock()

        assert await permission.has_permission(auth_request, view) is True


class TestIsAdminUser:
    """测试管理员权限"""

    @pytest.mark.asyncio
    async def test_denies_non_admin(self, auth_request: MagicMock, mock_user: MagicMock):
        """测试拒绝非管理员"""
        from faster_app.viewsets.permissions import IsAdminUser

        mock_user.is_admin = False
        permission = IsAdminUser()
        view = MagicMock()

        assert await permission.has_permission(auth_request, view) is False

    @pytest.mark.asyncio
    async def test_allows_admin(self, mock_request: MagicMock, admin_user: MagicMock):
        """测试允许管理员"""
        from faster_app.viewsets.permissions import IsAdminUser

        mock_request.state.user = admin_user
        permission = IsAdminUser()
        view = MagicMock()

        assert await permission.has_permission(mock_request, view) is True

    @pytest.mark.asyncio
    async def test_denies_unauthenticated(self, mock_request: MagicMock):
        """测试拒绝未认证用户"""
        from faster_app.viewsets.permissions import IsAdminUser

        mock_request.state.user = None
        permission = IsAdminUser()
        view = MagicMock()

        assert await permission.has_permission(mock_request, view) is False


class TestIsOwner:
    """测试所有者权限"""

    @pytest.mark.asyncio
    async def test_allows_owner(self, auth_request: MagicMock, mock_user: MagicMock):
        """测试允许所有者"""
        from faster_app.viewsets.permissions import IsOwner

        # 创建一个对象，限定只有 owner_id 属性
        obj = MagicMock(spec=["owner_id"])
        obj.owner_id = mock_user.id

        permission = IsOwner()
        view = MagicMock()

        assert await permission.has_object_permission(auth_request, view, obj) is True

    @pytest.mark.asyncio
    async def test_denies_non_owner(self, auth_request: MagicMock, mock_user: MagicMock):
        """测试拒绝非所有者"""
        from faster_app.viewsets.permissions import IsOwner

        obj = MagicMock(spec=["owner_id"])
        obj.owner_id = 999  # 不同的用户 ID

        permission = IsOwner()
        view = MagicMock()

        assert await permission.has_object_permission(auth_request, view, obj) is False

    @pytest.mark.asyncio
    async def test_allows_owner_with_user_id(self, auth_request: MagicMock, mock_user: MagicMock):
        """测试通过 user_id 属性检查所有者"""
        from faster_app.viewsets.permissions import IsOwner

        obj = MagicMock(spec=["user_id"])
        obj.user_id = mock_user.id

        permission = IsOwner()
        view = MagicMock()

        assert await permission.has_object_permission(auth_request, view, obj) is True


class TestIsOwnerOrReadOnly:
    """测试所有者或只读权限"""

    @pytest.mark.asyncio
    async def test_allows_safe_methods(self, mock_request: MagicMock):
        """测试允许安全方法"""
        from faster_app.viewsets.permissions import IsOwnerOrReadOnly

        mock_request.method = "GET"
        permission = IsOwnerOrReadOnly()
        view = MagicMock()
        obj = MagicMock()

        assert await permission.has_object_permission(mock_request, view, obj) is True

    @pytest.mark.asyncio
    async def test_allows_owner_unsafe_methods(
        self, auth_request: MagicMock, mock_user: MagicMock
    ):
        """测试允许所有者执行不安全方法"""
        from faster_app.viewsets.permissions import IsOwnerOrReadOnly

        auth_request.method = "DELETE"
        obj = MagicMock(spec=["owner_id"])
        obj.owner_id = mock_user.id

        permission = IsOwnerOrReadOnly()
        view = MagicMock()

        assert await permission.has_object_permission(auth_request, view, obj) is True

    @pytest.mark.asyncio
    async def test_denies_non_owner_unsafe_methods(
        self, auth_request: MagicMock, mock_user: MagicMock
    ):
        """测试拒绝非所有者执行不安全方法"""
        from faster_app.viewsets.permissions import IsOwnerOrReadOnly

        auth_request.method = "DELETE"
        obj = MagicMock(spec=["owner_id"])
        obj.owner_id = 999

        permission = IsOwnerOrReadOnly()
        view = MagicMock()

        assert await permission.has_object_permission(auth_request, view, obj) is False
