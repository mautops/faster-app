# 配置管理

Faster APP 提供了灵活的配置管理系统，支持环境变量、配置文件和自动发现。

## 🎯 配置优先级

配置按以下优先级加载（从高到低）：

1. **环境变量**（最高优先级）
2. **.env 文件**
3. **自定义配置类**
4. **内置默认配置**（最低优先级）

## 内置配置

Faster APP 提供了一些内置配置：

```python
class Settings(BaseSettings):
    # 应用配置
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = "sqlite://./faster_app.db"

    # 日志配置
    LOG_LEVEL: str = "INFO"
```

## 自定义配置

创建自定义配置类：

```python
# config/settings.py
from faster_app.settings.config import BaseSettings

class CustomSettings(BaseSettings):
    """自定义配置"""

    # 应用配置
    APP_NAME: str = "My App"
    APP_VERSION: str = "1.0.0"

    # 业务配置
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list[str] = [".jpg", ".png", ".pdf"]

    # 第三方服务
    REDIS_URL: str = "redis://localhost:6379/0"
```

## 使用配置

```python
from faster_app.settings.config import get_settings

settings = get_settings()

print(settings.APP_NAME)
print(settings.DEBUG)
```

更多内容请查看完整文档...
