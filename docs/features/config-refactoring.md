# 配置结构重构说明

## 概述

配置系统已经重构为更加模块化和易于维护的结构，将配置分组到独立的文件中。

## 新的文件结构

```
faster_app/settings/
├── groups/                 # 配置组目录
│   ├── __init__.py        # 导出所有配置组
│   ├── server.py          # 服务器配置 (ServerSettings)
│   ├── jwt.py             # JWT 配置 (JWTSettings)
│   ├── database.py        # 数据库配置 (DatabaseSettings)
│   └── log.py             # 日志配置 (LogSettings)
└── builtins/
    └── settings.py        # 主配置类 (Settings)
```

## 主要改进

### 1. 文件名简洁

- ✅ 主配置类名改为 `Settings`（而不是 `GroupedSettings`）
- ✅ 文件名保持简洁 `settings.py`

### 2. 配置组独立文件

每个配置组都有自己的文件，遵循单一职责原则：

- `server.py` - 服务器配置（host, port）
- `jwt.py` - JWT 配置（secret_key, algorithm, access_token_expire_minutes）
- `database.py` - 数据库配置（type, host, port, user, password, database）
- `log.py` - 日志配置（level, format）

### 3. 代码隔离

- 每个配置组独立维护
- 修改某个配置组不影响其他
- 更容易测试和调试

### 4. 导入清晰

```python
# 导入配置组
from faster_app.settings.groups import (
    ServerSettings,
    JWTSettings,
    DatabaseSettings,
    LogSettings,
)

# 导入主配置
from faster_app.settings.builtins.settings import Settings

# 或者使用别名（向后兼容）
from faster_app.settings.builtins.settings import DefaultSettings
```

## 使用方式

### 基本使用

```python
from faster_app.settings.builtins.settings import Settings

# 创建配置实例
settings = Settings()

# 访问配置
print(settings.project_name)           # 基础配置
print(settings.server.host)            # 服务器配置
print(settings.jwt.secret_key)         # JWT 配置
print(settings.database.host)          # 数据库配置
print(settings.log.level)              # 日志配置
```

### 自定义配置组

```python
from faster_app.settings.groups import DatabaseSettings
from faster_app.settings.builtins.settings import Settings

# 创建自定义数据库配置
custom_db = DatabaseSettings(
    type="postgres",
    host="prod.db.com",
    port=5432,
    user="prod_user",
    password="Str0ng!P@ssw0rd",
    database="production_db"
)

# 使用自定义配置
settings = Settings(database=custom_db)
```

### 环境变量

使用双下划线 `__` 表示嵌套：

```bash
# 基础配置
export FASTER_PROJECT_NAME="My App"
export FASTER_DEBUG=false

# 服务器配置
export FASTER_SERVER__HOST=10.0.0.1
export FASTER_SERVER__PORT=8000

# JWT 配置
export FASTER_JWT__SECRET_KEY=your-secret-key
export FASTER_JWT__ALGORITHM=HS256

# 数据库配置
export FASTER_DATABASE__TYPE=postgres
export FASTER_DATABASE__HOST=db.production.com
export FASTER_DATABASE__PASSWORD=your-password

# 日志配置
export FASTER_LOG__LEVEL=INFO
```

## 向后兼容

为了保持向后兼容，提供了 `DefaultSettings` 别名：

```python
# 新方式（推荐）
from faster_app.settings.builtins.settings import Settings
settings = Settings()

# 旧方式（仍然可用）
from faster_app.settings.builtins.settings import DefaultSettings
settings = DefaultSettings()

# DefaultSettings 是 Settings 的别名
assert DefaultSettings is Settings  # True
```

## 配置发现

配置发现机制已更新以支持新的配置结构：

```python
from faster_app.settings.discover import SettingsDiscover

# 自动发现和合并配置
settings = SettingsDiscover().merge()

# 访问配置组
print(settings.server.host)
print(settings.database.type)
```

## 迁移指南

### 从旧的扁平配置迁移

#### 1. 更新导入

```python
# 旧代码
from faster_app.settings.builtins.settings import DefaultSettings

# 新代码（推荐）
from faster_app.settings.builtins.settings import Settings

# 或保持向后兼容
from faster_app.settings.builtins.settings import DefaultSettings  # 仍然可用
```

#### 2. 更新配置访问

```python
# 旧代码
settings.DB_HOST
settings.DB_PORT
settings.SECRET_KEY
settings.LOG_LEVEL

# 新代码
settings.database.host
settings.database.port
settings.jwt.secret_key
settings.log.level
```

#### 3. 更新环境变量

```bash
# 旧环境变量
FASTER_DB_HOST=localhost
FASTER_SECRET_KEY=key

# 新环境变量（使用双下划线）
FASTER_DATABASE__HOST=localhost
FASTER_JWT__SECRET_KEY=key
```

#### 4. 更新日志配置引用

如果你直接使用了 `configs.LOG_LEVEL`，需要改为 `configs.log.level`：

```python
# 旧代码
configs.LOG_LEVEL
configs.LOG_FORMAT

# 新代码
configs.log.level
configs.log.format
```

## 优势总结

| 方面 | 旧结构 | 新结构 |
|------|--------|--------|
| **文件组织** | 单一文件 | 多文件分组 |
| **代码隔离** | ❌ 混在一起 | ✅ 独立文件 |
| **可维护性** | ⚠️ 一般 | ✅ 优秀 |
| **可测试性** | ⚠️ 一般 | ✅ 优秀 |
| **导入清晰度** | ⚠️ 一般 | ✅ 优秀 |
| **单一职责** | ❌ 否 | ✅ 是 |
| **文件名** | ❌ 冗长 | ✅ 简洁 |

## 最佳实践

### ✅ 推荐做法

1. **使用新的配置结构**
   ```python
   from faster_app.settings.builtins.settings import Settings
   settings = Settings()
   ```

2. **访问配置时使用分组**
   ```python
   settings.server.host
   settings.database.type
   settings.jwt.algorithm
   ```

3. **配置组独立使用**
   ```python
   from faster_app.settings.groups import DatabaseSettings
   db = DatabaseSettings(type="postgres")
   ```

4. **环境变量使用双下划线**
   ```bash
   export FASTER_DATABASE__HOST=localhost
   ```

### ❌ 避免的做法

1. ❌ 混用旧的扁平访问方式（已不支持）
2. ❌ 直接修改配置组内部实现（使用继承）
3. ❌ 跨配置组创建依赖关系

## 故障排查

### 问题 1: AttributeError: 'Settings' object has no attribute 'DB_HOST'

**原因：** 使用了旧的扁平配置字段名

**解决：**
```python
# ❌ 错误
settings.DB_HOST

# ✅ 正确
settings.database.host
```

### 问题 2: 环境变量不生效

**原因：** 使用了旧的环境变量格式

**解决：**
```bash
# ❌ 错误
export FASTER_DB_HOST=localhost

# ✅ 正确
export FASTER_DATABASE__HOST=localhost
```

### 问题 3: 导入错误

**原因：** 使用了旧的导入路径

**解决：**
```python
# ❌ 可能失败
from faster_app.settings.groups.server import ServerSettings

# ✅ 推荐
from faster_app.settings.groups import ServerSettings
```

## 总结

新的配置结构提供了：

- ✅ 更清晰的代码组织
- ✅ 更好的可维护性
- ✅ 更强的代码隔离
- ✅ 更简洁的文件命名
- ✅ 完整的向后兼容
- ✅ 符合单一职责原则

建议在所有新代码中使用新的配置结构！

