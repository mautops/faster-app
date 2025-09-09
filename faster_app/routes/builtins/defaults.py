from fastapi import APIRouter
from settings import configs

router = APIRouter()


@router.get("/")
async def default():
    return {
        "message": f"Make {configs.PROJECT_NAME} Great Again",
        "version": configs.VERSION,
    }
