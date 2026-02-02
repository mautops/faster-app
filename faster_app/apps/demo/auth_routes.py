"""
权限和认证测试路由

演示 JWT 认证和管理员权限控制功能。
"""

from faster_app.apps.demo.models import DemoModel
from faster_app.apps.demo.schemas import DemoCreate, DemoResponse, DemoUpdate
from faster_app.viewsets import (
    IsAdminUser,
    JWTAuthentication,
    ModelViewSet,
    as_router,
)


class AdminDemoViewSet(ModelViewSet):
    """
    需要管理员权限的 ViewSet - 演示 JWT 认证和管理员权限控制

    所有操作都需要：
    1. JWT 认证(通过 Authorization: Bearer <token> header)
    2. 管理员权限(token 中 is_admin=True)
    """

    model = DemoModel
    schema = DemoResponse  # type: ignore[assignment]
    create_schema = DemoCreate
    update_schema = DemoUpdate

    # 启用 JWT 认证
    authentication_classes = [JWTAuthentication]

    # 需要管理员权限
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()


# 需要管理员权限的路由
admin_demo_router = as_router(
    AdminDemoViewSet,
    prefix="/admin-demos",
    tags=["Admin Demo"],
)
