from fastapi import APIRouter, Depends
from faster_app.settings import configs
from pydantic import BaseModel, Field
from faster_app.settings import logger
from faster_app.apps.demo.models import DemoModel
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.tortoise import apaginate
from tortoise.contrib.pydantic import pydantic_model_creator
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/demo", tags=["Demo"])

# 创建 Pydantic 模型用于序列化
DemoModelPydantic = pydantic_model_creator(DemoModel, name="DemoModel")


class DemoRequest(BaseModel):
    message: str = Field(default="world")


@router.post("/")
async def demo(request: DemoRequest):
    logger.info(f"demo request: {request}")
    return JSONResponse(
        content={
            "message": f"Make {configs.PROJECT_NAME}",
            "version": configs.VERSION,
            "hello": request.message,
        },
        status_code=200,
    )


@router.get("/models")
async def pagination(
    params: Params = Depends(Params.as_query),
) -> Page[DemoModelPydantic]:
    return await apaginate(queryset=DemoModel.all(), params=params)
