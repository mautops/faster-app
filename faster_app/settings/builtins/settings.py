"""
应用配置文件

使用嵌套配置模型，结构更清晰、更易维护
"""

from pydantic import BaseModel, Field, model_validator  # noqa: I001
from pydantic_settings import BaseSettings, SettingsConfigDict


# 配置分组


class ServerConfig(BaseModel):
    """服务器配置"""

    host: str = Field(default="0.0.0.0", description="监听地址", validation_alias="HOST")
    port: int = Field(default=8000, description="监听端口", validation_alias="PORT")


class JWTConfig(BaseModel):
    """JWT 认证配置"""

    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        description="JWT 密钥，生产环境必须修改",
        validation_alias="SECRET_KEY",
    )
    algorithm: str = Field(default="HS256", description="加密算法", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        description="访问令牌过期时间（分钟）",
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )


class DatabaseConfig(BaseModel):
    """数据库配置"""

    url: str = Field(
        default="sqlite://db.sqlite", description="数据库连接 URL", validation_alias="DB_URL"
    )


class LogConfig(BaseModel):
    """日志配置"""

    level: str = Field(default="INFO", description="日志级别", validation_alias="LOG_LEVEL")
    format: str = Field(default="STRING", description="日志格式", validation_alias="LOG_FORMAT")
    to_file: bool = Field(
        default=False, description="是否输出到文件", validation_alias="LOG_TO_FILE"
    )
    file_path: str = Field(
        default="logs/app.log", description="日志文件路径", validation_alias="LOG_FILE_PATH"
    )
    backup_count: int = Field(
        default=10, description="备份文件数量", validation_alias="LOG_FILE_BACKUP_COUNT"
    )


class LifespanConfig(BaseModel):
    """生命周期配置"""

    enable_database: bool = Field(
        default=False,
        description="是否启用数据库 lifespan",
        validation_alias="ENABLE_DATABASE_LIFESPAN",
    )
    enable_apps: bool = Field(
        default=False, description="是否启用应用 lifespan", validation_alias="ENABLE_APPS_LIFESPAN"
    )
    enable_user: bool = Field(
        default=False,
        description="是否启用用户自定义 lifespan",
        validation_alias="ENABLE_USER_LIFESPANS",
    )


class ThrottleConfig(BaseModel):
    """限流配置"""

    rates: dict[str, str] = Field(
        default={"user": "100/hour", "anon": "20/hour", "default": "100/hour"},
        description="限流速率配置",
        validation_alias="THROTTLE_RATES",
    )


class CORSConfig(BaseModel):
    """CORS 跨域配置"""

    allow_origins: list[str] = Field(
        default=["*"],
        description="允许的源域名列表，生产环境应明确指定",
        validation_alias="CORS_ALLOW_ORIGINS",
    )
    allow_credentials: bool = Field(
        default=False,
        description="是否允许携带凭证",
        validation_alias="CORS_ALLOW_CREDENTIALS",
    )
    allow_methods: list[str] = Field(
        default=["*"], description="允许的 HTTP 方法", validation_alias="CORS_ALLOW_METHODS"
    )
    allow_headers: list[str] = Field(
        default=["*"], description="允许的请求头", validation_alias="CORS_ALLOW_HEADERS"
    )
    expose_headers: list[str] = Field(
        default=[], description="暴露的响应头", validation_alias="CORS_EXPOSE_HEADERS"
    )
    max_age: int = Field(
        default=600, description="预检请求缓存时间（秒）", validation_alias="CORS_MAX_AGE"
    )

    @model_validator(mode="after")
    def validate_credentials_origins(self):
        """验证 credentials 和 origins 的组合安全性"""
        if self.allow_credentials and "*" in self.allow_origins:
            raise ValueError("安全错误: allow_credentials=True 不能与 allow_origins=['*'] 同时使用")
        return self


class TrustedHostConfig(BaseModel):
    """可信主机配置"""

    enabled: bool = Field(
        default=False,
        description="是否启用（生产环境建议启用）",
        validation_alias="TRUSTED_HOST_ENABLED",
    )
    hosts: list[str] = Field(
        default=["*"], description="允许的主机名列表", validation_alias="TRUSTED_HOSTS"
    )


class TimingConfig(BaseModel):
    """性能监控配置"""

    enabled: bool = Field(
        default=True,
        description="是否启用性能监控中间件",
        validation_alias="TIMING_ENABLED",
    )
    slow_threshold: float = Field(
        default=1.0, description="慢请求阈值（秒）", validation_alias="TIMING_SLOW_THRESHOLD"
    )


class RequestLoggingConfig(BaseModel):
    """请求日志配置"""

    enabled: bool = Field(
        default=True,
        description="是否启用请求日志中间件",
        validation_alias="REQUEST_LOGGING_ENABLED",
    )
    log_body: bool = Field(
        default=False,
        description="是否记录请求体（可能包含敏感信息）",
        validation_alias="REQUEST_LOGGING_LOG_BODY",
    )
    log_response: bool = Field(
        default=False,
        description="是否记录响应体",
        validation_alias="REQUEST_LOGGING_LOG_RESPONSE",
    )


class GZipConfig(BaseModel):
    """GZip 压缩配置"""

    enabled: bool = Field(
        default=True, description="是否启用 GZip 压缩", validation_alias="GZIP_ENABLED"
    )
    minimum_size: int = Field(
        default=1000, description="最小压缩大小（字节）", validation_alias="GZIP_MINIMUM_SIZE"
    )


class MiddlewareConfig(BaseModel):
    """中间件配置（统一管理所有中间件配置）"""

    cors: CORSConfig = Field(default_factory=CORSConfig)
    trusted_host: TrustedHostConfig = Field(default_factory=TrustedHostConfig)
    timing: TimingConfig = Field(default_factory=TimingConfig)
    request_logging: RequestLoggingConfig = Field(default_factory=RequestLoggingConfig)
    gzip: GZipConfig = Field(default_factory=GZipConfig)


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
    project_name: str = Field(
        default="Faster APP", description="项目名称", validation_alias="PROJECT_NAME"
    )
    version: str = Field(default="0.0.1", description="版本号", validation_alias="VERSION")
    debug: bool = Field(default=True, description="调试模式", validation_alias="DEBUG")
    validate_routes: bool = Field(
        default=True, description="是否启用路由冲突检测", validation_alias="VALIDATE_ROUTES"
    )

    # 数据库配置相关字段（用于从环境变量读取）
    # 注意：由于 pydantic_settings 的限制，嵌套 BaseModel 中的 validation_alias 无法从环境变量读取
    # 因此需要在顶层添加字段读取环境变量，然后通过 model_validator 传递给嵌套配置
    db_url: str = Field(
        default="sqlite://db.sqlite", description="数据库连接 URL", validation_alias="DB_URL"
    )
    enable_database_lifespan: bool = Field(
        default=False,
        description="是否启用数据库生命周期",
        validation_alias="ENABLE_DATABASE_LIFESPAN",
    )
    enable_apps_lifespan: bool = Field(
        default=False,
        description="是否启用应用生命周期",
        validation_alias="ENABLE_APPS_LIFESPAN",
    )
    enable_user_lifespans: bool = Field(
        default=False,
        description="是否启用用户自定义 lifespan",
        validation_alias="ENABLE_USER_LIFESPANS",
    )

    # 嵌套配置
    server: ServerConfig = Field(default_factory=ServerConfig, description="服务器配置")
    jwt: JWTConfig = Field(default_factory=JWTConfig, description="JWT 配置")
    database: DatabaseConfig = Field(default_factory=DatabaseConfig, description="数据库配置")
    log: LogConfig = Field(default_factory=LogConfig, description="日志配置")
    lifespan: LifespanConfig = Field(default_factory=LifespanConfig, description="生命周期配置")
    throttle: ThrottleConfig = Field(default_factory=ThrottleConfig, description="限流配置")
    middleware: MiddlewareConfig = Field(default_factory=MiddlewareConfig, description="中间件配置")

    @model_validator(mode="after")
    def validate_production_settings(self):
        """生产环境配置验证"""
        # 从顶层字段设置嵌套配置（修复 pydantic_settings 嵌套配置无法读取环境变量的问题）
        self.database.url = self.db_url
        self.lifespan.enable_database = self.enable_database_lifespan
        self.lifespan.enable_apps = self.enable_apps_lifespan
        self.lifespan.enable_user = self.enable_user_lifespans

        if not self.debug:
            # 生产环境检查
            if self.jwt.secret_key == "your-secret-key-here-change-in-production":
                raise ValueError("生产环境必须修改 JWT secret_key")

            # CORS 安全检查
            cors = self.middleware.cors
            if cors.allow_credentials and "*" in cors.allow_origins:
                raise ValueError(
                    "生产环境 CORS 配置不安全: "
                    "allow_credentials=True 不能与 allow_origins=['*'] 同时使用"
                )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
