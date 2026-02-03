"""
Tortoise ORM 配置生成器

提供延迟加载的 ORM 配置，避免在导入时执行
"""

from urllib.parse import parse_qs, urlparse, urlunparse

from tortoise.backends.base.config_generator import expand_db_url

from faster_app.models.discover import ModelDiscover
from faster_app.settings import logger
from faster_app.settings.config import configs


def get_tortoise_config() -> dict:
    """
    生成 Tortoise ORM 配置

    延迟加载：只在需要时调用此函数，避免在导入时执行

    Returns:
        Tortoise ORM 配置字典
    """
    # 发现所有模型并按 app 分组
    models_discover = ModelDiscover().discover()

    # 收集所有发现的模型路径
    all_model_paths = []
    for _app_name, model_paths in models_discover.items():
        all_model_paths.extend(model_paths)

    # 构建 Tortoise ORM 配置
    # 将所有模型放在 "models" app 下，这样 aerich 可以统一追踪所有模型
    apps_config = {
        "models": {
            "models": ["aerich.models"] + all_model_paths,
            "default_connection": "default",
        },
    }

    # 获取数据库 URL
    db_url = configs.DB_URL

    try:
        # 处理 DB scheme: 将 'postgresql' 转换为 Tortoise ORM 支持的 'postgres'
        url_parts = urlparse(db_url)
        original_scheme = url_parts.scheme
        if url_parts.scheme == "postgresql":
            # 统一转换为 'postgres'（Tortoise ORM 标准方案）
            new_scheme = "postgres"
            new_url_parts = url_parts._replace(scheme=new_scheme)
            db_url = urlunparse(new_url_parts)
            logger.info(f"将 DB scheme 从 '{original_scheme}' 转换为 '{new_scheme}'")

        # 1. 首先使用 expand_db_url 解析基本 URL
        connection_config = expand_db_url(db_url)

        # 2. 手动解析 URL 查询参数，处理 schema 和连接池配置
        url = urlparse(db_url)
        query_params = parse_qs(url.query)

        credentials = connection_config.get("credentials", {})
        engine = connection_config.get("engine")

        # 3. 处理 schema 配置
        if "schema" in query_params:
            credentials["schema"] = query_params["schema"][-1]

        # 4. 处理连接池配置，同时支持 minsize/maxsize 和 min_size/max_size 两种格式
        if "minsize" in query_params:
            credentials["minsize"] = int(query_params["minsize"][-1])
        elif "min_size" in query_params:
            credentials["minsize"] = int(query_params["min_size"][-1])

        if "maxsize" in query_params:
            credentials["maxsize"] = int(query_params["maxsize"][-1])
        elif "max_size" in query_params:
            credentials["maxsize"] = int(query_params["max_size"][-1])

        # 5. 处理 application_name 配置
        if "application_name" in query_params:
            credentials["application_name"] = query_params["application_name"][-1]

        # 6. 处理 SSL 配置并移除 asyncpg 不支持的参数
        unsupported_params = [
            "sslmode",
            "channel_binding",
            "sslcert",
            "sslkey",
            "sslrootcert",
            "sslcrl",
            "target_session_attrs",
            "options",
            "keepalives",
            "keepalives_idle",
            "keepalives_interval",
            "keepalives_count",
            "tcp_user_timeout",
            "replication",
            "gssencmode",
            "krbsrvname",
            "gsslib",
            "service",
            "passfile",
        ]

        # 提取 sslmode 用于转换
        sslmode = credentials.pop("sslmode", None)
        if sslmode is None and "sslmode" in query_params:
            sslmode = query_params["sslmode"][-1]

        # 移除所有不支持的参数
        for param in unsupported_params:
            credentials.pop(param, None)

        # 将 sslmode 转换为 asyncpg 支持的 ssl 参数
        if sslmode:
            if sslmode == "disable":
                credentials["ssl"] = False
            elif sslmode in ("require", "prefer", "allow"):
                credentials["ssl"] = True
            elif sslmode in ("verify-ca", "verify-full"):
                # 对于严格的 SSL 验证，使用默认 SSL 上下文
                import ssl

                credentials["ssl"] = ssl.create_default_context()

        # 获取 schema 参数用于日志记录
        schema = credentials.get("schema")

        logger.info(
            f"使用 credentials 配置方式初始化数据库连接，"
            f"引擎: {engine}, "
            f"schema: {schema if schema else '未设置（使用默认）'}"
        )

        tortoise_config = {
            "connections": {"default": connection_config},
            "apps": apps_config,
        }

    except Exception as e:
        # 如果解析失败，回退到 URL 字符串方式（保持兼容性）
        logger.warning(
            f"解析 DB_URL 失败: {e}，回退到 URL 字符串配置方式。"
            f"如果使用了 schema 等特殊参数，可能无法正常工作。"
        )
        tortoise_config = {
            "connections": {"default": {"db_url": db_url}},
            "apps": apps_config,
        }

    logger.debug(f"Tortoise ORM config: {tortoise_config}")
    return tortoise_config


# 为了保持兼容性，提供一个全局变量（但推荐使用函数）
TORTOISE_ORM = get_tortoise_config()
