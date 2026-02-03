"""
应用配置文件

使用扁平化配置结构，简化配置管理
"""

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DefaultSettings(BaseSettings):
    """
    应用设置 - 扁平化配置

    所有配置使用扁平结构，通过命名空间前缀组织。
    环境变量直接映射，无需额外的 validation_alias。

    环境变量示例：
    - PROJECT_NAME="Faster APP"
    - DEBUG=true
    - SERVER_HOST=0.0.0.0
    - SERVER_PORT=8080
    - JWT_SECRET_KEY="your-secret"
    - DB_URL="sqlite://db.sqlite"
    - CORS_ORIGINS='["https://example.com"]'
    """

    # ==================== 基础配置 ====================
    PROJECT_NAME: str = Field(default="Faster APP", description="项目名称")
    VERSION: str = Field(default="0.0.1", description="版本号")
    DEBUG: bool = Field(default=True, description="调试模式")
    VALIDATE_ROUTES: bool = Field(default=True, description="是否启用路由冲突检测")

    # ==================== 服务器配置 ====================
    SERVER_HOST: str = Field(default="0.0.0.0", description="监听地址")
    SERVER_PORT: int = Field(default=8000, description="监听端口")

    # ==================== JWT 认证配置 ====================
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-here-change-in-production",
        description="JWT 密钥，生产环境必须修改",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT 加密算法")
    JWT_EXPIRE_MINUTES: int = Field(default=30, description="访问令牌过期时间（分钟）")

    # ==================== 数据库配置 ====================
    DB_URL: str = Field(default="sqlite://db.sqlite", description="数据库连接 URL")

    # ==================== 日志配置 ====================
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FORMAT: str = Field(default="STRING", description="日志格式 (STRING/JSON)")
    LOG_TO_FILE: bool = Field(default=False, description="是否输出到文件")
    LOG_FILE_PATH: str = Field(default="logs/app.log", description="日志文件路径")
    LOG_FILE_BACKUP_COUNT: int = Field(default=10, description="日志备份文件数量")

    # ==================== 生命周期配置 ====================
    LIFESPAN_DATABASE: bool = Field(default=False, description="是否启用数据库 lifespan")
    LIFESPAN_APPS: bool = Field(default=False, description="是否启用应用 lifespan")
    LIFESPAN_USER: bool = Field(default=False, description="是否启用用户自定义 lifespan")

    # ==================== 限流配置 ====================
    THROTTLE_USER_RATE: str = Field(default="100/hour", description="用户限流速率")
    THROTTLE_ANON_RATE: str = Field(default="20/hour", description="匿名用户限流速率")
    THROTTLE_DEFAULT_RATE: str = Field(default="100/hour", description="默认限流速率")

    # ==================== CORS 跨域配置 ====================
    CORS_ORIGINS: list[str] = Field(
        default=["*"],
        description="允许的源域名列表，生产环境应明确指定",
    )
    CORS_CREDENTIALS: bool = Field(default=False, description="是否允许携带凭证")
    CORS_METHODS: list[str] = Field(default=["*"], description="允许的 HTTP 方法")
    CORS_HEADERS: list[str] = Field(default=["*"], description="允许的请求头")
    CORS_EXPOSE_HEADERS: list[str] = Field(default=[], description="暴露的响应头")
    CORS_MAX_AGE: int = Field(default=600, description="预检请求缓存时间（秒）")

    # ==================== 可信主机配置 ====================
    TRUSTED_HOST_ENABLED: bool = Field(
        default=False,
        description="是否启用可信主机检查（生产环境建议启用）",
    )
    TRUSTED_HOSTS: list[str] = Field(default=["*"], description="允许的主机名列表")

    # ==================== 性能监控配置 ====================
    TIMING_ENABLED: bool = Field(default=True, description="是否启用性能监控中间件")
    TIMING_SLOW_THRESHOLD: float = Field(default=1.0, description="慢请求阈值（秒）")

    # ==================== 请求日志配置 ====================
    REQUEST_LOGGING_ENABLED: bool = Field(default=True, description="是否启用请求日志中间件")
    REQUEST_LOGGING_LOG_BODY: bool = Field(
        default=False,
        description="是否记录请求体（可能包含敏感信息）",
    )
    REQUEST_LOGGING_LOG_RESPONSE: bool = Field(default=False, description="是否记录响应体")

    # ==================== GZip 压缩配置 ====================
    GZIP_ENABLED: bool = Field(default=True, description="是否启用 GZip 压缩")
    GZIP_MINIMUM_SIZE: int = Field(default=1000, description="最小压缩大小（字节）")

    @model_validator(mode="after")
    def validate_production_settings(self):
        """生产环境配置验证"""
        if not self.DEBUG:
            # 生产环境检查
            if self.JWT_SECRET_KEY == "your-secret-key-here-change-in-production":
                raise ValueError("生产环境必须修改 JWT_SECRET_KEY")

            # CORS 安全检查
            if self.CORS_CREDENTIALS and "*" in self.CORS_ORIGINS:
                raise ValueError(
                    "生产环境 CORS 配置不安全: "
                    "CORS_CREDENTIALS=True 不能与 CORS_ORIGINS=['*'] 同时使用"
                )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
