# 配置分组与嵌套

## 概述

配置分组与嵌套是一种最佳实践，通过将相关配置组织成独立的配置类，提高代码的可读性、可维护性和类型安全性。

## 为什么需要配置分组？

### ❌ 扁平化配置的问题

```python
# 所有配置混在一起，难以维护
class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "App"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # JWT 配置
    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库配置
    DB_TYPE: str = "sqlite"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_DATABASE: str = "db"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "STRING"
    # ... 还有更多配置
```

**问题：**
- 配置项太多，难以找到相关配置
- 命名容易冲突（多个模块可能都有 `host`, `port`）
- 无法独立验证某个模块的配置
- IDE 自动补全体验差
- 难以重用配置

### ✅ 分组配置的优势

```python
# 配置按功能分组，清晰明了
class Settings(BaseSettings):
    # 基础配置（保持扁平）
    project_name: str = "App"
    debug: bool = True
    
    # 配置组（嵌套）
    server: ServerSettings = ServerSettings()
    jwt: JWTSettings = JWTSettings()
    database: DatabaseSettings = DatabaseSettings()
    log: LogSettings = LogSettings()
```

**访问方式对比：**

```python
# 扁平化（难读）
settings.DB_HOST
settings.DB_PORT
settings.DB_USER
settings.SECRET_KEY
settings.ALGORITHM

# 分组（清晰）
settings.database.host
settings.database.port
settings.database.user
settings.jwt.secret_key
settings.jwt.algorithm
```

## 配置分组的8大优势

### 1. 逻辑清晰 📋

相关配置归类在一起，一眼就能看出某个配置属于哪个模块。

```python
# ✅ 清晰：数据库相关配置都在 database 下
settings.database.host
settings.database.port
settings.database.user
settings.database.password
```

### 2. 易于维护 🔧

修改某个模块的配置不影响其他模块。

```python
# 只修改数据库配置
class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    # 添加新字段不影响其他配置组
    connection_pool_size: int = 10
```

### 3. 类型安全 🛡️

每个配置组都有独立的类型定义，编译期就能发现错误。

```python
# IDE 会立即提示类型错误
settings.server.port = "invalid"  # ❌ 类型错误: int ≠ str
```

### 4. IDE 智能提示 💡

分组配置大大改善了 IDE 的自动补全体验。

```python
settings.server.  # IDE 提示: host, port
settings.jwt.     # IDE 提示: secret_key, algorithm, access_token_expire_minutes
settings.database.  # IDE 提示: type, host, port, user, password, database
settings.log.     # IDE 提示: level, format
```

### 5. 可重用性 ♻️

配置组可以独立使用和重用。

```python
# 创建独立的配置组
dev_db = DatabaseSettings(type="sqlite", database="dev.db")
prod_db = DatabaseSettings(type="postgres", host="prod.db.com")

# 在不同环境中重用
dev_settings = Settings(database=dev_db)
prod_settings = Settings(database=prod_db)
```

### 6. 验证精细 ✓

每个配置组可以有自己的验证逻辑。

```python
class DatabaseSettings(BaseModel):
    port: int
    
    @field_validator("port")
    def validate_port(cls, v):
        # 只验证数据库端口，不影响其他配置
        if not 1 <= v <= 65535:
            raise ValueError("database.port 无效")
        return v
```

### 7. 命名空间隔离 🔒

避免字段名冲突。

```python
# 多个模块可以有相同的字段名，不会冲突
settings.server.host      # 服务器主机
settings.database.host    # 数据库主机
settings.cache.host       # 缓存主机
```

### 8. 向后兼容 🔄

可以保留旧的访问方式，同时提供新的分组方式。

```python
# 新方式（推荐）
settings.database.host

# 旧方式（通过属性映射）
@property
def DB_HOST(self):
    return self.database.host
```

## 实现方式

### 方式 1: 使用 BaseModel（推荐）

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# 定义配置组
class ServerSettings(BaseModel):
    """服务器配置组"""
    host: str = "0.0.0.0"
    port: int = 8000

class DatabaseSettings(BaseModel):
    """数据库配置组"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "app_db"

# 主配置类
class Settings(BaseSettings):
    """应用配置"""
    project_name: str = "My App"
    debug: bool = True
    
    # 嵌套配置组
    server: ServerSettings = ServerSettings()
    database: DatabaseSettings = DatabaseSettings()
    
    class Config:
        env_file = ".env"
        env_prefix = "APP_"
        env_nested_delimiter = "__"  # 支持 APP_DATABASE__HOST
```

### 方式 2: 使用 Field 设置默认值

```python
from pydantic import BaseModel, Field

class ServerSettings(BaseModel):
    host: str = Field(default="0.0.0.0", description="服务器监听地址")
    port: int = Field(default=8000, ge=1, le=65535, description="服务器端口")
```

### 方式 3: 使用工厂函数

```python
def create_database_settings(env: str = "dev") -> DatabaseSettings:
    """根据环境创建数据库配置"""
    if env == "prod":
        return DatabaseSettings(
            type="postgres",
            host="prod.db.com",
            port=5432
        )
    return DatabaseSettings(type="sqlite", database="dev.db")

settings = Settings(database=create_database_settings("prod"))
```

## 环境变量映射

### 嵌套分隔符

使用双下划线 `__` 来表示嵌套关系：

```bash
# 扁平化配置
export FASTER_DB_HOST=localhost
export FASTER_DB_PORT=5432

# 分组配置（使用双下划线）
export FASTER_DATABASE__HOST=localhost
export FASTER_DATABASE__PORT=5432
export FASTER_SERVER__HOST=0.0.0.0
export FASTER_SERVER__PORT=8000
export FASTER_JWT__SECRET_KEY=your-secret-key
```

### .env 文件示例

```bash
# .env

# 基础配置
FASTER_PROJECT_NAME=My Production App
FASTER_DEBUG=false

# 服务器配置（使用双下划线）
FASTER_SERVER__HOST=10.0.0.1
FASTER_SERVER__PORT=8000

# JWT 配置
FASTER_JWT__SECRET_KEY=production-secret-key-with-at-least-32-chars
FASTER_JWT__ALGORITHM=HS256
FASTER_JWT__ACCESS_TOKEN_EXPIRE_MINUTES=60

# 数据库配置
FASTER_DATABASE__TYPE=postgres
FASTER_DATABASE__HOST=db.production.com
FASTER_DATABASE__PORT=5432
FASTER_DATABASE__USER=prod_user
FASTER_DATABASE__PASSWORD=Str0ng!P@ssw0rd
FASTER_DATABASE__DATABASE=production_db

# 日志配置
FASTER_LOG__LEVEL=INFO
FASTER_LOG__FORMAT=STRING
```

## 使用示例

### 基本使用

```python
from faster_app.settings.builtins.settings_grouped import GroupedSettings

# 加载配置
settings = GroupedSettings()

# 访问配置
print(settings.project_name)
print(settings.server.host)
print(settings.server.port)
print(settings.database.host)
print(settings.jwt.algorithm)
print(settings.log.level)
```

### 覆盖配置

```python
from faster_app.settings.builtins.settings_grouped import (
    GroupedSettings,
    ServerSettings,
    DatabaseSettings
)

# 方式 1: 通过构造函数
settings = GroupedSettings(
    debug=False,
    server=ServerSettings(host="10.0.0.1", port=9000),
    database=DatabaseSettings(
        type="postgres",
        host="db.example.com",
        port=5432
    )
)

# 方式 2: 通过环境变量
# export FASTER_SERVER__HOST=10.0.0.1
# export FASTER_DATABASE__HOST=db.example.com
settings = GroupedSettings()
```

### 条件配置

```python
def get_settings(env: str = "dev") -> GroupedSettings:
    """根据环境返回配置"""
    if env == "prod":
        return GroupedSettings(
            debug=False,
            server=ServerSettings(host="10.0.0.1"),
            database=DatabaseSettings(
                type="postgres",
                host="prod.db.com"
            )
        )
    elif env == "test":
        return GroupedSettings(
            debug=True,
            database=DatabaseSettings(type="sqlite", database=":memory:")
        )
    else:  # dev
        return GroupedSettings(debug=True)

# 使用
settings = get_settings("prod")
```

## 最佳实践

### ✅ 推荐做法

1. **按功能分组**
   ```python
   # 将相关配置归类
   server: ServerSettings
   database: DatabaseSettings
   jwt: JWTSettings
   log: LogSettings
   ```

2. **使用小写字段名**
   ```python
   # ✅ 推荐：小写 + 下划线
   project_name: str
   secret_key: str
   
   # ❌ 不推荐：大写
   PROJECT_NAME: str
   SECRET_KEY: str
   ```

3. **提供描述性的 docstring**
   ```python
   class ServerSettings(BaseModel):
       """
       服务器配置组
       
       包含服务器监听地址、端口等配置
       """
       host: str = Field(description="服务器监听地址")
       port: int = Field(description="服务器端口")
   ```

4. **每个配置组独立验证**
   ```python
   class DatabaseSettings(BaseModel):
       port: int
       
       @field_validator("port")
       def validate_port(cls, v):
           # 验证逻辑只针对当前配置组
           ...
   ```

5. **保持向后兼容**
   ```python
   class Settings(BaseSettings):
       database: DatabaseSettings
       
       # 提供旧的访问方式
       @property
       def DB_HOST(self) -> str:
           return self.database.host
   ```

### ❌ 避免的做法

1. ❌ 过度嵌套（不要超过 3 层）
2. ❌ 在配置组之间创建依赖关系
3. ❌ 混用扁平和分组配置
4. ❌ 配置组过于细碎

## 迁移指南

### 从扁平配置迁移到分组配置

#### 步骤 1: 创建配置组类

```python
# 旧的扁平配置
class OldSettings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "user"

# 新的分组配置
class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "user"

class NewSettings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
```

#### 步骤 2: 更新环境变量

```bash
# 旧的环境变量
FASTER_DB_HOST=localhost
FASTER_DB_PORT=5432

# 新的环境变量（使用双下划线）
FASTER_DATABASE__HOST=localhost
FASTER_DATABASE__PORT=5432
```

#### 步骤 3: 更新代码中的访问方式

```python
# 旧代码
host = settings.DB_HOST
port = settings.DB_PORT

# 新代码
host = settings.database.host
port = settings.database.port
```

#### 步骤 4: 提供兼容层（可选）

```python
class NewSettings(BaseSettings):
    database: DatabaseSettings
    
    # 兼容旧的访问方式
    @property
    def DB_HOST(self) -> str:
        return self.database.host
    
    @property
    def DB_PORT(self) -> int:
        return self.database.port
```

## 实际案例

### 案例 1: 微服务配置

```python
class ServiceDiscoverySettings(BaseModel):
    """服务发现配置"""
    enabled: bool = True
    consul_host: str = "localhost"
    consul_port: int = 8500

class TracingSettings(BaseModel):
    """链路追踪配置"""
    enabled: bool = False
    jaeger_host: str = "localhost"
    jaeger_port: int = 6831

class MicroserviceSettings(BaseSettings):
    """微服务配置"""
    service_name: str = "my-service"
    service_discovery: ServiceDiscoverySettings = ServiceDiscoverySettings()
    tracing: TracingSettings = TracingSettings()
```

### 案例 2: 多数据库配置

```python
class PrimaryDatabaseSettings(BaseModel):
    """主数据库配置"""
    host: str = "primary.db.com"
    port: int = 5432

class ReadReplicaSettings(BaseModel):
    """只读副本配置"""
    host: str = "replica.db.com"
    port: int = 5432

class MultiDBSettings(BaseSettings):
    """多数据库配置"""
    primary: PrimaryDatabaseSettings = PrimaryDatabaseSettings()
    replica: ReadReplicaSettings = ReadReplicaSettings()
```

## 常见问题

### Q: 分组配置是否影响性能？

A: 不会。配置在应用启动时加载一次，分组只是逻辑上的组织方式，不影响运行时性能。

### Q: 如何在不同环境使用不同的配置组？

A: 使用工厂函数或条件逻辑：

```python
def get_database_settings(env: str):
    if env == "prod":
        return DatabaseSettings(type="postgres", host="prod.db")
    return DatabaseSettings(type="sqlite")

settings = Settings(database=get_database_settings(os.getenv("ENV")))
```

### Q: 配置组可以再嵌套吗？

A: 可以，但不建议超过 2-3 层：

```python
class CredentialsSettings(BaseModel):
    user: str
    password: str

class DatabaseSettings(BaseModel):
    host: str
    credentials: CredentialsSettings  # 嵌套的配置组
```

### Q: 如何验证配置组之间的关系？

A: 使用模型级别的验证器：

```python
@model_validator(mode="after")
def validate_config_relationships(self):
    if self.server.port == self.database.port:
        raise ValueError("服务器和数据库不能使用相同的端口")
    return self
```

## 总结

配置分组与嵌套是现代应用配置管理的最佳实践：

| 方面 | 扁平配置 | 分组配置 |
|------|---------|---------|
| **可读性** | ❌ 差 | ✅ 优秀 |
| **维护性** | ❌ 困难 | ✅ 容易 |
| **类型安全** | ⚠️ 一般 | ✅ 强 |
| **IDE 支持** | ⚠️ 一般 | ✅ 优秀 |
| **可重用性** | ❌ 差 | ✅ 优秀 |
| **验证精细度** | ⚠️ 一般 | ✅ 精细 |
| **命名空间** | ❌ 易冲突 | ✅ 隔离 |

**推荐在所有新项目中使用配置分组！**

