# 配置敏感信息保护使用指南

## 概述

从本次更新开始，Faster APP 的配置系统增强了敏感信息保护功能，使用 Pydantic 的 `SecretStr` 类型来保护敏感数据。

## 主要特性

### 1. 敏感字段保护

以下字段现在使用 `SecretStr` 类型保护：
- `SECRET_KEY`: JWT 签名密钥
- `DB_PASSWORD`: 数据库密码

### 2. 自动验证

#### 生产环境检查

当 `DEBUG=False` 时（生产环境），系统会自动验证：

**SECRET_KEY 验证：**
- ❌ 不能使用默认值 `your-secret-key-here-change-in-production`
- ✅ 必须通过环境变量设置自定义密钥

**DB_PASSWORD 验证：**
- ❌ 不能使用弱密码：`postgres`, `password`, `123456`, `admin`, `root`
- ✅ 必须使用强密码

#### 开发环境

当 `DEBUG=True` 时（开发环境），允许使用默认凭据，方便开发调试。

### 3. 序列化保护

敏感信息在序列化时自动隐藏：

```python
from faster_app.settings.discover import SettingsDiscover

settings = SettingsDiscover().merge()

# 获取真实值
secret = settings.SECRET_KEY.get_secret_value()  # 返回实际密钥

# 序列化时自动隐藏
settings_dict = settings.model_dump()
print(settings_dict['SECRET_KEY'])  # 输出: **********
```

## 使用方式

### 方式 1: 环境变量（推荐）

在 `.env` 文件中设置：

```bash
# 开发环境
DEBUG=true
SECRET_KEY=my-dev-secret-key
DB_PASSWORD=postgres

# 生产环境
DEBUG=false
SECRET_KEY=your-super-secret-production-key-with-at-least-32-chars
DB_PASSWORD=YourStr0ng!Pr0duction@P@ssw0rd
```

### 方式 2: 代码中设置

```python
from faster_app.settings.builtins.settings import DefaultSettings

# 开发环境
settings = DefaultSettings(
    DEBUG=True,
    # 使用默认值即可
)

# 生产环境
settings = DefaultSettings(
    DEBUG=False,
    SECRET_KEY="your-super-secret-production-key",
    DB_PASSWORD="YourStr0ng!Pr0duction@P@ssw0rd"
)
```

### 方式 3: 自定义配置类

在 `config/settings.py` 中：

```python
from faster_app.settings.builtins.settings import DefaultSettings
from pydantic import SecretStr

class Settings(DefaultSettings):
    """自定义配置"""
    
    # 继承所有默认配置
    # 可以覆盖任何配置项
    PROJECT_NAME: str = "My Project"
    
    # 敏感信息使用 SecretStr
    SECRET_KEY: SecretStr = SecretStr("my-custom-key")
```

## 访问敏感值

在应用代码中使用时，需要调用 `get_secret_value()` 获取真实值：

```python
from faster_app.app import app

# 获取配置
settings = app.settings

# 访问普通字段
project_name = settings.PROJECT_NAME

# 访问敏感字段
secret_key = settings.SECRET_KEY.get_secret_value()
db_password = settings.DB_PASSWORD.get_secret_value()
```

## TORTOISE_ORM 配置

数据库配置会自动处理 `SecretStr`，无需手动转换：

```python
# TORTOISE_ORM 中的密码已自动解密
settings.TORTOISE_ORM["connections"]["POSTGRES"]["credentials"]["password"]
# 返回解密后的字符串，可直接用于数据库连接
```

## 验证错误示例

### 生产环境使用默认 SECRET_KEY

```python
settings = DefaultSettings(DEBUG=False)
# ValidationError: 生产环境必须修改 SECRET_KEY！
```

### 生产环境使用弱密码

```python
settings = DefaultSettings(
    DEBUG=False,
    SECRET_KEY="my-custom-key",
    DB_PASSWORD="postgres"  # 弱密码
)
# ValidationError: 生产环境不能使用弱密码 'postgres'！
```

## 最佳实践

### ✅ 推荐做法

1. **使用环境变量**：生产环境的敏感信息应通过环境变量注入
2. **不同环境使用不同配置**：开发、测试、生产环境分别使用不同的 `.env` 文件
3. **强密码策略**：生产环境使用复杂的强密码
4. **版本控制排除**：确保 `.env` 文件在 `.gitignore` 中

### ❌ 避免做法

1. ❌ 在代码中硬编码敏感信息
2. ❌ 将 `.env` 文件提交到版本控制
3. ❌ 生产环境使用默认或弱密码
4. ❌ 在日志中输出敏感信息

## 配置文件示例

### .env.example（提交到版本控制）

```bash
# 项目配置
PROJECT_NAME=Faster APP
VERSION=0.0.1
DEBUG=true

# 服务器配置
HOST=0.0.0.0
PORT=8000

# JWT 配置
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DB_TYPE=sqlite
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=change-me-in-production
DB_DATABASE=faster_app
```

### .env（不提交到版本控制）

```bash
# 实际使用的配置，包含真实的敏感信息
SECRET_KEY=actual-secret-key-here
DB_PASSWORD=actual-strong-password-here
```

## 测试

运行测试验证配置功能：

```bash
uv run python test_settings_security.py
```

## 技术细节

### SecretStr 类型

`SecretStr` 是 Pydantic 提供的特殊类型：
- 自动隐藏字符串表示（`__repr__`）
- 序列化时默认隐藏
- 通过 `get_secret_value()` 获取真实值

### 验证器

使用 Pydantic 的 `field_validator` 装饰器实现：
- 在字段赋值时自动触发
- 可以访问其他字段的值
- 抛出 `ValueError` 来拒绝无效值

### 配置合并

`discover.py` 中的 `merge()` 方法已更新：
- 使用 `mode='python'` 保留 `SecretStr` 类型
- 支持用户配置中的 `SecretStr` 字段
- 动态创建类时识别 `SecretStr` 类型

## 升级指南

如果你从旧版本升级：

1. **检查环境变量**：确保生产环境设置了强密码
2. **更新代码**：如果直接访问密码字段，需要改为调用 `get_secret_value()`
3. **测试配置**：在部署前测试生产环境配置是否通过验证

```python
# 旧代码
password = settings.DB_PASSWORD  # 返回 SecretStr 对象

# 新代码
password = settings.DB_PASSWORD.get_secret_value()  # 返回字符串
```

## 常见问题

**Q: 为什么开发环境可以使用弱密码？**

A: 为了方便本地开发和调试，开发环境（`DEBUG=True`）不强制密码策略。但生产环境必须使用强密码。

**Q: 如何在日志中输出配置（不包含敏感信息）？**

A: 直接使用 `model_dump()`，敏感字段会自动隐藏：

```python
import json
settings_dict = settings.model_dump()
print(json.dumps(settings_dict, indent=2))
```

**Q: 可以自定义弱密码列表吗？**

A: 可以，在 `config/settings.py` 中继承 `DefaultSettings` 并重写 `validate_db_password_in_production` 方法。

**Q: TORTOISE_ORM 配置为什么能直接使用密码字符串？**

A: 在 `DefaultSettings.__init__` 中，我们调用了 `get_secret_value()` 将 `SecretStr` 转换为字符串，所以 `TORTOISE_ORM` 配置中的密码已经是解密后的字符串。

