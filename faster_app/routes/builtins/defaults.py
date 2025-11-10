from fastapi import APIRouter
from faster_app.settings import configs

router = APIRouter()


@router.get("/")
async def default():
    return {
        "message": f"Make {configs.project_name}",
        "version": configs.version,
    }
