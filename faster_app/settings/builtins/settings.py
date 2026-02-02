"""
应用配置文件

使用嵌套配置模型，结构更清晰、更易维护
"""

from pydantic import BaseModel, Field, model_validator  # noqa: I001
from pydantic_settings import BaseSettings, SettingsConfigDict


# 配置分组


class ServerConfig(BaseModel):
    """服务器配置"""

    HOST: str = Field(default="0.0.0.0", description="监听地址", validation_alias="HOST")
    PORT: int = Field(default=8000, description="监听端口", validation_alias="PORT")


class JWTConfig(BaseModel):
    """JWT 认证配置"""

    SECRET_KEY: str = Field(
        default="your-secret-key-here-change-in-production",
        description="JWT 密钥，生产环境必须修改",
        validation_alias="SECRET_KEY",
    )
    ALGORITHM: str = Field(default="HS256", description="加密算法", validation_alias="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="访问令牌过期时间（分钟）",
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )


class DatabaseConfig(BaseModel):
    """数据库配置"""

    URL: str = Field(
        default="sqlite://db.sqlite", description="数据库连接 URL", validation_alias="DB_URL"
    )


class LogConfig(BaseModel):
    """日志配置"""

    LEVEL: str = Field(default="INFO", description="日志级别", validation_alias="LOG_LEVEL")
    FORMAT: str = Field(default="STRING", description="日志格式", validation_alias="LOG_FORMAT")
    TO_FILE: bool = Field(
        default=False, description="是否输出到文件", validation_alias="LOG_TO_FILE"
    )
    FILE_PATH: str = Field(
        default="logs/app.log", description="日志文件路径", validation_alias="LOG_FILE_PATH"
    )
    BACKUP_COUNT: int = Field(
        default=10, description="备份文件数量", validation_alias="LOG_FILE_BACKUP_COUNT"
    )


class LifespanConfig(BaseModel):
    """生命周期配置"""

    ENABLE_DATABASE: bool = Field(
        default=False,
        description="是否启用数据库 lifespan",
        validation_alias="ENABLE_DATABASE_LIFESPAN",
    )
    ENABLE_APPS: bool = Field(
        default=False, description="是否启用应用 lifespan", validation_alias="ENABLE_APPS_LIFESPAN"
    )
    ENABLE_USER: bool = Field(
        default=False,
        description="是否启用用户自定义 lifespan",
        validation_alias="ENABLE_USER_LIFESPANS",
    )


class ThrottleConfig(BaseModel):
    """限流配置"""

    RATES: dict[str, str] = Field(
        default={"user": "100/hour", "anon": "20/hour", "default": "100/hour"},
        description="限流速率配置",
        validation_alias="THROTTLE_RATES",
    )


class CORSConfig(BaseModel):
    """CORS 跨域配置"""

    ALLOW_ORIGINS: list[str] = Field(
        default=["*"],
        description="允许的源域名列表，生产环境应明确指定",
        validation_alias="CORS_ALLOW_ORIGINS",
    )
    ALLOW_CREDENTIALS: bool = Field(
        default=False,
        description="是否允许携带凭证",
        validation_alias="CORS_ALLOW_CREDENTIALS",
    )
    ALLOW_METHODS: list[str] = Field(
        default=["*"], description="允许的 HTTP 方法", validation_alias="CORS_ALLOW_METHODS"
    )
    ALLOW_HEADERS: list[str] = Field(
        default=["*"], description="允许的请求头", validation_alias="CORS_ALLOW_HEADERS"
    )
    EXPOSE_HEADERS: list[str] = Field(
        default=[], description="暴露的响应头", validation_alias="CORS_EXPOSE_HEADERS"
    )
    MAX_AGE: int = Field(
        default=600, description="预检请求缓存时间（秒）", validation_alias="CORS_MAX_AGE"
    )

    @model_validator(mode="after")
    def validate_credentials_origins(self):
        """验证 credentials 和 origins 的组合安全性"""
        if self.ALLOW_CREDENTIALS and "*" in self.ALLOW_ORIGINS:
            raise ValueError("安全错误: ALLOW_CREDENTIALS=True 不能与 ALLOW_ORIGINS=['*'] 同时使用")
        return self


class TrustedHostConfig(BaseModel):
    """可信主机配置"""

    ENABLED: bool = Field(
        default=False,
        description="是否启用（生产环境建议启用）",
        validation_alias="TRUSTED_HOST_ENABLED",
    )
    HOSTS: list[str] = Field(
        default=["*"], description="允许的主机名列表", validation_alias="TRUSTED_HOSTS"
    )


class TimingConfig(BaseModel):
    """性能监控配置"""

    ENABLED: bool = Field(
        default=True,
        description="是否启用性能监控中间件",
        validation_alias="TIMING_ENABLED",
    )
    SLOW_THRESHOLD: float = Field(
        default=1.0, description="慢请求阈值（秒）", validation_alias="TIMING_SLOW_THRESHOLD"
    )


class RequestLoggingConfig(BaseModel):
    """请求日志配置"""

    ENABLED: bool = Field(
        default=True,
        description="是否启用请求日志中间件",
        validation_alias="REQUEST_LOGGING_ENABLED",
    )
    LOG_BODY: bool = Field(
        default=False,
        description="是否记录请求体（可能包含敏感信息）",
        validation_alias="REQUEST_LOGGING_LOG_BODY",
    )
    LOG_RESPONSE: bool = Field(
        default=False,
        description="是否记录响应体",
        validation_alias="REQUEST_LOGGING_LOG_RESPONSE",
    )


class GZipConfig(BaseModel):
    """GZip 压缩配置"""

    ENABLED: bool = Field(
        default=True, description="是否启用 GZip 压缩", validation_alias="GZIP_ENABLED"
    )
    MINIMUM_SIZE: int = Field(
        default=1000, description="最小压缩大小（字节）", validation_alias="GZIP_MINIMUM_SIZE"
    )


class MiddlewareConfig(BaseModel):
    """中间件配置（统一管理所有中间件配置）"""

    CORS: CORSConfig = Field(default_factory=CORSConfig)
    TRUSTED_HOST: TrustedHostConfig = Field(default_factory=TrustedHostConfig)
    TIMING: TimingConfig = Field(default_factory=TimingConfig)
    REQUEST_LOGGING: RequestLoggingConfig = Field(default_factory=RequestLoggingConfig)
    GZIP: GZipConfig = Field(default_factory=GZipConfig)


# 主配置类


class DefaultSettings(BaseSettings):
    """
    应用设置

    使用嵌套配置模型，结构更清晰。
    环境变量使用简单的大写命名，例如：
    - PROJECT_NAME="Faster APP"
    - DEBUG=true
    - HOST=0.0.0.0
    - PORT=8080
    - SECRET_KEY="your-secret"
    - DB_URL="sqlite://db.sqlite"
    - CORS_ALLOW_ORIGINS='["https://example.com"]'
    """

    # 基础配置
    PROJECT_NAME: str = Field(
        default="Faster APP", description="项目名称", validation_alias="PROJECT_NAME"
    )
    VERSION: str = Field(default="0.0.1", description="版本号", validation_alias="VERSION")
    DEBUG: bool = Field(default=True, description="调试模式", validation_alias="DEBUG")
    VALIDATE_ROUTES: bool = Field(
        default=True, description="是否启用路由冲突检测", validation_alias="VALIDATE_ROUTES"
    )

    # 数据库配置相关字段（用于从环境变量读取）
    # 注意：由于 pydantic_settings 的限制，嵌套 BaseModel 中的 validation_alias 无法从环境变量读取
    # 因此需要在顶层添加字段读取环境变量，然后通过 model_validator 传递给嵌套配置
    DB_URL: str = Field(
        default="sqlite://db.sqlite", description="数据库连接 URL", validation_alias="DB_URL"
    )
    ENABLE_DATABASE_LIFESPAN: bool = Field(
        default=False,
        description="是否启用数据库生命周期",
        validation_alias="ENABLE_DATABASE_LIFESPAN",
    )
    ENABLE_APPS_LIFESPAN: bool = Field(
        default=False,
        description="是否启用应用生命周期",
        validation_alias="ENABLE_APPS_LIFESPAN",
    )
    ENABLE_USER_LIFESPANS: bool = Field(
        default=False,
        description="是否启用用户自定义 lifespan",
        validation_alias="ENABLE_USER_LIFESPANS",
    )

    # 嵌套配置
    SERVER: ServerConfig = Field(default_factory=ServerConfig, description="服务器配置")
    JWT: JWTConfig = Field(default_factory=JWTConfig, description="JWT 配置")
    DATABASE: DatabaseConfig = Field(default_factory=DatabaseConfig, description="数据库配置")
    LOG: LogConfig = Field(default_factory=LogConfig, description="日志配置")
    LIFESPAN: LifespanConfig = Field(default_factory=LifespanConfig, description="生命周期配置")
    THROTTLE: ThrottleConfig = Field(default_factory=ThrottleConfig, description="限流配置")
    MIDDLEWARE: MiddlewareConfig = Field(default_factory=MiddlewareConfig, description="中间件配置")

    @model_validator(mode="after")
    def validate_production_settings(self):
        """生产环境配置验证"""
        # 从顶层字段设置嵌套配置（修复 pydantic_settings 嵌套配置无法读取环境变量的问题）
        # 注意：使用正确的大写字段名
        self.DATABASE.URL = self.DB_URL
        self.LIFESPAN.ENABLE_DATABASE = self.ENABLE_DATABASE_LIFESPAN
        self.LIFESPAN.ENABLE_APPS = self.ENABLE_APPS_LIFESPAN
        self.LIFESPAN.ENABLE_USER = self.ENABLE_USER_LIFESPANS

        if not self.DEBUG:
            # 生产环境检查
            if self.JWT.SECRET_KEY == "your-secret-key-here-change-in-production":
                raise ValueError("生产环境必须修改 JWT secret_key")

            # CORS 安全检查
            cors = self.MIDDLEWARE.CORS
            if cors.ALLOW_CREDENTIALS and "*" in cors.ALLOW_ORIGINS:
                raise ValueError(
                    "生产环境 CORS 配置不安全: "
                    "allow_credentials=True 不能与 allow_origins=['*'] 同时使用"
                )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
