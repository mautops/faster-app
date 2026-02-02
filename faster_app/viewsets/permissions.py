"""
权限系统

提供权限检查功能,支持操作级权限和对象级权限。
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from fastapi import Request

if TYPE_CHECKING:
    from faster_app.viewsets.base import ViewSet


class BasePermission(ABC):
    """
    权限基类

    所有权限类都应继承此类,实现权限检查逻辑。
    """

    @abstractmethod
    async def has_permission(self, request: Request, view: "ViewSet") -> bool:
        """
        检查是否有权限执行操作(操作级权限)

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例

        Returns:
            True 表示有权限,False 表示无权限
        """
        pass

    async def has_object_permission(self, request: Request, view: "ViewSet", obj: object) -> bool:
        """
        检查是否有权限操作特定对象(对象级权限)

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例
            obj: 要操作的对象

        Returns:
            True 表示有权限,False 表示无权限

        Note:
            默认返回 True,子类可以重写此方法实现对象级权限检查
        """
        return True


class AllowAny(BasePermission):
    """
    允许所有请求

    不进行任何权限检查,所有请求都允许。
    """

    async def has_permission(self, request: Request, view: "ViewSet") -> bool:
        return True


class IsAuthenticated(BasePermission):
    """
    需要认证

    检查请求是否已认证(是否有用户信息)。
    """

    async def has_permission(self, request: Request, view: "ViewSet") -> bool:
        # 检查 request.state 中是否有 user 信息
        # 这需要认证系统设置 request.state.user
        return hasattr(request.state, "user") and request.state.user is not None


class IsAdminUser(BasePermission):
    """
    需要管理员权限

    检查用户是否是管理员。
    """

    async def has_permission(self, request: Request, view: "ViewSet") -> bool:
        if not hasattr(request.state, "user") or request.state.user is None:
            return False

        # 检查用户是否有 is_admin 属性或 role 属性
        user = request.state.user
        if hasattr(user, "is_admin"):
            return bool(user.is_admin)
        if hasattr(user, "role"):
            return bool(user.role == "admin")
        if hasattr(user, "is_superuser"):
            return bool(user.is_superuser)

        return False

    async def has_object_permission(self, request: Request, view: "ViewSet", obj: object) -> bool:
        """
        检查对象级权限：只有管理员才能操作对象

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例
            obj: 要操作的对象

        Returns:
            True 表示有权限,False 表示无权限
        """
        # 对象级权限检查与操作级权限检查相同
        return await self.has_permission(request, view)


class IsOwner(BasePermission):
    """
    检查是否是对象所有者

    检查当前用户是否是对象的所有者。
    对象需要有 owner_id 或 user_id 字段,或者有 owner 或 user 关联。
    """

    async def has_permission(self, request: Request, view: "ViewSet") -> bool:
        # 操作级权限：需要认证
        return hasattr(request.state, "user") and request.state.user is not None

    async def has_object_permission(self, request: Request, view: "ViewSet", obj: object) -> bool:
        """
        检查是否是对象所有者

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例
            obj: 要操作的对象

        Returns:
            True 表示是所有者,False 表示不是
        """
        if not hasattr(request.state, "user") or request.state.user is None:
            return False

        user = request.state.user
        user_id = getattr(user, "id", None)
        if user_id is None:
            return False

        # 检查对象的 owner_id 或 user_id 字段
        if hasattr(obj, "owner_id"):
            return bool(obj.owner_id == user_id)
        if hasattr(obj, "user_id"):
            return bool(obj.user_id == user_id)

        # 检查对象的 owner 或 user 关联
        if hasattr(obj, "owner"):
            owner = obj.owner
            if hasattr(owner, "__await__"):
                owner = await owner
            if owner and getattr(owner, "id", None) == user_id:
                return True
        if hasattr(obj, "user"):
            user_obj = obj.user
            if hasattr(user_obj, "__await__"):
                user_obj = await user_obj
            if user_obj and getattr(user_obj, "id", None) == user_id:
                return True

        return False


class IsOwnerOrReadOnly(BasePermission):
    """
    所有者或只读

    允许所有者进行所有操作,其他用户只能读取。
    """

    async def has_permission(self, request: Request, view: "ViewSet") -> bool:
        # 允许所有请求(包括未认证)
        return True

    async def has_object_permission(self, request: Request, view: "ViewSet", obj: object) -> bool:
        """
        检查权限：所有者可以所有操作,其他用户只能读取

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例
            obj: 要操作的对象

        Returns:
            True 表示有权限,False 表示无权限
        """
        # 只读操作(GET, HEAD, OPTIONS)允许所有人
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # 写操作需要是所有者
        if not hasattr(request.state, "user") or request.state.user is None:
            return False

        user = request.state.user
        user_id = getattr(user, "id", None)
        if user_id is None:
            return False

        # 检查是否是所有者
        if hasattr(obj, "owner_id"):
            return bool(obj.owner_id == user_id)
        if hasattr(obj, "user_id"):
            return bool(obj.user_id == user_id)

        return False
