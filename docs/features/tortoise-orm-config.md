# TORTOISE_ORM 配置优化

## 问题背景

在之前的实现中，`TORTOISE_ORM` 配置是在 `__init__` 方法中动态生成的：

```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.TORTOISE_ORM = {
        "connections": {...},
        "apps": {...}
    }
```

这种实现存在以下问题：

### ❌ 存在的问题

1. **不符合最佳实践**
   - 在 `__init__` 中手动设置实例属性违反了 Pydantic 的设计原则
   - Pydantic 模型应该通过字段定义或计算字段来管理数据

2. **配置不会动态更新**
   - 如果在实例化后修改了 `DB_HOST`、`DB_PORT` 等字段
   - `TORTOISE_ORM` 配置不会自动更新，仍然保留初始化时的值
   - 可能导致配置不一致的 Bug

3. **代码可维护性差**
   - `__init__` 方法中的副作用使代码难以理解和维护
   - 不利于单元测试和调试

4. **潜在的循环引用风险**
   - 在 `__init__` 中访问其他字段可能导致初始化顺序问题

## 解决方案

使用 Python 的 `@property` 装饰器将 `TORTOISE_ORM` 改为动态计算属性：

```python
@property
def TORTOISE_ORM(self) -> dict:
    """
    动态生成 Tortoise ORM 配置
    
    优点:
    1. 配置是动态计算的，当依赖的字段改变时会自动更新
    2. 避免在 __init__ 中手动设置实例属性
    3. 符合 Pydantic 最佳实践
    4. 懒加载，只在需要时计算
    
    Returns:
        Tortoise ORM 配置字典
    """
    return {
        "connections": {
            "SQLITE": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {
                    "file_path": f"{self._normalize_db_name(self.PROJECT_NAME)}.db"
                },
            },
            "POSTGRES": {
                "engine": self.DB_ENGINE,
                "credentials": {
                    "host": self.DB_HOST,
                    "port": self.DB_PORT,
                    "user": self.DB_USER,
                    "password": self.DB_PASSWORD.get_secret_value(),
                    "database": self.DB_DATABASE,
                },
            },
        },
        "apps": {
            "models": {
                "default_connection": self.DB_TYPE.upper()
            }
        },
    }
```

## 优势对比

### ✅ 新实现的优点

| 特性 | 旧实现 (`__init__`) | 新实现 (`@property`) |
|------|---------------------|---------------------|
| **动态更新** | ❌ 不支持 | ✅ 自动更新 |
| **懒加载** | ❌ 初始化时生成 | ✅ 按需计算 |
| **符合最佳实践** | ❌ 副作用 | ✅ 声明式 |
| **代码清晰度** | ❌ 较差 | ✅ 优秀 |
| **可测试性** | ❌ 一般 | ✅ 优秀 |
| **内存效率** | ❌ 立即占用 | ✅ 按需生成 |

### 1. 配置动态更新

**旧实现的问题：**
```python
settings = DefaultSettings()
print(settings.TORTOISE_ORM["connections"]["POSTGRES"]["credentials"]["host"])
# 输出: localhost

settings.DB_HOST = "192.168.1.100"
print(settings.TORTOISE_ORM["connections"]["POSTGRES"]["credentials"]["host"])
# 输出: localhost (未更新！❌)
```

**新实现的优势：**
```python
settings = DefaultSettings()
print(settings.TORTOISE_ORM["connections"]["POSTGRES"]["credentials"]["host"])
# 输出: localhost

settings.DB_HOST = "192.168.1.100"
print(settings.TORTOISE_ORM["connections"]["POSTGRES"]["credentials"]["host"])
# 输出: 192.168.1.100 (自动更新！✅)
```

### 2. 懒加载

**旧实现：**
- 每次创建 `DefaultSettings` 实例时都会立即生成 `TORTOISE_ORM`
- 即使不使用数据库功能也会计算配置

**新实现：**
- 只有在访问 `TORTOISE_ORM` 时才会计算
- 如果不使用数据库，不会有任何开销

```python
# 不使用数据库
settings = DefaultSettings()
# 此时 TORTOISE_ORM 还未生成，无性能开销

# 需要使用时才生成
orm_config = settings.TORTOISE_ORM  # 此时才计算
```

### 3. 符合 Pydantic 最佳实践

Pydantic 推荐的配置方式：
- ✅ 使用字段定义（Field）
- ✅ 使用 `@property` 或 `@computed_field` 做计算
- ❌ 避免在 `__init__` 中设置实例属性

### 4. 敏感信息安全

新实现确保每次访问时都调用 `get_secret_value()`，避免密码泄露：

```python
settings = DefaultSettings(DB_PASSWORD="MySecret")

# 每次访问都会重新解密
password = settings.TORTOISE_ORM["connections"]["POSTGRES"]["credentials"]["password"]
# 返回: "MySecret"
```

## 使用方式

### 基本使用

```python
from faster_app.settings.discover import SettingsDiscover

# 获取配置
settings = SettingsDiscover().merge()

# 访问 TORTOISE_ORM（自动计算）
orm_config = settings.TORTOISE_ORM

# 使用配置初始化 Tortoise
from tortoise import Tortoise

await Tortoise.init(config=settings.TORTOISE_ORM)
```

### 动态修改配置

```python
# 修改数据库配置
settings.DB_HOST = "prod.database.com"
settings.DB_PORT = 3306
settings.DB_DATABASE = "production_db"

# TORTOISE_ORM 自动反映新配置
orm_config = settings.TORTOISE_ORM
print(orm_config["connections"]["POSTGRES"]["credentials"]["host"])
# 输出: prod.database.com
```

### 切换数据库类型

```python
# 默认使用 SQLite
settings = DefaultSettings()
print(settings.TORTOISE_ORM["apps"]["models"]["default_connection"])
# 输出: SQLITE

# 切换到 PostgreSQL
settings.DB_TYPE = "postgres"
print(settings.TORTOISE_ORM["apps"]["models"]["default_connection"])
# 输出: POSTGRES
```

### 项目名称自动规范化

```python
settings = DefaultSettings(PROJECT_NAME="My Cool Project")
sqlite_path = settings.TORTOISE_ORM["connections"]["SQLITE"]["credentials"]["file_path"]
print(sqlite_path)
# 输出: my_cool_project.db

# 修改项目名
settings.PROJECT_NAME = "Test-App (2024)!"
new_sqlite_path = settings.TORTOISE_ORM["connections"]["SQLITE"]["credentials"]["file_path"]
print(new_sqlite_path)
# 输出: test_app_2024.db
```

## 注意事项

### 1. Property 不会序列化

`@property` 不是 Pydantic 字段，因此不会出现在 `model_dump()` 中：

```python
settings = DefaultSettings()
settings_dict = settings.model_dump()

# TORTOISE_ORM 不在字典中（预期行为）
print("TORTOISE_ORM" in settings_dict)  # False

# 但可以直接访问
orm_config = settings.TORTOISE_ORM  # 正常工作
```

如果需要序列化 TORTOISE_ORM，可以手动添加：

```python
settings_dict = settings.model_dump()
settings_dict["TORTOISE_ORM"] = settings.TORTOISE_ORM
```

### 2. 每次访问都会重新计算

Property 每次访问都会重新生成字典：

```python
config1 = settings.TORTOISE_ORM
config2 = settings.TORTOISE_ORM

# 值相同
assert config1 == config2  # True

# 但是不同的对象实例
assert config1 is not config2  # True
```

如果需要缓存，可以保存到变量：

```python
# 缓存配置避免重复计算
orm_config = settings.TORTOISE_ORM

# 多次使用缓存的配置
await Tortoise.init(config=orm_config)
# ... 其他使用 orm_config 的地方
```

### 3. 与自动发现机制集成

TORTOISE_ORM 中的 `models` 列表由自动发现机制填充：

```python
from faster_app.models.discover import ModelsDiscover

# 发现所有模型
models = ModelsDiscover().discover_models()

# 填充到配置中
settings.TORTOISE_ORM["apps"]["models"]["models"] = models
```

## 性能对比

### 内存使用

| 场景 | 旧实现 | 新实现 |
|------|--------|--------|
| 创建实例 | 立即分配内存 | 无额外内存 |
| 不使用数据库 | 浪费内存 | 零开销 |
| 频繁访问 | 固定内存 | 按需生成 |

### 计算开销

- **旧实现**: 初始化时计算一次
- **新实现**: 每次访问时计算（通常访问次数很少）

在实际应用中：
- 应用启动时通常只访问一次 `TORTOISE_ORM`
- 性能差异可忽略不计
- 新实现的优势（动态更新、代码清晰）远大于微小的性能开销

## 测试用例

完整的测试覆盖：

```python
def test_tortoise_orm_dynamic_updates():
    """测试动态更新"""
    settings = DefaultSettings()
    
    settings.DB_HOST = "192.168.1.100"
    assert settings.TORTOISE_ORM["connections"]["POSTGRES"]["credentials"]["host"] == "192.168.1.100"
    
    settings.DB_PORT = 3306
    assert settings.TORTOISE_ORM["connections"]["POSTGRES"]["credentials"]["port"] == 3306

def test_tortoise_orm_password_decryption():
    """测试密码解密"""
    settings = DefaultSettings(DB_PASSWORD="MySecret")
    password = settings.TORTOISE_ORM["connections"]["POSTGRES"]["credentials"]["password"]
    assert password == "MySecret"

def test_tortoise_orm_sqlite_path():
    """测试 SQLite 路径生成"""
    settings = DefaultSettings(PROJECT_NAME="My Project")
    path = settings.TORTOISE_ORM["connections"]["SQLITE"]["credentials"]["file_path"]
    assert path == "my_project.db"
```

## 总结

将 `TORTOISE_ORM` 从 `__init__` 方法改为 `@property` 带来了多方面的改进：

### 主要收益

1. ✅ **配置动态更新** - 修改字段后自动反映变化
2. ✅ **懒加载** - 按需计算，提高启动性能
3. ✅ **符合最佳实践** - 遵循 Pydantic 设计原则
4. ✅ **代码清晰** - 声明式编程，易于理解
5. ✅ **易于测试** - 减少副作用，提高可测试性
6. ✅ **避免 Bug** - 消除配置不一致的风险

### 适用场景

这种模式适合所有需要基于其他字段动态计算的配置项：

- ✅ 数据库连接配置
- ✅ API 端点 URL
- ✅ 日志配置
- ✅ 缓存配置
- ✅ 任何派生配置

### 未来优化

如果需要缓存以避免重复计算，可以使用 `functools.lru_cache`：

```python
from functools import lru_cache

@property
def TORTOISE_ORM(self) -> dict:
    return self._get_tortoise_orm_config()

@lru_cache(maxsize=1)
def _get_tortoise_orm_config(self) -> dict:
    # 配置生成逻辑
    return {...}
```

但在当前场景下，直接计算已经足够高效。

