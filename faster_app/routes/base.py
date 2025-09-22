"""
统一返回格式
"""

from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一返回格式"""

    success: bool = Field(default=True, description="请求是否成功")
    code: int = Field(default=200, description="状态码")
    message: str = Field(description="响应消息")
    data: Optional[T] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class ErrorResponse(BaseModel):
    """错误响应格式"""

    success: bool = Field(default=False, description="请求是否成功")
    code: int = Field(description="错误状态码")
    message: str = Field(description="错误消息")
    detail: Optional[str] = Field(default=None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
