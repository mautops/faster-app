"""
统一返回格式
"""

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一返回格式"""

    message: str
    data: dict
