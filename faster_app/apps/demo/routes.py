from fastapi import APIRouter, Depends, HTTPException
from faster_app.settings import configs
from pydantic import BaseModel, Field
from faster_app.settings import logger
from faster_app.apps.demo.models import DemoModel
from tortoise_pagination import Pagination, Page
from tortoise.contrib.pydantic import pydantic_model_creator
from faster_app.utils.response import success_response
from faster_app.utils.exceptions import (
    BusinessException,
    AuthenticationException,
    ResourceNotFoundException,
)


router = APIRouter(prefix="/demo", tags=["demo"])

# 创建 Pydantic 模型用于序列化
DemoModelPydantic = pydantic_model_creator(DemoModel, name="DemoModel")


class DemoRequest(BaseModel):
    data: str = Field(default="world")


@router.post("/")
async def demo(request: DemoRequest):
    """演示接口 - 展示新的响应格式"""
    logger.info(f"demo request: {request}")

    # 演示业务异常处理
    if request.data == "error":
        raise BusinessException(
            "这是一个演示业务异常", detail="请不要传入 'error' 作为参数"
        )

    # 演示 HTTP 异常处理
    if request.data == "http_error":
        raise HTTPException(status_code=400, detail="这是一个演示 HTTP 异常")

    data = {
        "project": configs.PROJECT_NAME,
        "version": configs.VERSION,
        "hello": request.data,
    }

    return success_response(data=data, message="演示接口调用成功")


@router.get("/models")
async def pagination(
    pagination: Pagination = Depends(Pagination.from_query),
) -> Page[DemoModelPydantic]:
    """分页查询演示模型"""
    return await pagination.paginated_response(DemoModel.all(), DemoModelPydantic)


@router.get("/test-exceptions")
async def test_exceptions(exception_type: str = "business"):
    """测试异常处理器"""
    if exception_type == "business":
        raise BusinessException("这是一个业务异常测试")
    elif exception_type == "auth":
        raise AuthenticationException("这是一个认证异常测试")
    elif exception_type == "not_found":
        raise ResourceNotFoundException("这是一个资源未找到异常测试")
    elif exception_type == "http":
        raise HTTPException(status_code=400, detail="这是一个 HTTP 异常测试")
    elif exception_type == "validation":
        # 触发验证错误
        raise ValueError("这是一个值错误测试")
    elif exception_type == "server":
        # 触发服务器错误
        raise Exception("这是一个服务器内部错误测试")
    else:
        return success_response(message="异常处理器测试正常")
