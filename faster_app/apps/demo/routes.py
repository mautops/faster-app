from fastapi import APIRouter
from faster_app.settings import configs
from pydantic import BaseModel, Field

router = APIRouter(prefix="/demo", tags=["demo"])


class DemoRequest(BaseModel):
    data: str = Field(default="world")


@router.post("/")
async def demo(request: DemoRequest):
    return {
        "message": f"Make {configs.PROJECT_NAME}",
        "version": configs.VERSION,
        "hello": request.data,
    }
