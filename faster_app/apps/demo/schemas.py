from pydantic import BaseModel, Field


class BackgroundTaskRequest(BaseModel):
    email: str = Field(
        ..., description="接收通知的邮箱地址", example="user@example.com"
    )
    message: str = Field(..., description="通知消息内容", example="您的任务已完成")
    task_id: str = Field(default="task-001", description="任务ID")
