"""
模型基类, 使用 pydantic 库管理模型
"""

import re
from deprecated import deprecated
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


class EnumModel(Model):
    """模型基类，支持子类自定义状态枚举

    示例:

    子类中定义 StrEnum 枚举

    class TaskStatusEnum(StrEnum):
        # 任务状态枚举 \n
        PENDING = "pending" \n
        RUNNING = "running" \n
        COMPLETED = "completed" \n
        FAILED = "failed"

    则自动创建 task_status 字段，默认状态为 PENDING
    """

    class StatusEnum(StrEnum):
        """默认状态枚举"""

        ACTIVE = "active"
        INACTIVE = "inactive"

    @staticmethod
    def _enum_class_to_field_name(enum_class_name: str) -> str:
        """
        将枚举类名转换为字段名
        例如: StatusEnum -> status, OrderStatusEnum -> order_status
        """
        # 去掉 Enum 后缀
        name = enum_class_name
        if name.endswith("Enum"):
            name = name[:-4]

        # 将驼峰命名转换为蛇形命名
        # 在大写字母前插入下划线，然后转换为小写
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

        return name

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        enum_class = getattr(cls, "StatusEnum", EnumModel.StatusEnum)
        is_custom_enum = enum_class is not EnumModel.StatusEnum

        field_name = (
            EnumModel._enum_class_to_field_name(enum_class.__name__)
            if is_custom_enum
            else "status"
        )
        default_value = list(enum_class)[0].value

        setattr(
            cls,
            field_name,
            CharEnumField(enum_class, default=default_value, verbose_name="状态"),
        )

    class Meta:
        abstract = True


class StatusModel(Model):
    """模型基类"""

    class StatusEnum(IntEnum):
        """状态枚举"""

        ACTIVE = 1
        INACTIVE = 0

    status = IntEnumField(default=1, verbose_name="状态", enum_type=StatusEnum)

    @deprecated(version="0.0.40", reason="StatusModel 已弃用，请使用 EnumModel 代替。")
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

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

    @deprecated(version="0.0.40", reason="ScopeModel 已弃用，请使用 EnumModel 代替。")
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    class Meta:
        abstract = True
