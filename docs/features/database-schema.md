# 数据库 Schema 支持

## 概述

为了支持多租户架构和数据隔离，Faster APP 支持通过 **数据库 schema** 来区分和隔离数据。特别适用于 PostgreSQL 的 schema 特性。

## 什么是 Database Schema？

**Schema** 是数据库中的逻辑命名空间，用于组织和隔离数据库对象（表、视图、函数等）。

### 各数据库的支持情况

| 数据库 | Schema 支持 | 说明 |
|--------|------------|------|
| **PostgreSQL** | ✅ 完全支持 | Schema 是一等公民，默认为 `public` |
| **MySQL** | ⚠️ 有限支持 | MySQL 中 schema = database |
| **SQLite** | ❌ 不支持 | SQLite 没有 schema 概念 |

## 为什么需要 Schema？

### ✅ 优势

1. **多租户隔离** - 每个租户一个 schema，数据隔离但共享数据库
2. **环境隔离** - 在同一数据库中隔离 dev/test/staging 数据
3. **权限管理** - 精细化的 schema 级别权限控制
4. **逻辑分组** - 按业务模块组织表结构
5. **降低成本** - 避免为每个租户创建独立数据库

### 典型场景

#### 1. 多租户 SaaS 应用

```
Database: saas_app
├── Schema: tenant_a (租户 A 的数据)
│   ├── users
│   ├── orders
│   └── products
├── Schema: tenant_b (租户 B 的数据)
│   ├── users
│   ├── orders
│   └── products
└── Schema: public (公共数据)
    ├── system_config
    └── global_settings
```

#### 2. 微服务数据隔离

```
Database: microservices
├── Schema: user_service
├── Schema: order_service
├── Schema: payment_service
└── Schema: inventory_service
```

#### 3. 环境数据隔离

```
Database: myapp
├── Schema: dev
├── Schema: test
├── Schema: staging
└── Schema: public (生产)
```

## 使用方式

### 方式 1: DATABASE_URL 查询参数（推荐）

```bash
# PostgreSQL with schema
export FASTER_DATABASE_URL="postgresql://user:pass@host:5432/mydb?schema=tenant1"

# 不指定 schema（使用数据库默认，PostgreSQL 默认是 public）
export FASTER_DATABASE_URL="postgresql://user:pass@host:5432/mydb"
```

### 方式 2: 独立环境变量

```bash
export FASTER_DATABASE__TYPE=postgres
export FASTER_DATABASE__HOST=localhost
export FASTER_DATABASE__PORT=5432
export FASTER_DATABASE__DATABASE=mydb
export FASTER_DATABASE__DB_SCHEMA=tenant1
```

### 方式 3: Python 代码

```python
from faster_app.settings.builtins.settings import Settings
from faster_app.settings.groups import DatabaseSettings

# 直接创建配置
db = DatabaseSettings(
    type="postgres",
    host="localhost",
    database="saas_app",
    db_schema="tenant_a"
)

# 从 URL 创建
db = DatabaseSettings.from_database_url(
    "postgresql://user:pass@localhost:5432/saas_app?schema=tenant_a"
)
```

## 完整示例

### 多租户 SaaS 应用

```python
"""多租户示例"""
from faster_app.settings.groups import DatabaseSettings

# 租户 A
tenant_a_db = DatabaseSettings.from_database_url(
    "postgresql://app:secret@prod.db:5432/saas?schema=tenant_a"
)

# 租户 B
tenant_b_db = DatabaseSettings.from_database_url(
    "postgresql://app:secret@prod.db:5432/saas?schema=tenant_b"
)

# 两个租户使用同一个数据库，但数据完全隔离
assert tenant_a_db.database == tenant_b_db.database == "saas"
assert tenant_a_db.db_schema != tenant_b_db.db_schema
```

### 动态租户切换

```python
"""运行时动态切换租户 schema"""
import os
from faster_app.settings.builtins.settings import Settings

def get_settings_for_tenant(tenant_id: str) -> Settings:
    """为指定租户获取配置"""
    base_url = "postgresql://app:secret@db.example.com:5432/saas"
    os.environ["FASTER_DATABASE_URL"] = f"{base_url}?schema=tenant_{tenant_id}"
    return Settings()

# 租户 A 的配置
settings_a = get_settings_for_tenant("a")
print(settings_a.database.db_schema)  # tenant_a

# 租户 B 的配置
settings_b = get_settings_for_tenant("b")
print(settings_b.database.db_schema)  # tenant_b
```

### 环境隔离

```bash
# 开发环境
export FASTER_DATABASE_URL="postgresql://dev:dev@localhost:5432/myapp?schema=dev"

# 测试环境
export FASTER_DATABASE_URL="postgresql://test:test@localhost:5432/myapp?schema=test"

# 生产环境（使用默认 public schema）
export FASTER_DATABASE_URL="postgresql://prod:secret@prod.db:5432/myapp"
```

### Docker Compose 多租户

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 租户 A 服务
  app_tenant_a:
    image: faster-app
    environment:
      - FASTER_DATABASE_URL=postgresql://app:pass@db:5432/saas?schema=tenant_a
    ports:
      - "8001:8000"
  
  # 租户 B 服务
  app_tenant_b:
    image: faster-app
    environment:
      - FASTER_DATABASE_URL=postgresql://app:pass@db:5432/saas?schema=tenant_b
    ports:
      - "8002:8000"
  
  # 共享数据库
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=saas
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=pass
    volumes:
      - ./init-schemas.sql:/docker-entrypoint-initdb.d/init.sql
```

```sql
-- init-schemas.sql
-- 创建租户 schema
CREATE SCHEMA IF NOT EXISTS tenant_a;
CREATE SCHEMA IF NOT EXISTS tenant_b;

-- 授权
GRANT ALL ON SCHEMA tenant_a TO app;
GRANT ALL ON SCHEMA tenant_b TO app;
```

## TORTOISE_ORM 集成

Schema 配置会自动集成到 Tortoise ORM 配置中：

```python
from faster_app.settings.builtins.settings import Settings

settings = Settings()

# 有 schema 时
# TORTOISE_ORM['connections']['POSTGRES']['credentials']
# {
#     'host': 'localhost',
#     'port': 5432,
#     'user': 'user',
#     'password': '***',
#     'database': 'mydb',
#     'schema': 'tenant_a'  ← 自动添加
# }

# 无 schema 时（默认）
# {
#     'host': 'localhost',
#     'port': 5432,
#     'user': 'user',
#     'password': '***',
#     'database': 'mydb'
#     # 没有 schema 字段，使用数据库默认
# }
```

## PostgreSQL Schema 最佳实践

### 1. 创建 Schema

```sql
-- 创建 schema
CREATE SCHEMA tenant_a;

-- 创建 schema 并指定所有者
CREATE SCHEMA tenant_a AUTHORIZATION app_user;

-- 设置默认 search_path
ALTER ROLE app_user SET search_path TO tenant_a, public;
```

### 2. Schema 权限管理

```sql
-- 授予所有权限
GRANT ALL ON SCHEMA tenant_a TO tenant_a_user;

-- 授予特定权限
GRANT USAGE ON SCHEMA tenant_a TO read_only_user;
GRANT SELECT ON ALL TABLES IN SCHEMA tenant_a TO read_only_user;

-- 撤销权限
REVOKE ALL ON SCHEMA tenant_a FROM public;
```

### 3. 查询指定 Schema 的表

```sql
-- 查询 tenant_a schema 中的用户表
SELECT * FROM tenant_a.users;

-- 设置 search_path 后可省略 schema 前缀
SET search_path TO tenant_a;
SELECT * FROM users;  -- 自动在 tenant_a 中查找
```

## 配置优先级

Schema 配置遵循以下优先级：

1. **DATABASE_URL 查询参数** - `?schema=xxx`
2. **FASTER_DATABASE__DB_SCHEMA** 环境变量
3. **默认值** - `None`（使用数据库默认 schema）

```bash
# 示例：URL 参数优先
export FASTER_DATABASE_URL="postgresql://user:pass@host:5432/db?schema=from_url"
export FASTER_DATABASE__DB_SCHEMA="from_env"

# 实际使用: from_url（URL 参数优先）
```

## 注意事项

### ✅ 推荐做法

1. **明确指定 Schema**
   ```python
   # 推荐：明确指定
   url = "postgresql://user:pass@host:5432/db?schema=tenant_a"
   ```

2. **Schema 命名规范**
   ```
   ✅ 推荐: tenant_a, user_service, dev_env
   ❌ 避免: Tenant-A, user.service, dev env
   ```

3. **权限最小化**
   ```sql
   -- 每个租户只能访问自己的 schema
   GRANT USAGE ON SCHEMA tenant_a TO tenant_a_user;
   REVOKE ALL ON SCHEMA tenant_b FROM tenant_a_user;
   ```

4. **备份时包含 Schema**
   ```bash
   # 备份特定 schema
   pg_dump -h localhost -U user -n tenant_a mydb > tenant_a_backup.sql
   
   # 恢复
   psql -h localhost -U user mydb < tenant_a_backup.sql
   ```

### ⚠️ 注意事项

1. **Schema 必须存在**
   - 应用启动前确保 schema 已创建
   - 使用迁移工具自动创建

2. **跨 Schema 查询性能**
   - 避免频繁的跨 schema JOIN
   - 考虑数据复制或物化视图

3. **连接池配置**
   - 每个 schema 可能需要独立的连接池
   - 注意连接数限制

4. **SQLite 忽略 Schema**
   ```python
   # SQLite 会忽略 schema 参数
   db = DatabaseSettings.from_database_url(
       "sqlite:///mydb.db?schema=ignored"
   )
   assert db.db_schema is None  # SQLite 不支持
   ```

## 迁移指南

### 从单 Schema 迁移到多 Schema

**步骤 1: 创建新 Schema**
```sql
CREATE SCHEMA tenant_new;
```

**步骤 2: 复制表结构**
```sql
-- 方法 1: 手动复制
CREATE TABLE tenant_new.users (LIKE public.users INCLUDING ALL);

-- 方法 2: 使用 pg_dump
pg_dump -s -n public mydb | sed 's/public\./tenant_new./g' | psql mydb
```

**步骤 3: 迁移数据**
```sql
INSERT INTO tenant_new.users SELECT * FROM public.users WHERE tenant_id = 'new';
```

**步骤 4: 更新配置**
```bash
# 更新环境变量
export FASTER_DATABASE_URL="postgresql://user:pass@host:5432/mydb?schema=tenant_new"
```

## 故障排查

### 问题 1: Schema 不存在

```
ERROR: schema "tenant_a" does not exist
```

**解决方案:**
```sql
CREATE SCHEMA IF NOT EXISTS tenant_a;
```

### 问题 2: 权限不足

```
ERROR: permission denied for schema tenant_a
```

**解决方案:**
```sql
GRANT USAGE ON SCHEMA tenant_a TO your_user;
GRANT ALL ON ALL TABLES IN SCHEMA tenant_a TO your_user;
```

### 问题 3: 找不到表

```
ERROR: relation "users" does not exist
```

**解决方案:**
```sql
-- 检查 search_path
SHOW search_path;

-- 设置正确的 search_path
SET search_path TO tenant_a, public;

-- 或使用全限定名
SELECT * FROM tenant_a.users;
```

## 相关文档

- [DATABASE_URL 支持](./database-url.md) - 数据库 URL 配置
- [配置分组](./config-grouping.md) - 配置结构说明
- [生产环境验证](./production-validation.md) - 生产配置检查

## 技术细节

### 实现原理

```python
# 1. URL 解析
from urllib.parse import urlparse, parse_qs

url = "postgresql://user:pass@host:5432/db?schema=tenant_a"
parsed = urlparse(url)
query_params = parse_qs(parsed.query)
schema = query_params.get("schema", [None])[0]  # "tenant_a"

# 2. 字段定义
class DatabaseSettings(BaseModel):
    db_schema: Optional[str] = None  # 使用 db_schema 避免与 BaseModel.schema 冲突

# 3. Tortoise ORM 集成
credentials = {
    "host": self.database.host,
    "database": self.database.database,
}
if self.database.db_schema:
    credentials["schema"] = self.database.db_schema
```

### 字段命名说明

配置字段使用 `db_schema` 而不是 `schema`，原因：
- Pydantic `BaseModel` 有内置的 `schema()` 方法
- 使用 `db_schema` 避免命名冲突
- 在 URL 和环境变量中仍使用 `schema` 更直观

```python
# ✅ 配置字段: db_schema
settings.database.db_schema  

# ✅ URL 参数: schema
"?schema=tenant_a"

# ✅ 环境变量: DB_SCHEMA
FASTER_DATABASE__DB_SCHEMA=tenant_a

# ✅ Tortoise ORM: schema
credentials["schema"] = db_schema
```

## 总结

Database Schema 支持是一个**简单、强大、实用**的功能：

1. ✅ **多租户友好** - 数据隔离的最佳实践
2. ✅ **环境隔离** - 开发/测试/生产数据分离
3. ✅ **灵活配置** - URL 参数或环境变量
4. ✅ **自动集成** - 无缝集成到 Tortoise ORM
5. ✅ **PostgreSQL 优化** - 充分利用 PostgreSQL schema 特性

**推荐在多租户 SaaS 应用中使用 Schema 实现数据隔离！** 🚀

