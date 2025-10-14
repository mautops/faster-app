from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class DemoCreate(BaseModel):
    """创建 Demo 的请求 Schema - 自定义验证和描述"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Demo 名称",
        examples=["我的第一个 Demo"],
    )
    status: Optional[int] = Field(
        default=1, description="状态:1-激活, 0-未激活", examples=[1]
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """自定义验证:名称不能包含特殊字符"""
        if any(char in v for char in ["<", ">", "&", "'"]):
            raise ValueError("名称不能包含特殊字符")
        return v.strip()


class DemoUpdate(BaseModel):
    """更新 Demo 的请求 Schema - 所有字段可选"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Demo 名称"
    )
    status: Optional[int] = Field(None, description="状态:1-激活, 0-未激活")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if any(char in v for char in ["<", ">", "&", "'"]):
            raise ValueError("名称不能包含特殊字符")
        return v.strip()


class DemoResponse(BaseModel):
    """Demo 响应 Schema - 完全自定义输出格式"""

    id: UUID = Field(..., description="记录ID")
    name: str = Field(..., description="Demo 名称")
    status: int = Field(..., description="状态")
    status_display: str = Field(..., description="状态显示文本")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "示例 Demo",
                "status": 1,
                "status_display": "激活",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }

    @staticmethod
    def get_status_display(status: int) -> str:
        """获取状态的显示文本"""
        return "激活" if status == 1 else "未激活"

    @classmethod
    async def from_orm_model(cls, obj):
        """从 ORM 对象创建响应"""
        return cls(
            id=obj.id,
            name=obj.name,
            status=obj.status,
            status_display=cls.get_status_display(obj.status),
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


class BackgroundTaskRequest(BaseModel):
    """后台任务请求"""

    email: str = Field(
        ..., description="接收通知的邮箱地址", examples=["user@example.com"]
    )
    message: str = Field(..., description="通知消息内容", examples=["您的任务已完成"])
    task_id: str = Field(default="task-001", description="任务ID")


class DemoStatistics(BaseModel):
    """Demo 统计信息"""

    total: int = Field(..., description="总数")
    active: int = Field(..., description="激活数")
    inactive: int = Field(..., description="未激活数")
