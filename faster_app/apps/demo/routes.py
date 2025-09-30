from fastapi import APIRouter, Depends
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
