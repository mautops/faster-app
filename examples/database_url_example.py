"""
DATABASE_URL 使用示例
"""

import os

# ============================================================
# 示例 1: PostgreSQL 生产环境
# ============================================================
print("示例 1: PostgreSQL 生产环境")
print("=" * 60)

os.environ["DATABASE_URL"] = "postgresql://appuser:secret@prod.db.com:5432/myapp"

from faster_app.settings.builtins.settings import Settings

settings = Settings()
print(f"数据库类型: {settings.database.type}")
print(f"主机: {settings.database.host}")
print(f"端口: {settings.database.port}")
print(f"用户: {settings.database.user}")
print(f"数据库: {settings.database.database}")
print()

# 清理
del os.environ["DATABASE_URL"]

# ============================================================
# 示例 2: SQLite 开发环境
# ============================================================
print("示例 2: SQLite 开发环境")
print("=" * 60)

os.environ["FASTER_DATABASE_URL"] = "sqlite:///dev.db"

settings = Settings()
print(f"数据库类型: {settings.database.type}")
print(f"数据库文件: {settings.database.database}")
print()

# 清理
del os.environ["FASTER_DATABASE_URL"]

# ============================================================
# 示例 3: MySQL 数据库
# ============================================================
print("示例 3: MySQL 数据库")
print("=" * 60)

os.environ["DATABASE_URL"] = "mysql://root:password@localhost:3306/myapp"

settings = Settings()
print(f"数据库类型: {settings.database.type}")
print(f"主机: {settings.database.host}")
print(f"端口: {settings.database.port}")
print()

# 清理
del os.environ["DATABASE_URL"]

# ============================================================
# 示例 4: 多租户 - Schema 支持
# ============================================================
print("示例 4: 多租户（Schema 支持）")
print("=" * 60)

# 租户 A
os.environ["DATABASE_URL"] = "postgresql://app:pass@db.example.com:5432/saas?schema=tenant_a"
settings = Settings()
print(f"租户 A - Schema: {settings.database.db_schema}")

# 清理
del os.environ["DATABASE_URL"]

# 租户 B
os.environ["DATABASE_URL"] = "postgresql://app:pass@db.example.com:5432/saas?schema=tenant_b"
settings = Settings()
print(f"租户 B - Schema: {settings.database.db_schema}")
print()

# 清理
del os.environ["DATABASE_URL"]

# ============================================================
# 示例 5: 配置优先级
# ============================================================
print("示例 5: 配置优先级")
print("=" * 60)

# 同时设置两个 URL
os.environ["DATABASE_URL"] = "postgresql://user1@host1:5432/db1"
os.environ["FASTER_DATABASE_URL"] = "postgresql://user2@host2:5432/db2"

settings = Settings()
print(f"实际使用的主机: {settings.database.host}")
print(f"说明: FASTER_DATABASE_URL 优先于 DATABASE_URL")
print()

# 清理
del os.environ["DATABASE_URL"]
del os.environ["FASTER_DATABASE_URL"]

# ============================================================
# 示例 6: .env 文件使用
# ============================================================
print("示例 6: .env 文件配置")
print("=" * 60)
print("# .env 文件内容：")
print("DATABASE_URL=postgresql://app:pass@db.example.com:5432/appdb")
print()
print("# 或者使用带前缀的版本（推荐）：")
print("FASTER_DATABASE_URL=postgresql://app:pass@db.example.com:5432/appdb")
print()

print("=" * 60)
print("✅ DATABASE_URL 让数据库配置变得简单！")
print("=" * 60)

