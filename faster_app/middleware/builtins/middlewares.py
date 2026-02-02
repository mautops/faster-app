"""
中间件配置

⚠️ 注意：默认只启用 FastAPI 内置的核心中间件，不包含自定义中间件以避免性能开销。
如需添加自定义中间件（如日志、性能监控），请参考 custom.py 中的使用示例。

支持特性：
1. 环境感知：根据 DEBUG 配置自动选择开发/生产环境配置
2. 优先级排序：通过 priority 字段控制中间件执行顺序（数字越小越先执行）
3. 动态启用/禁用：通过 enabled 字段控制中间件是否加载
4. 配置来自 Settings：所有敏感配置从配置文件读取

优先级说明（参见 MiddlewarePriority 枚举）：
- 1-10: 日志和监控（最外层，捕获一切）
- 11-20: 安全相关（CORS, TrustedHost, SecurityHeaders）
- 21-30: 压缩和优化
- 31+: 其他业务中间件

中间件执行顺序：
请求流：priority 1 -> 2 -> 3 -> ... -> 路由处理器
响应流：路由处理器 -> ... -> 3 -> 2 -> 1
"""

from faster_app.middleware.discover import PRIORITY_CORS, PRIORITY_GZIP, PRIORITY_TRUSTED_HOST
from faster_app.settings import configs

# 中间件配置列表
MIDDLEWARES = [
    {
        "class": "fastapi.middleware.cors.CORSMiddleware",
        "priority": PRIORITY_CORS,
        "enabled": True,
        "kwargs": {
            "allow_origins": configs.MIDDLEWARE.CORS.ALLOW_ORIGINS,
            "allow_credentials": configs.MIDDLEWARE.CORS.ALLOW_CREDENTIALS,
            "allow_methods": configs.MIDDLEWARE.CORS.ALLOW_METHODS,
            "allow_headers": configs.MIDDLEWARE.CORS.ALLOW_HEADERS,
            "expose_headers": configs.MIDDLEWARE.CORS.EXPOSE_HEADERS,
            "max_age": configs.MIDDLEWARE.CORS.MAX_AGE,
        },
    },
    {
        "class": "fastapi.middleware.trustedhost.TrustedHostMiddleware",
        "priority": PRIORITY_TRUSTED_HOST,
        "enabled": configs.MIDDLEWARE.TRUSTED_HOST.ENABLED,
        "kwargs": {"allowed_hosts": configs.MIDDLEWARE.TRUSTED_HOST.HOSTS},
    },
    {
        "class": "fastapi.middleware.gzip.GZipMiddleware",
        "priority": PRIORITY_GZIP,
        "enabled": configs.MIDDLEWARE.GZIP.ENABLED,
        "kwargs": {"minimum_size": configs.MIDDLEWARE.GZIP.MINIMUM_SIZE},
    },
]


# 启动时日志提示


def _log_middleware_info():
    """记录中间件配置信息"""
    from faster_app.settings import logger

    if configs.DEBUG:
        logger.info("🔧 [开发模式] 中间件使用宽松的安全配置")
    else:
        # 生产环境提示
        cors_cfg = configs.MIDDLEWARE.CORS
        if "*" in cors_cfg.ALLOW_ORIGINS:
            logger.warning("⚠️  [安全提示] 生产环境 CORS 允许所有域名访问，建议指定明确的域名列表")

        trusted_cfg = configs.MIDDLEWARE.TRUSTED_HOST
        if not trusted_cfg.ENABLED:
            logger.warning(
                "⚠️  [安全提示] 生产环境建议启用 TrustedHostMiddleware "
                "（设置 TRUSTED_HOST_ENABLED=true）"
            )
        elif "*" in trusted_cfg.HOSTS:
            logger.warning("⚠️  [安全提示] TrustedHost 允许所有主机名，建议指定明确的主机名列表")


# 记录配置信息
_log_middleware_info()
