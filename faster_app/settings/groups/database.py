"""
数据库配置组 - 基于 DATABASE_URL
"""

from typing import Optional
from urllib.parse import urlparse, unquote, parse_qs
from pydantic import BaseModel, SecretStr, field_validator


class DatabaseSettings(BaseModel):
    """
    数据库配置 - 仅支持 DATABASE_URL

    使用示例:
        # PostgreSQL
        DATABASE_URL=postgresql://user:pass@host:5432/database?schema=myschema

        # MySQL
        DATABASE_URL=mysql://user:pass@host:3306/database

        # SQLite
        DATABASE_URL=sqlite:///path/to/database.db
    """

    type: str
    engine: str
    host: str
    port: int
    user: str
    password: SecretStr
    database: str
    db_schema: Optional[str] = None

    @field_validator("port")
    @classmethod
    def validate_port(cls, v, info):
        """验证数据库端口号范围"""
        # SQLite 不需要端口，允许为 0
        db_type = info.data.get("type", "")
        if db_type == "sqlite":
            return v

        if not 1 <= v <= 65535:
            raise ValueError(f"database.port 必须在 1-65535 之间，当前值: {v}")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """验证数据库类型"""
        allowed_types = ["sqlite", "postgres", "mysql"]
        v_lower = v.lower()
        if v_lower not in allowed_types:
            raise ValueError(f"database.type 必须是 {allowed_types} 之一，当前值: {v}")
        return v_lower

    @classmethod
    def from_database_url(cls, url: str) -> "DatabaseSettings":
        """
        从 DATABASE_URL 创建配置

        支持格式:
        - postgresql://user:pass@host:port/database
        - postgresql://user:pass@host:port/database?schema=myschema
        - mysql://user:pass@host:port/database
        - sqlite:///path/to/database.db

        Args:
            url: 数据库连接 URL

        Returns:
            DatabaseSettings 实例

        Raises:
            ValueError: URL 格式错误
        """
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValueError(f"DATABASE_URL 格式错误: {e}")

        # 验证 scheme
        if not parsed.scheme:
            raise ValueError("DATABASE_URL 缺少数据库类型（scheme）")

        # 映射数据库类型
        db_type_map = {
            "postgresql": "postgres",
            "postgres": "postgres",
            "mysql": "mysql",
            "sqlite": "sqlite",
        }

        db_type = db_type_map.get(parsed.scheme.lower())
        if not db_type:
            raise ValueError(
                f"不支持的数据库类型: {parsed.scheme}，支持: {list(db_type_map.keys())}"
            )

        # 解析查询参数
        query_params = parse_qs(parsed.query) if parsed.query else {}
        schema = query_params.get("schema", [None])[0]

        # SQLite 特殊处理
        if db_type == "sqlite":
            db_path = parsed.path or "faster_app.db"
            return cls(
                type="sqlite",
                engine="tortoise.backends.sqlite",
                host="",
                port=0,
                user="",
                password=SecretStr(""),
                database=db_path,
                db_schema=None,
            )

        # PostgreSQL/MySQL
        if not parsed.hostname:
            raise ValueError("DATABASE_URL 缺少主机名（host）")

        # 默认端口
        default_ports = {"postgres": 5432, "mysql": 3306}
        port = parsed.port or default_ports.get(db_type, 5432)

        # 数据库名称
        database = parsed.path.lstrip("/") if parsed.path else "app"
        if not database:
            raise ValueError("DATABASE_URL 缺少数据库名称")

        return cls(
            type=db_type,
            engine="tortoise.backends.asyncpg"
            if db_type == "postgres"
            else "tortoise.backends.mysql",
            host=parsed.hostname,
            port=port,
            user=unquote(parsed.username) if parsed.username else "postgres",
            password=SecretStr(unquote(parsed.password) if parsed.password else ""),
            database=database,
            db_schema=schema,
        )
