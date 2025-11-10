"""
服务器配置组
"""

from pydantic import BaseModel, field_validator


class ServerSettings(BaseModel):
    """服务器配置组"""

    host: str = "0.0.0.0"
    port: int = 8000

    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        """验证端口号范围"""
        if not 1 <= v <= 65535:
            raise ValueError(f"server.port 必须在 1-65535 之间，当前值: {v}")
        return v

