from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks
from faster_app.apps.demo.schemas import BackgroundTaskRequest
from faster_app.apps.demo.tasks import send_notification, write_log_to_file
from faster_app.settings import configs
from pydantic import BaseModel, Field
from faster_app.settings import logger
from faster_app.apps.demo.models import DemoModel
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.tortoise import apaginate
from tortoise.contrib.pydantic import pydantic_model_creator
from faster_app.utils.response import ApiResponse
from http import HTTPStatus


router = APIRouter(prefix="/demo", tags=["Demo"])

# 创建 Pydantic 模型用于序列化
DemoModelPydantic = pydantic_model_creator(DemoModel, name="DemoModel")


class DemoRequest(BaseModel):
    message: str = Field(default="world")


@router.post("/")
async def demo(request: DemoRequest):
    """演示接口 - 返回项目信息"""
    logger.info(f"demo request: {request}")
    return ApiResponse.success(
        data={
            "message": f"Make {configs.PROJECT_NAME}",
            "version": configs.VERSION,
            "hello": request.message,
        },
        message="请求成功",
    )


@router.get("/error")
async def error():
    """演示错误处理接口"""
    try:
        raise Exception("这是一个测试错误")
    except Exception as e:
        logger.error(f"捕获到错误: {e}")
        return ApiResponse.error(
            message="操作失败",
            error_detail=f"{type(e).__name__}: {str(e)}",
            code=500,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@router.get("/models")
async def pagination(
    params: Params = Depends(),
) -> Page[DemoModelPydantic]:
    return await apaginate(query=DemoModel.all(), params=params)


@router.post("/background-task")
async def create_background_task(
    request: BackgroundTaskRequest,
    background_tasks: BackgroundTasks,
):
    """
    后台任务演示接口

    此接口展示如何使用 FastAPI 的 BackgroundTasks 来处理后台异步任务。
    接口会立即返回响应，而后台任务会在响应返回后继续执行。

    适用场景:
    - 发送邮件通知
    - 生成报表文件
    - 数据清理和归档
    - 日志记录
    - 调用第三方API
    """
    # 添加多个后台任务
    background_tasks.add_task(
        send_notification, email=request.email, message=request.message
    )

    background_tasks.add_task(
        write_log_to_file, task_id=request.task_id, data=request.model_dump()
    )

    logger.info("[主请求] 已添加后台任务，立即返回响应")

    return ApiResponse.success(
        data={
            "task_id": request.task_id,
            "status": "processing",
            "message": "任务已提交，正在后台处理",
            "submitted_at": datetime.now().isoformat(),
        },
        message="后台任务已启动，请查看日志了解执行情况",
    )
