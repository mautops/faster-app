# DATABASE_URL 支持

## 概述

为了简化数据库配置并遵循 [12-Factor App](https://12factor.net/config) 最佳实践，Faster APP 支持通过单个 `DATABASE_URL` 环境变量配置数据库连接。

## 为什么需要 DATABASE_URL？

### ✅ 优势

1. **部署简化** - 一个变量替代多个独立配置
2. **云原生友好** - 主流云平台（Heroku、Railway、Render）标准支持
3. **统一标准** - 业界广泛认可的配置方式
4. **降低出错** - 减少配置项，降低配置错误概率
5. **安全性** - 密码等敏感信息集中在一个变量中

### 适用场景

- ✅ 云平台部署（Heroku、Railway、Render、Fly.io）
- ✅ 容器化部署（Docker、Kubernetes）
- ✅ CI/CD 环境配置
- ✅ 多环境切换（开发、测试、生产）

## 使用方式

### 方式 1: DATABASE_URL（标准）

```bash
export DATABASE_URL=postgresql://user:password@host:5432/database
```

### 方式 2: FASTER_DATABASE_URL（推荐）

使用带前缀的版本，避免环境变量冲突：

```bash
export FASTER_DATABASE_URL=postgresql://user:password@host:5432/database
```

### 方式 3: 独立变量（向后兼容）

如果更喜欢传统方式，仍可使用独立环境变量：

```bash
export FASTER_DATABASE__TYPE=postgres
export FASTER_DATABASE__HOST=localhost
export FASTER_DATABASE__PORT=5432
export FASTER_DATABASE__USER=user
export FASTER_DATABASE__PASSWORD=password
export FASTER_DATABASE__DATABASE=mydb
```

## 支持的数据库

### PostgreSQL

```bash
# 标准格式
postgresql://user:password@host:5432/database

# 别名支持
postgres://user:password@host:5432/database

# 默认端口（可省略）
postgresql://user:password@host/database  # 端口 5432

# 带 schema（多租户/数据隔离）
postgresql://user:password@host:5432/database?schema=tenant_a
```

> 💡 **提示**: 关于 Schema 的详细使用，请参考 [数据库 Schema 支持](./database-schema.md)

### MySQL

```bash
# 标准格式
mysql://user:password@host:3306/database

# 默认端口（可省略）
mysql://user:password@host/database  # 端口 3306
```

### SQLite

```bash
# 绝对路径
sqlite:////absolute/path/to/database.db

# 相对路径
sqlite:///relative/path/database.db

# 当前目录
sqlite:///database.db
```

## 配置优先级

当多种配置方式同时存在时，按以下优先级：

1. **构造函数参数** - `Settings(database=...)`
2. **FASTER_DATABASE_URL** - 带前缀的 URL
3. **DATABASE_URL** - 标准 URL
4. **FASTER_DATABASE__*** - 独立环境变量
5. **默认值** - 代码中的默认配置

```python
# 优先级示例
os.environ["DATABASE_URL"] = "postgresql://user1:pass@host1:5432/db1"
os.environ["FASTER_DATABASE_URL"] = "postgresql://user2:pass@host2:5432/db2"

settings = Settings()
# 实际使用: host2（FASTER_DATABASE_URL 优先）
```

## 特殊字符处理

如果密码包含特殊字符，需要进行 URL 编码：

### Python 示例

```python
from urllib.parse import quote

password = "p@ss!w#rd$123"
encoded = quote(password, safe="")
# 结果: p%40ss%21w%23rd%24123

url = f"postgresql://user:{encoded}@host:5432/db"
```

### 常见特殊字符编码

| 字符 | 编码 | 字符 | 编码 |
|------|------|------|------|
| `@`  | `%40` | `#`  | `%23` |
| `:`  | `%3A` | `?`  | `%3F` |
| `/`  | `%2F` | `&`  | `%26` |
| `%`  | `%25` | `$`  | `%24` |

### 在线工具

- [URL Encoder/Decoder](https://www.urlencoder.org/)
- Python: `urllib.parse.quote()`
- Node.js: `encodeURIComponent()`

## 实际案例

### 开发环境

```bash
# .env.development
FASTER_DATABASE_URL=sqlite:///dev.db
```

### 测试环境

```bash
# .env.test
FASTER_DATABASE_URL=postgresql://test:test@localhost:5432/test_db
```

### 生产环境（云平台）

```bash
# 云平台自动提供
DATABASE_URL=postgresql://user:pass@prod-db.cloud.com:5432/prod_db
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    image: faster-app
    environment:
      - FASTER_DATABASE_URL=postgresql://app:password@db:5432/appdb
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=appdb
```

### Kubernetes

```yaml
# deployment.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  FASTER_DATABASE_URL: postgresql://user:pass@postgres:5432/db

---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: app
        envFrom:
        - configMapRef:
            name: app-config
```

## 错误处理

### 常见错误

#### 1. 格式错误

```bash
# ❌ 错误：缺少协议
DATABASE_URL=localhost:5432/db

# ✅ 正确
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

#### 2. 不支持的数据库

```bash
# ❌ 错误：不支持 MongoDB
DATABASE_URL=mongodb://localhost:27017/db
# 错误: 不支持的数据库类型: mongodb，支持: ['postgresql', 'postgres', 'mysql', 'sqlite']

# ✅ 正确：使用支持的数据库
DATABASE_URL=postgresql://localhost:5432/db
```

#### 3. 缺少必要信息

```bash
# ❌ 错误：PostgreSQL 缺少主机名
DATABASE_URL=postgresql:///db
# 错误: DATABASE_URL 缺少主机名（host）

# ✅ 正确
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

### 解析失败处理

如果 `DATABASE_URL` 解析失败，系统会：
1. 发出警告（Warning）
2. 回退到独立环境变量或默认配置
3. 不会中断应用启动

```python
# 解析失败时的警告
UserWarning: DATABASE_URL 解析失败: <错误详情>，使用默认配置
```

## 最佳实践

### ✅ 推荐做法

1. **生产环境使用 DATABASE_URL**
   - 简化配置，减少出错
   - 符合云平台标准

2. **开发环境使用 SQLite**
   ```bash
   FASTER_DATABASE_URL=sqlite:///dev.db
   ```

3. **密码包含特殊字符要编码**
   ```python
   from urllib.parse import quote
   password = quote("p@ss!word", safe="")
   ```

4. **优先使用 FASTER_DATABASE_URL**
   - 避免与其他应用冲突

5. **敏感信息使用密钥管理**
   - 生产环境从密钥管理服务读取
   - 不要在代码中硬编码

### ❌ 避免的做法

1. **不要在代码中硬编码 URL**
   ```python
   # ❌ 错误
   settings = Settings(database_url="postgresql://...")
   
   # ✅ 正确：使用环境变量
   # export FASTER_DATABASE_URL=postgresql://...
   ```

2. **不要混用配置方式**
   ```bash
   # ❌ 混乱：同时设置 URL 和独立变量
   export FASTER_DATABASE_URL=postgresql://...
   export FASTER_DATABASE__HOST=different-host
   
   # ✅ 清晰：只用一种方式
   export FASTER_DATABASE_URL=postgresql://...
   ```

3. **不要忽略密码编码**
   ```bash
   # ❌ 特殊字符未编码可能导致解析错误
   DATABASE_URL=postgresql://user:p@ss:word@host:5432/db
   
   # ✅ 正确编码
   DATABASE_URL=postgresql://user:p%40ss%3Aword@host:5432/db
   ```

## 迁移指南

### 从独立变量迁移到 DATABASE_URL

**之前：**
```bash
export FASTER_DATABASE__TYPE=postgres
export FASTER_DATABASE__HOST=prod.db.com
export FASTER_DATABASE__PORT=5432
export FASTER_DATABASE__USER=appuser
export FASTER_DATABASE__PASSWORD=secret123
export FASTER_DATABASE__DATABASE=appdb
```

**之后：**
```bash
export FASTER_DATABASE_URL=postgresql://appuser:secret123@prod.db.com:5432/appdb
```

**好处：**
- 6 个变量 → 1 个变量
- 更清晰，更易管理
- 与云平台标准一致

## 兼容性说明

- ✅ **完全向后兼容** - 独立环境变量仍然有效
- ✅ **渐进式迁移** - 可以逐步从旧方式迁移到新方式
- ✅ **零破坏性** - 现有代码无需修改

## 相关文档

- [配置分组](./config-grouping.md) - 了解配置结构
- [环境变量前缀](./env-prefix.md) - 环境变量命名规范
- [生产环境验证](./production-validation.md) - 生产配置安全检查
- [敏感信息保护](./settings-security.md) - 密码等敏感数据处理

## 技术细节

### 实现原理

```python
from urllib.parse import urlparse, unquote

def from_database_url(cls, url: str) -> "DatabaseSettings":
    """从 DATABASE_URL 创建配置"""
    parsed = urlparse(url)
    
    # 解析数据库类型
    db_type = parsed.scheme  # postgresql, mysql, sqlite
    
    # 解析连接信息
    host = parsed.hostname
    port = parsed.port or 5432  # 默认端口
    user = unquote(parsed.username)  # URL 解码
    password = unquote(parsed.password)  # URL 解码
    database = parsed.path.lstrip("/")
    
    return cls(type=db_type, host=host, ...)
```

### 测试覆盖

- ✅ PostgreSQL/MySQL/SQLite 解析
- ✅ 默认端口处理
- ✅ 特殊字符密码
- ✅ 环境变量优先级
- ✅ 向后兼容性
- ✅ 错误处理

## 总结

DATABASE_URL 支持是一个**简单、实用、非侵入性**的功能增强：

1. ✅ **简化配置** - 一个变量搞定所有连接信息
2. ✅ **标准兼容** - 符合 12-Factor App 和云平台标准
3. ✅ **向后兼容** - 不破坏现有配置方式
4. ✅ **灵活可选** - 可以选用或不用

**推荐在生产环境使用 DATABASE_URL，让配置更清晰、更安全！** 🚀

