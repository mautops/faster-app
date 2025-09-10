from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/demo", tags=["demo"])


class DemoRequest(BaseModel):
    name: str


@router.post("/")
async def get_demo(request: DemoRequest):
    return {"message": f"Hello, {request.name}!"}
