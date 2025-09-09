"""
模型基类, 使用 pydantic 库管理模型
"""

from enum import IntEnum, StrEnum
from tortoise import Model
from tortoise.fields import (
    IntEnumField,
    UUIDField,
    DatetimeField,
    CharEnumField,
    BooleanField,
    TextField,
)


class UUIDModel(Model):
    """模型基类"""

    id = UUIDField(pk=True, verbose_name="ID")

    class Meta:
        abstract = True


class DateTimeModel(Model):
    """模型基类"""

    created_at = DatetimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = DatetimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True


class StatusModel(Model):
    """模型基类"""

    class StatusEnum(IntEnum):
        """状态枚举"""

        ACTIVE = 1
        INACTIVE = 0

    status = IntEnumField(default=1, verbose_name="状态", enum_type=StatusEnum)

    class Meta:
        abstract = True

    def validate_status(self):
        """如果状态枚举 不存在或不是 IntEnum 类型, 则抛出异常"""
        # 检查是否存在 StatusEnum 属性
        if not hasattr(self, "StatusEnum"):
            raise ValueError(f"{self.__class__.__name__} 必须定义 StatusEnum")

        # 检查 StatusEnum 是否是 IntEnum 的子类
        if not (
            isinstance(self.StatusEnum, type) and issubclass(self.StatusEnum, IntEnum)
        ):
            raise ValueError(
                f"{self.__class__.__name__}.StatusEnum 必须是 IntEnum 的子类"
            )

        # 检查当前状态值是否在枚举中
        try:
            self.StatusEnum(self.status)
        except ValueError:
            valid_values = [e.value for e in self.StatusEnum]
            raise ValueError(f"状态值 {self.status} 不在有效枚举值 {valid_values} 中")


class ScopeModel(Model):
    """作用域模型基类，存储作用域"""

    class ScopeEnum(StrEnum):
        """作用域枚举"""

        SYSTEM = "system"
        TENANT = "tenant"
        PROJECT = "project"
        OBJECT = "object"

    scope = CharEnumField(ScopeEnum, default=ScopeEnum.PROJECT, verbose_name="作用域")

    class Meta:
        abstract = True


class SyncTimeModel(Model):
    """add sync_time field to model"""

    sync_time = DatetimeField(verbose_name="同步时间", blank=True, null=True)

    class Meta:
        abstract = True


class SyncCrontabModel(SyncTimeModel):
    """add sync_crontab field to model"""

    sync_crontab = DatetimeField(verbose_name="定时同步", null=True, blank=True)
    sync_status = BooleanField(verbose_name="同步状态", default=False)
    sync_error_message = TextField(verbose_name="同步错误", blank=True, null=True)

    class Meta:
        abstract = True
