"""
日志配置组
"""

from pydantic import BaseModel, field_validator


class LogSettings(BaseModel):
    """日志配置组"""

    level: str = "INFO"
    format: str = "STRING"

    @field_validator("level")
    @classmethod
    def validate_level(cls, v):
        """验证日志级别"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"log.level 必须是 {allowed_levels} 之一，当前值: {v}")
        return v_upper
