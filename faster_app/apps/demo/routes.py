"""
Demo 路由 - ViewSet 功能演示

统一的 Demo ViewSet,展示所有 ViewSet 特性:
1. 基础 CRUD 操作
2. 认证和权限系统 (可选)
3. 过滤和排序
4. 限流控制
5. 自定义 Action
6. 钩子函数
"""

from datetime import datetime

from fastapi import BackgroundTasks, Request

from faster_app.apps.demo.models import DemoModel
from faster_app.apps.demo.schemas import (
    BackgroundTaskRequest,
    DemoCreate,
    DemoResponse,
    DemoStatistics,
    DemoUpdate,
)
from faster_app.apps.demo.tasks import send_notification, write_log_to_file
from faster_app.exceptions import ConflictError, NotFoundError
from faster_app.settings import logger
from faster_app.utils.response import ApiResponse
from faster_app.viewsets import (
    AnonRateThrottle,
    FieldFilter,
    IsAuthenticated,
    JWTAuthentication,
    ModelViewSet,
    OrderingFilter,
    SearchFilter,
    UserRateThrottle,
    action,
    as_router,
)


class DemoViewSet(ModelViewSet):
    """
    Demo ViewSet - 统一的功能演示

    包含所有 ViewSet 特性:
    - 基础 CRUD 操作
    - 认证和权限 (可选,默认允许所有)
    - 过滤和排序
    - 限流控制
    - 自定义 Action
    - 钩子函数
    """

    model = DemoModel
    schema = DemoResponse  # type: ignore[assignment]
    create_schema = DemoCreate
    update_schema = DemoUpdate

    # 认证和权限 (可选,默认允许所有)
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # 过滤和排序
    filter_backends = [SearchFilter, OrderingFilter, FieldFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "updated_at", "status", "name"]
    ordering = ["-created_at"]
    filter_fields = {
        "status": "exact",
        "name": "icontains",
    }

    # 限流 (可选,默认不限流)
    # 使用默认配置：user=100/hour, anon=20/hour
    throttle_classes = [UserRateThrottle(), AnonRateThrottle()]

    def get_queryset(self):
        """自定义查询集"""
        return self.model.all()

    # 钩子函数示例
    async def perform_create_hook(self, create_data: DemoCreate, request: Request) -> DemoCreate:  # type: ignore[override]
        """创建前钩子 - 业务逻辑检查"""
        existing = await self.model.filter(name=create_data.name).first()
        if existing:
            raise ConflictError(message="名称已存在", data={"name": create_data.name})
        logger.info(f"[创建前] 准备创建记录: {create_data.name}")
        return create_data

    async def perform_create_after_hook(self, instance: DemoModel, request: Request) -> DemoModel:  # type: ignore[override]
        """创建后钩子 - 记录日志"""
        logger.info(f"[创建后] 已创建记录: {instance.id} - {instance.name}")
        return instance

    async def perform_update_hook(  # type: ignore[override]
        self, instance: DemoModel, update_data: DemoUpdate, request: Request
    ) -> DemoUpdate:
        """更新前钩子"""
        logger.info(f"[更新前] 准备更新记录: {instance.id}")
        return update_data

    async def perform_update_after_hook(self, instance: DemoModel, request: Request) -> DemoModel:  # type: ignore[override]
        """更新后钩子"""
        logger.info(f"[更新后] 已更新记录: {instance.id} - {instance.name}")
        return instance

    async def perform_destroy_hook(self, instance: DemoModel, request: Request) -> bool:  # type: ignore[override]
        """删除前钩子"""
        logger.info(f"[删除前] 准备删除记录: {instance.id}")
        return True

    async def perform_destroy_after_hook(self, instance: DemoModel, request: Request) -> None:  # type: ignore[override]
        """删除后钩子"""
        logger.info(f"[删除后] 已删除记录: {instance.id}")

    # 自定义 Action 示例
    @action(detail=False, methods=["GET"])
    async def statistics(self, request: Request):
        """
        统计信息 - 列表级别的 action

        访问路径: GET /demos/statistics
        支持过滤参数: ?status=1&name=test
        """
        queryset = self.get_queryset()
        # 应用过滤
        queryset = await self.filter_queryset(queryset, request)

        total = await queryset.count()
        active = await queryset.filter(status=1).count()
        inactive = total - active

        statistics_data = DemoStatistics(
            total=total,
            active=active,
            inactive=inactive,
        )

        return ApiResponse.success(
            data=statistics_data.model_dump(mode="json"),
            message="统计信息查询成功",
        )

    @action(detail=True, methods=["POST"])
    async def activate(self, request: Request, pk: str):
        """
        激活操作 - 对象级别的 action

        访问路径: POST /demos/{pk}/activate
        """
        instance = await self.get_object(pk)
        if not instance:
            raise NotFoundError(message="记录不存在", data={"pk": pk})
        instance.status = 1
        await instance.save()

        serialized_data = await DemoResponse.from_orm_model(instance)
        return ApiResponse.success(
            data=serialized_data.model_dump(mode="json"),
            message="激活成功",
        )

    @action(detail=True, methods=["POST"])
    async def deactivate(self, request: Request, pk: str):
        """
        停用操作 - 对象级别的 action

        访问路径: POST /demos/{pk}/deactivate
        """
        instance = await self.get_object(pk)
        if not instance:
            raise NotFoundError(message="记录不存在", data={"pk": pk})
        instance.status = 0
        await instance.save()

        serialized_data = await DemoResponse.from_orm_model(instance)
        return ApiResponse.success(
            data=serialized_data.model_dump(mode="json"),
            message="停用成功",
        )

    @action(detail=False, methods=["POST"])
    async def batch_create(self, request: Request, items_data: list[DemoCreate]):
        """
        批量创建 - 列表级别的 action

        访问路径: POST /demos/batch-create
        """
        created_records = []
        for create_data in items_data:
            instance = await self.perform_create(create_data)
            created_records.append(instance)

        return ApiResponse.success(
            data={"count": len(created_records)},
            message=f"成功创建 {len(created_records)} 条记录",
        )

    @action(detail=False, methods=["POST"])
    async def background_task(
        self,
        request: Request,
        task_request: BackgroundTaskRequest,
        background_tasks: BackgroundTasks,
    ):
        """
        后台任务 - 展示 FastAPI BackgroundTasks 的使用

        访问路径: POST /demos/background-task
        """
        background_tasks.add_task(
            send_notification, email=task_request.email, message=task_request.message
        )
        background_tasks.add_task(
            write_log_to_file, task_id=task_request.task_id, data=task_request.model_dump()
        )

        logger.info("[主请求] 已添加后台任务, 立即返回响应")

        return ApiResponse.success(
            data={
                "task_id": task_request.task_id,
                "status": "processing",
                "message": "任务已提交, 正在后台处理",
                "submitted_at": datetime.now().isoformat(),
            },
            message="后台任务已启动",
        )


# 统一的 router,包含所有功能
demo_router = as_router(
    DemoViewSet,
    prefix="/demos",
    tags=["Demo"],
)
