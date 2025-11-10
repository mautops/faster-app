"""
应用配置 - 使用分组配置结构
"""

import os
from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from faster_app.settings.groups import (
    ServerSettings,
    JWTSettings,
    DatabaseSettings,
    LogSettings,
)


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    project_name: str = "Faster APP"
    version: str = "0.0.1"
    debug: bool = True  # 生产环境中应设置为 False

    # API 配置
    api_v1_str: str = "/api/v1"

    # 配置组
    server: ServerSettings = ServerSettings()
    jwt: JWTSettings = JWTSettings()
    database: DatabaseSettings = DatabaseSettings()
    log: LogSettings = LogSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FASTER_",
        env_nested_delimiter="__",  # 支持嵌套：FASTER_DATABASE__HOST
        extra="ignore",
    )

    def __init__(self, **kwargs):
        """
        初始化配置，支持 DATABASE_URL

        优先级：
        1. 构造函数参数
        2. DATABASE_URL / FASTER_DATABASE_URL 环境变量
        3. 独立的 FASTER_DATABASE__* 环境变量
        4. 默认值
        """
        # 检查 DATABASE_URL（优先使用带前缀的）
        database_url = os.getenv("FASTER_DATABASE_URL") or os.getenv("DATABASE_URL")

        if database_url and "database" not in kwargs:
            # 如果设置了 DATABASE_URL 且没有手动传入 database 参数
            try:
                kwargs["database"] = DatabaseSettings.from_database_url(database_url)
            except ValueError as e:
                # URL 解析失败，发出警告但不中断
                import warnings

                warnings.warn(f"DATABASE_URL 解析失败: {e}，使用默认配置", UserWarning)

        super().__init__(**kwargs)

    @field_validator("jwt", mode="before")
    @classmethod
    def validate_jwt_in_production(cls, v, info):
        """验证生产环境 JWT 配置"""
        debug_mode = info.data.get("debug", True)

        # 确保 v 是字典或 JWTSettings 对象
        if isinstance(v, JWTSettings):
            jwt_dict = v.model_dump()
        elif isinstance(v, dict):
            jwt_dict = v
        else:
            return v

        if not debug_mode:
            # 检查 secret_key
            secret_key = jwt_dict.get("secret_key")
            if isinstance(secret_key, SecretStr):
                secret_value = secret_key.get_secret_value()
            elif isinstance(secret_key, str):
                secret_value = secret_key
            else:
                secret_value = str(secret_key) if secret_key else ""

            # 生产环境检查默认密钥
            if secret_value == "your-secret-key-here-change-in-production":
                raise ValueError(
                    "生产环境必须修改 jwt.secret_key！"
                    "请通过环境变量 FASTER_JWT__SECRET_KEY 设置安全的密钥"
                )

            # 检查密钥长度（至少 32 个字符）
            if len(secret_value) < 32:
                raise ValueError(
                    f"生产环境 jwt.secret_key 长度必须至少 32 个字符，"
                    f"当前长度: {len(secret_value)}"
                )

        return v

    @field_validator("database", mode="before")
    @classmethod
    def validate_database_in_production(cls, v, info):
        """验证生产环境数据库配置"""
        debug_mode = info.data.get("debug", True)

        # 确保 v 是字典或 DatabaseSettings 对象
        if isinstance(v, DatabaseSettings):
            db_dict = v.model_dump()
        elif isinstance(v, dict):
            db_dict = v
        else:
            return v

        if not debug_mode:
            # 检查密码
            password = db_dict.get("password")
            if isinstance(password, SecretStr):
                password_value = password.get_secret_value()
            elif isinstance(password, str):
                password_value = password
            else:
                password_value = str(password) if password else ""

            # 检查弱密码
            weak_passwords = ["postgres", "password", "123456", "admin", "root"]
            if password_value in weak_passwords:
                raise ValueError(
                    f"生产环境不能使用弱密码 '{password_value}'！"
                    "请通过环境变量 FASTER_DATABASE__PASSWORD 设置强密码"
                )

            # 检查密码长度（至少 8 个字符）
            if len(password_value) < 8:
                raise ValueError(
                    f"生产环境数据库密码长度必须至少 8 个字符，"
                    f"当前长度: {len(password_value)}"
                )

        return v

    @model_validator(mode="after")
    def validate_production_settings(self):
        """模型级别的生产环境验证"""
        # 生产环境检查
        if not self.debug:
            # 1. 检查服务器配置
            if self.server.host == "0.0.0.0":
                import warnings

                warnings.warn(
                    "生产环境使用 server.host=0.0.0.0 可能存在安全风险，"
                    "建议使用具体的 IP 地址或域名",
                    UserWarning,
                )

            # 2. PostgreSQL 生产环境配置检查
            if self.database.type == "postgres":
                if self.database.host in ["localhost", "127.0.0.1"]:
                    import warnings

                    warnings.warn(
                        "生产环境数据库使用 localhost 可能配置错误，"
                        "请确认数据库连接配置是否正确",
                        UserWarning,
                    )

            # 3. Token 过期时间检查
            if self.jwt.access_token_expire_minutes < 5:
                raise ValueError(
                    f"生产环境 jwt.access_token_expire_minutes 不应少于 5 分钟，"
                    f"当前值: {self.jwt.access_token_expire_minutes}"
                )

            # 4. 检查项目名称
            if self.project_name == "Faster APP":
                import warnings

                warnings.warn(
                    "建议在生产环境修改 project_name 为实际项目名称", UserWarning
                )

        return self

    @property
    def TORTOISE_ORM(self) -> dict:
        """
        动态生成 Tortoise ORM 配置

        Returns:
            Tortoise ORM 配置字典
        """
        # PostgreSQL 连接配置
        postgres_credentials = {
            "host": self.database.host,
            "port": self.database.port,
            "user": self.database.user,
            "password": self.database.password.get_secret_value(),
            "database": self.database.database,
        }

        # 如果配置了 schema，添加到连接配置
        if self.database.db_schema:
            postgres_credentials["schema"] = self.database.db_schema

        return {
            "connections": {
                "SQLITE": {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {
                        "file_path": f"{self._normalize_db_name(self.project_name)}.db"
                    },
                },
                "POSTGRES": {
                    "engine": self.database.engine,
                    "credentials": postgres_credentials,
                },
            },
            "apps": {"models": {"default_connection": self.database.type.upper()}},
        }

    def _normalize_db_name(self, project_name: str) -> str:
        """
        将项目名称转换为适合数据库的格式

        规则:
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

        # 移除特殊字符, 只保留字母、数字和下划线
        db_name = re.sub(r"[^a-z0-9_]", "", db_name)

        # 确保以字母开头
        if db_name and not db_name[0].isalpha():
            db_name = "app_" + db_name

        # 如果为空或过短, 使用默认前缀
        if not db_name or len(db_name) < 2:
            db_name = "app_db"

        # 限制长度(数据库名称通常有长度限制)
        if len(db_name) > 50:
            db_name = db_name[:49].rstrip("_")

        return db_name


# 向后兼容的别名
DefaultSettings = Settings
