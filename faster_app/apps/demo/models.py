from enum import StrEnum
from faster_app.models.base import UUIDModel, DateTimeModel, EnumModel
from tortoise import fields


class DemoModel(UUIDModel, DateTimeModel, EnumModel):
    """demo model"""

    class TaskStatusEnum(StrEnum):
        """任务状态枚举"""

        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"

    name = fields.CharField(max_length=255)

    class Meta:
        table = "demo"
        table_description = "demo model"

    def __str__(self):
        return self.name
