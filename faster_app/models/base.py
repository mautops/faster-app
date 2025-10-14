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
)


class UUIDModel(Model):
    """模型基类"""

    id = UUIDField(primary_key=True, verbose_name="ID")

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


class ScopeModel(Model):
    """作用域模型基类, 存储作用域"""

    class ScopeEnum(StrEnum):
        """作用域枚举"""

        SYSTEM = "system"
        TENANT = "tenant"
        PROJECT = "project"
        OBJECT = "object"

    scope = CharEnumField(ScopeEnum, default=ScopeEnum.PROJECT, verbose_name="作用域")

    class Meta:
        abstract = True
