"""
Demo 路由 - 展示三种 CRUD 开发模式

模式一:快速模式 - 完全自动生成(5 行代码搞定 CRUD)
模式二:平衡模式 - 部分自定义(灵活且高效)
模式三:完全控制 - 全部自定义(适合复杂业务)
"""

from datetime import datetime
from fastapi import APIRouter, BackgroundTasks
from faster_app.apps.demo.schemas import (
    BackgroundTaskRequest,
    DemoCreate,
    DemoUpdate,
    DemoStatistics,
)
from faster_app.apps.demo.tasks import send_notification, write_log_to_file
from faster_app.settings import logger
from faster_app.apps.demo.models import DemoModel
from faster_app.utils.crud import CRUDRouter, CRUDBase
from faster_app.utils.response import ApiResponse
from http import HTTPStatus


# ==================== 模式一:快速模式 ====================
# 5 行代码完成标准 CRUD, 适合快速原型开发

# 创建路由 - 自动生成所有 CRUD 接口
demo_quick_router = CRUDRouter(
    model=DemoModel,
    prefix="/demos-quick",
    tags=["Demo - 快速模式(自动生成)"],
    operations="CRUDL",  # 支持所有操作(默认值, 可以省略)
).get_router()

# 就这么简单！你已经有了完整的 CRUD 接口:
# GET    /demos-quick/          - 列表查询(分页)  [L]
# POST   /demos-quick/          - 创建              [C]
# GET    /demos-quick/{id}      - 查询单个          [R]
# PUT    /demos-quick/{id}      - 更新              [U]
# DELETE /demos-quick/{id}      - 删除              [D]


# ==================== 模式二:平衡模式 ====================
# 使用自定义 Schema, 保留灵活性, 适合大多数场景

demo_balanced_router = CRUDRouter(
    model=DemoModel,
    create_schema=DemoCreate,  # 自定义创建 Schema(带验证)
    update_schema=DemoUpdate,  # 自定义更新 Schema(带验证)
    # response_schema 不传, 自动生成
    prefix="/demos",
    tags=["Demo - 平衡模式(推荐)"],
).get_router()


# 在自动生成的基础上, 可以添加自定义路由
@demo_balanced_router.get("/statistics", response_model=DemoStatistics)
async def get_statistics():
    """获取统计信息 - 自定义端点"""
    total = await DemoModel.all().count()
    active = await DemoModel.filter(status=1).count()
    inactive = await DemoModel.filter(status=0).count()

    return DemoStatistics(
        total=total,
        active=active,
        inactive=inactive,
    )


@demo_balanced_router.post("/batch-create")
async def batch_create(items_data: list[DemoCreate]):
    """批量创建 - 自定义端点"""
    created_records = []
    for create_data in items_data:
        record = await DemoModel.create(**create_data.model_dump())
        created_records.append(record)

    return ApiResponse.success(
        data={"count": len(created_records)},
        message=f"成功创建 {len(created_records)} 条记录",
    )


# ==================== 模式三:完全控制模式 ====================
# 使用 CRUDBase 作为工具类, 手动定义所有路由
# 适合需要完全控制的复杂业务场景

demo_custom_router = APIRouter(prefix="/demos-custom", tags=["Demo - 完全控制模式"])

# 使用 CRUD 工具类处理数据操作
demo_crud = CRUDBase(
    model=DemoModel,
    create_schema=DemoCreate,
    update_schema=DemoUpdate,
)


@demo_custom_router.get("/")
async def list_demos(
    skip: int = 0,
    limit: int = 100,
    status: int | None = None,
):
    """
    自定义列表查询
    - 支持按状态筛选
    - 自定义分页参数
    - 自定义响应格式
    """
    filters = {}
    if status is not None:
        filters["status"] = status

    records = await demo_crud.get_multi(
        skip=skip,
        limit=limit,
        filters=filters,
        order_by=["-created_at"],  # 按创建时间倒序
    )

    total = await DemoModel.filter(**filters).count()

    return ApiResponse.success(
        data={
            "items": [
                await demo_crud.response_schema.from_tortoise_orm(record)
                for record in records
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        },
        message="查询成功",
    )


@demo_custom_router.post("/")
async def create_demo(create_data: DemoCreate):
    """
    自定义创建接口
    - 添加业务逻辑
    - 自定义响应格式
    """
    # 检查名称是否重复
    existing = await DemoModel.filter(name=create_data.name).first()
    if existing:
        return ApiResponse.error(
            message="名称已存在", status_code=HTTPStatus.BAD_REQUEST
        )

    # 创建记录
    record = await demo_crud.create(create_data)

    logger.info(f"创建 Demo: {record.id} - {record.name}")

    return ApiResponse.success(
        data=await demo_crud.response_schema.from_tortoise_orm(record),
        message="创建成功",
    )


@demo_custom_router.get("/{record_id}")
async def get_demo(record_id: str):
    """自定义查询单个接口"""
    record = await demo_crud.get(record_id)
    if not record:
        return ApiResponse.error(message="记录不存在", status_code=HTTPStatus.NOT_FOUND)

    return ApiResponse.success(
        data=await demo_crud.response_schema.from_tortoise_orm(record)
    )


@demo_custom_router.put("/{record_id}")
async def update_demo(record_id: str, update_data: DemoUpdate):
    """自定义更新接口"""
    record = await demo_crud.update(record_id, update_data)
    if not record:
        return ApiResponse.error(message="记录不存在", status_code=HTTPStatus.NOT_FOUND)

    logger.info(f"更新 Demo: {record.id} - {record.name}")

    return ApiResponse.success(
        data=await demo_crud.response_schema.from_tortoise_orm(record),
        message="更新成功",
    )


@demo_custom_router.delete("/{record_id}")
async def delete_demo(record_id: str):
    """自定义删除接口"""
    success = await demo_crud.delete(record_id)
    if not success:
        return ApiResponse.error(message="记录不存在", status_code=HTTPStatus.NOT_FOUND)

    logger.info(f"删除 Demo: {record_id}")

    return ApiResponse.success(message="删除成功")


@demo_balanced_router.post("/background-task")
async def create_background_task(
    request: BackgroundTaskRequest,
    background_tasks: BackgroundTasks,
):
    """
    后台任务演示接口

    此接口展示如何使用 FastAPI 的 BackgroundTasks 来处理后台异步任务。
    """
    background_tasks.add_task(
        send_notification, email=request.email, message=request.message
    )
    background_tasks.add_task(
        write_log_to_file, task_id=request.task_id, data=request.model_dump()
    )

    logger.info("[主请求] 已添加后台任务, 立即返回响应")

    return ApiResponse.success(
        data={
            "task_id": request.task_id,
            "status": "processing",
            "message": "任务已提交, 正在后台处理",
            "submitted_at": datetime.now().isoformat(),
        },
        message="后台任务已启动",
    )
