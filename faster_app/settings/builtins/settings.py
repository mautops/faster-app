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
    DEBUG: bool = True  # 生产环境中应设置为 False，可通过环境变量 DEBUG=false 覆盖

    # Server 配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RUN_ENV: str = "development"

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

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "STRING"

    TORTOISE_ORM: Optional[dict] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 动态生成 TORTOISE_ORM 配置，确保使用实际的配置值
        self.TORTOISE_ORM = {
            "connections": {
                "development": {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {
                        "file_path": f"{self._normalize_db_name(self.PROJECT_NAME)}.db"
                    },
                },
                "production": {
                    "engine": self.DB_ENGINE,
                    "credentials": {
                        "host": self.DB_HOST,
                        "port": self.DB_PORT,
                        "user": self.DB_USER,
                        "password": self.DB_PASSWORD,
                        "database": self.DB_DATABASE,
                    },
                },
            },
            "apps": {
                "models": {
                    # "models": ["apps.llm.models"],  # 这里不要硬编码，由自动发现填充
                    "default_connection": self.RUN_ENV,
                }
            },
        }

    def _normalize_db_name(self, project_name: str) -> str:
        """
        将项目名称转换为适合数据库的格式

        规则：
        1. 转换为小写
        2. 空格替换为下划线
        3. 移除或替换特殊字符
        4. 确保以字母开头
        5. 限制长度

        Args:
            project_name: 项目名称

        Returns:
            规范化后的数据库名称
        """
        import re

        # 转换为小写
        db_name = project_name.lower()

        # 替换空格和连字符为下划线
        db_name = re.sub(r"[\s\-]+", "_", db_name)

        # 移除特殊字符，只保留字母、数字和下划线
        db_name = re.sub(r"[^a-z0-9_]", "", db_name)

        # 确保以字母开头
        if db_name and not db_name[0].isalpha():
            db_name = "app_" + db_name

        # 如果为空或过短，使用默认前缀
        if not db_name or len(db_name) < 2:
            db_name = "app_db"

        # 限制长度（数据库名称通常有长度限制）
        if len(db_name) > 50:
            db_name = db_name[:49].rstrip("_")

        return db_name

    class Config:
        env_file = ".env"
        exclude_from_env = {"TORTOISE_ORM"}
        extra = "ignore"
