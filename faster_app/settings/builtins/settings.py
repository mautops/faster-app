"""
应用配置文件
"""

from typing import Optional
from pydantic_settings import BaseSettings


class DefaultSettings(BaseSettings):
    """应用设置"""

    # 基础配置
    PROJECT_NAME: str = "Faster APP"
    VERSION: str = "0.0.1"
    DEBUG: bool = True

    # Server 配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # API 配置
    API_V1_STR: str = "/api/v1"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库配置
    DB_ENGINE: str = "tortoise.backends.asyncpg"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_DATABASE: str = "faster_app"

    TORTOISE_ORM: Optional[dict] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 动态生成 TORTOISE_ORM 配置，确保使用实际的配置值
        self.TORTOISE_ORM = {
            "connections": {
                "development": {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {"file_path": f"{self.get_db_name()}.db"},
                },
                "production": {
                    "engine": self.DB_ENGINE,
                    "credentials": {
                        "host": self.DB_HOST,
                        "port": self.DB_PORT,
                        "user": self.DB_USER,
                        "password": self.DB_PASSWORD,
                        "database": self.get_db_name(),
                    },
                },
            },
            "apps": {
                "models": {
                    # "models": ["apps.llm.models"],  # 这里不要硬编码，由自动发现填充
                    "default_connection": "development" if self.DEBUG else "production",
                }
            },
        }

    def get_db_name(self) -> str:
        # PROJECT_NAME 转换成小写，去掉空格，加上下划线
        return self.PROJECT_NAME.lower().replace(" ", "_")

    class Config:
        env_file = ".env"
        exclude_from_env = {"TORTOISE_ORM"}
        extra = "ignore"
