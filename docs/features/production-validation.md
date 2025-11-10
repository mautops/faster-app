# 生产环境配置验证（安全）

## 概述

Faster APP 提供了全面的生产环境配置验证机制，确保应用在生产环境部署时的安全性和稳定性。

## 验证层级

### 1. 字段级验证（Field Validators）

针对单个字段的即时验证，在字段赋值时自动触发。

### 2. 模型级验证（Model Validators）

在所有字段验证完成后执行，可以进行跨字段的复杂验证逻辑。

## 具体验证规则

### 🔒 敏感信息验证

#### SECRET_KEY 验证

**开发环境：**
- ✅ 允许使用默认值
- ✅ 允许任意长度

**生产环境（DEBUG=False）：**
- ❌ 不能使用默认值 `your-secret-key-here-change-in-production`
- ❌ 长度必须至少 32 个字符
- ✅ 必须通过环境变量设置强密钥

```python
# ❌ 生产环境会拒绝
settings = DefaultSettings(
    DEBUG=False,
    SECRET_KEY="short",  # 太短
    DB_PASSWORD="ValidPassword123"
)
# ValidationError: 生产环境 SECRET_KEY 长度必须至少 32 个字符

# ✅ 生产环境接受
settings = DefaultSettings(
    DEBUG=False,
    SECRET_KEY="my-super-secret-production-key-12345678",  # ≥32 字符
    DB_PASSWORD="ValidPassword123"
)
```

#### DB_PASSWORD 验证

**开发环境：**
- ✅ 允许弱密码
- ✅ 允许任意长度

**生产环境（DEBUG=False）：**
- ❌ 不能使用弱密码：`postgres`, `password`, `123456`, `admin`, `root`
- ❌ 长度必须至少 8 个字符
- ✅ 必须使用强密码

```python
# ❌ 生产环境会拒绝
settings = DefaultSettings(
    DEBUG=False,
    SECRET_KEY="a" * 32,
    DB_PASSWORD="postgres"  # 弱密码
)
# ValidationError: 生产环境不能使用弱密码 'postgres'

# ✅ 生产环境接受
settings = DefaultSettings(
    DEBUG=False,
    SECRET_KEY="a" * 32,
    DB_PASSWORD="Str0ng!P@ssw0rd"  # ≥8 字符且不在弱密码列表
)
```

### 🔢 数值范围验证

#### PORT 验证

```python
# ✅ 有效端口
settings = DefaultSettings(PORT=8000)  # 1-65535

# ❌ 无效端口
settings = DefaultSettings(PORT=0)      # ValidationError
settings = DefaultSettings(PORT=70000)  # ValidationError
```

#### DB_PORT 验证

```python
# ✅ 有效数据库端口
settings = DefaultSettings(DB_PORT=5432)  # 1-65535

# ❌ 无效数据库端口
settings = DefaultSettings(DB_PORT=-1)    # ValidationError
```

#### ACCESS_TOKEN_EXPIRE_MINUTES 验证

```python
# ✅ 合理的过期时间
settings = DefaultSettings(ACCESS_TOKEN_EXPIRE_MINUTES=30)  # 1-43200

# ❌ 过短或过长
settings = DefaultSettings(ACCESS_TOKEN_EXPIRE_MINUTES=0)      # ValidationError: 必须 > 0
settings = DefaultSettings(ACCESS_TOKEN_EXPIRE_MINUTES=50000)  # ValidationError: 不应超过 30 天
```

**生产环境额外限制：**
- ❌ 不应少于 5 分钟（防止频繁重新认证）

```python
# ❌ 生产环境会拒绝
settings = DefaultSettings(
    DEBUG=False,
    SECRET_KEY="a" * 32,
    DB_PASSWORD="ValidPassword123",
    ACCESS_TOKEN_EXPIRE_MINUTES=2  # < 5
)
# ValidationError: 生产环境 ACCESS_TOKEN_EXPIRE_MINUTES 不应少于 5 分钟
```

### 📋 枚举值验证

#### LOG_LEVEL 验证

```python
# ✅ 有效日志级别（自动转换为大写）
settings = DefaultSettings(LOG_LEVEL="debug")   # → "DEBUG"
settings = DefaultSettings(LOG_LEVEL="INFO")    # → "INFO"
settings = DefaultSettings(LOG_LEVEL="error")   # → "ERROR"

# 允许的值：DEBUG, INFO, WARNING, ERROR, CRITICAL

# ❌ 无效日志级别
settings = DefaultSettings(LOG_LEVEL="TRACE")   # ValidationError
```

#### ALGORITHM 验证

```python
# ✅ 有效 JWT 算法
settings = DefaultSettings(ALGORITHM="HS256")   # 对称加密
settings = DefaultSettings(ALGORITHM="RS256")   # 非对称加密

# 允许的值：HS256, HS384, HS512, RS256, RS384, RS512

# ❌ 无效算法
settings = DefaultSettings(ALGORITHM="MD5")     # ValidationError
```

#### DB_TYPE 验证

```python
# ✅ 有效数据库类型（自动转换为小写）
settings = DefaultSettings(DB_TYPE="SQLITE")    # → "sqlite"
settings = DefaultSettings(DB_TYPE="postgres")  # → "postgres"
settings = DefaultSettings(DB_TYPE="MySQL")     # → "mysql"

# 允许的值：sqlite, postgres, mysql

# ❌ 无效数据库类型
settings = DefaultSettings(DB_TYPE="mongodb")   # ValidationError
```

### ⚠️ 生产环境警告（Warnings）

某些配置在生产环境下虽然可以工作，但存在潜在风险或不合理，系统会发出警告但不阻止启动。

#### 警告 1: HOST=0.0.0.0

```python
settings = DefaultSettings(
    DEBUG=False,
    HOST="0.0.0.0",  # ⚠️  触发警告
    SECRET_KEY="a" * 32,
    DB_PASSWORD="ValidPassword123"
)
# UserWarning: 生产环境使用 HOST=0.0.0.0 可能存在安全风险，
#              建议使用具体的 IP 地址或域名
```

**建议：**
- 使用具体的内网 IP（如 `10.0.0.1`）
- 使用域名
- 通过反向代理（Nginx）暴露服务

#### 警告 2: PostgreSQL 使用 localhost

```python
settings = DefaultSettings(
    DEBUG=False,
    DB_TYPE="postgres",
    DB_HOST="localhost",  # ⚠️  触发警告
    SECRET_KEY="a" * 32,
    DB_PASSWORD="ValidPassword123"
)
# UserWarning: 生产环境数据库使用 localhost 可能配置错误，
#              请确认数据库连接配置是否正确
```

**原因：**
- 生产环境通常使用独立的数据库服务器
- localhost 可能表示配置未更新

#### 警告 3: 使用默认项目名

```python
settings = DefaultSettings(
    DEBUG=False,
    PROJECT_NAME="Faster APP",  # ⚠️  触发警告（默认值）
    SECRET_KEY="a" * 32,
    DB_PASSWORD="ValidPassword123"
)
# UserWarning: 建议在生产环境修改 PROJECT_NAME 为实际项目名称
```

## 验证时机

### 1. 应用启动时

配置在应用启动时自动验证：

```python
from faster_app.settings.discover import SettingsDiscover

# 自动执行所有验证
settings = SettingsDiscover().merge()

# 如果验证失败，抛出 ValidationError 阻止启动
```

### 2. 手动创建实例时

```python
from faster_app.settings.builtins.settings import DefaultSettings
from pydantic import ValidationError

try:
    settings = DefaultSettings(
        DEBUG=False,
        SECRET_KEY="short"  # 不满足要求
    )
except ValidationError as e:
    print("配置错误:", e.errors())
    # 处理错误...
```

## 错误处理

### ValidationError 结构

```python
try:
    settings = DefaultSettings(
        DEBUG=False,
        PORT=70000,
        SECRET_KEY="short",
        DB_PASSWORD="weak"
    )
except ValidationError as e:
    for error in e.errors():
        print(f"字段: {error['loc']}")
        print(f"类型: {error['type']}")
        print(f"消息: {error['msg']}")
```

输出：

```
字段: ('PORT',)
类型: value_error
消息: PORT 必须在 1-65535 之间，当前值: 70000

字段: ('SECRET_KEY',)
类型: value_error
消息: 生产环境 SECRET_KEY 长度必须至少 32 个字符，当前长度: 5

字段: ('DB_PASSWORD',)
类型: value_error
消息: 生产环境不能使用弱密码 'weak'！请通过环境变量 DB_PASSWORD 设置强密码
```

## 最佳实践

### ✅ 推荐的生产环境配置

```bash
# .env.production
DEBUG=false
PROJECT_NAME=My Production App

# 服务器配置
HOST=10.0.0.1
PORT=8000

# JWT 配置（至少 32 字符）
SECRET_KEY=my-super-secret-production-key-with-at-least-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 数据库配置
DB_TYPE=postgres
DB_HOST=db.production.com
DB_PORT=5432
DB_USER=prod_user
DB_PASSWORD=Str0ng!Pr0duction@P@ssw0rd  # 至少 8 字符，避免弱密码
DB_DATABASE=production_db

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=STRING
```

### ❌ 避免的配置

```bash
# ❌ 不要在生产环境这样配置
DEBUG=true                              # 生产环境必须关闭
HOST=0.0.0.0                           # 安全风险
SECRET_KEY=default-key                  # 太短且是默认值
DB_PASSWORD=postgres                    # 弱密码
DB_HOST=localhost                       # 可能配置错误
ACCESS_TOKEN_EXPIRE_MINUTES=2          # 过短
PORT=99999                              # 超出范围
LOG_LEVEL=TRACE                         # 无效值
```

## 配置检查清单

### 部署前检查

- [ ] `DEBUG` 设置为 `false`
- [ ] `SECRET_KEY` 长度至少 32 字符，且不是默认值
- [ ] `DB_PASSWORD` 长度至少 8 字符，且不在弱密码列表
- [ ] `HOST` 不是 `0.0.0.0`（或通过反向代理）
- [ ] `DB_HOST` 不是 `localhost`（如果使用远程数据库）
- [ ] `PROJECT_NAME` 修改为实际项目名称
- [ ] `PORT` 和 `DB_PORT` 在有效范围内
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` 合理（5-1440 分钟）
- [ ] `LOG_LEVEL` 设置为 `INFO` 或更高
- [ ] `ALGORITHM` 使用安全的算法

### 环境变量检查

```bash
# 检查关键环境变量是否设置
echo $DEBUG                              # 应该是 false
echo $SECRET_KEY | wc -c                # 应该 ≥ 32
echo $DB_PASSWORD | wc -c               # 应该 ≥ 8
```

## 自定义验证

如果需要添加自定义验证规则，可以在 `config/settings.py` 中继承 `DefaultSettings`：

```python
from faster_app.settings.builtins.settings import DefaultSettings
from pydantic import field_validator, model_validator

class Settings(DefaultSettings):
    """自定义配置"""
    
    # 添加新字段
    CUSTOM_FIELD: str = "default"
    
    @field_validator("CUSTOM_FIELD")
    @classmethod
    def validate_custom_field(cls, v, info):
        """自定义字段验证"""
        debug_mode = info.data.get("DEBUG", True)
        
        if not debug_mode and v == "default":
            raise ValueError("生产环境必须修改 CUSTOM_FIELD")
        
        return v
    
    @model_validator(mode="after")
    def validate_custom_logic(self):
        """自定义跨字段验证"""
        # 添加您的验证逻辑
        return self
```

## 常见问题

### Q: 为什么开发环境不强制密码要求？

A: 为了便于本地开发和测试。开发环境（`DEBUG=True`）允许使用弱密码和默认配置，但生产环境（`DEBUG=False`）会严格验证。

### Q: 警告会阻止应用启动吗？

A: 不会。警告只是提醒潜在问题，但不会阻止启动。如果需要将警告升级为错误，可以在 `model_validator` 中使用 `raise ValueError` 而不是 `warnings.warn`。

### Q: 如何关闭某个警告？

A: 使用 Python 的 warnings 过滤器：

```python
import warnings

# 忽略特定警告
warnings.filterwarnings("ignore", message=".*HOST=0.0.0.0.*")

# 或者在代码中
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    settings = DefaultSettings(...)
```

### Q: 验证失败如何调试？

A: ValidationError 提供了详细的错误信息：

```python
from pydantic import ValidationError

try:
    settings = DefaultSettings(...)
except ValidationError as e:
    # 打印友好的错误消息
    print(e)
    
    # 获取结构化错误
    for error in e.errors():
        print(f"字段: {'.'.join(str(x) for x in error['loc'])}")
        print(f"错误: {error['msg']}")
        print(f"输入: {error['input']}")
```

### Q: 可以动态调整验证规则吗？

A: 可以。验证规则是在类定义时确定的，但可以通过继承和覆盖来调整：

```python
class RelaxedSettings(DefaultSettings):
    """放宽某些验证规则"""
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key_in_production(cls, v, info):
        """覆盖父类的验证，放宽要求"""
        debug_mode = info.data.get("DEBUG", True)
        secret_value = v.get_secret_value() if isinstance(v, SecretStr) else str(v)
        
        if not debug_mode and len(secret_value) < 16:  # 放宽到 16 字符
            raise ValueError("密钥至少需要 16 字符")
        
        return v
```

## 安全建议

### 1. 使用环境变量

**永远不要**在代码中硬编码敏感信息：

```python
# ❌ 错误做法
class Settings(DefaultSettings):
    SECRET_KEY: SecretStr = SecretStr("my-production-key")  # 硬编码

# ✅ 正确做法
# 在 .env 文件或系统环境变量中设置
# SECRET_KEY=my-production-key
```

### 2. 使用密钥管理服务

对于生产环境，建议使用专业的密钥管理服务：
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Google Secret Manager

### 3. 定期轮换密钥

```bash
# 生成强随机密钥
openssl rand -hex 32

# 或使用 Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. 最小权限原则

数据库用户应该只有必要的权限：

```sql
-- ✅ 只授予应用需要的权限
GRANT SELECT, INSERT, UPDATE, DELETE ON database.* TO 'app_user'@'%';

-- ❌ 不要授予过多权限
GRANT ALL PRIVILEGES ON *.* TO 'app_user'@'%';  -- 危险！
```

## 监控和审计

建议在应用启动时记录配置状态（不包含敏感信息）：

```python
import logging

logger = logging.getLogger(__name__)

def log_config_status(settings):
    """记录配置状态（安全的）"""
    logger.info("配置加载完成:")
    logger.info(f"  DEBUG: {settings.DEBUG}")
    logger.info(f"  HOST: {settings.HOST}")
    logger.info(f"  PORT: {settings.PORT}")
    logger.info(f"  DB_TYPE: {settings.DB_TYPE}")
    logger.info(f"  DB_HOST: {settings.DB_HOST}")
    logger.info(f"  LOG_LEVEL: {settings.LOG_LEVEL}")
    # 不要记录 SECRET_KEY 和 DB_PASSWORD
```

## 总结

Faster APP 的生产环境配置验证提供了多层防护：

1. **字段级验证** - 即时检查单个字段的有效性
2. **模型级验证** - 跨字段的复杂验证逻辑
3. **警告机制** - 提醒潜在问题但不阻止启动
4. **清晰的错误消息** - 准确指出配置问题和修复建议

这些验证机制帮助您在部署前发现配置问题，提高应用的安全性和稳定性。

