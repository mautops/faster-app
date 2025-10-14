# 自动发现机制

Faster APP 的核心特性之一是**自动发现机制**，它能够自动扫描并注册项目中的各种组件，实现真正的"约定优于配置"。

## 🎯 设计理念

!!! quote "核心思想"
**开发者只需要按照约定编写代码，框架会自动完成组件的发现和注册，无需手动配置。**

这消除了传统 FastAPI 项目中大量的样板代码，让你专注于业务逻辑。

## 🔍 支持的组件类型

Faster APP 支持以下组件的自动发现：

| 组件类型   | 扫描路径           | 识别条件              | 注册目标     |
| ---------- | ------------------ | --------------------- | ------------ |
| **路由**   | `apps/*/*.py`      | `APIRouter` 实例      | FastAPI 应用 |
| **模型**   | `apps/*/models.py` | `tortoise.Model` 子类 | Tortoise ORM |
| **命令**   | `apps/*/*.py`      | `BaseCommand` 子类    | Fire CLI     |
| **中间件** | `middleware/*.py`  | `BaseMiddleware` 子类 | FastAPI 应用 |
| **配置**   | `config/*.py`      | `BaseSettings` 子类   | 全局配置     |

## 🛣️ 路由自动发现

### 工作原理

1. **扫描阶段**：递归扫描 `apps/` 目录下的所有 Python 文件
2. **识别阶段**：查找 `fastapi.APIRouter` 类型的实例变量
3. **注册阶段**：将找到的路由器注册到 FastAPI 应用

### 示例代码

```python
# apps/users/routes.py
from fastapi import APIRouter

# 创建路由器 - 会被自动发现
router = APIRouter(prefix="/users", tags=["用户"])

@router.get("")
async def list_users():
    """获取用户列表"""
    return {"users": []}

@router.post("")
async def create_user(name: str):
    """创建用户"""
    return {"user": {"name": name}}
```

### 命名约定

!!! tip "路由器变量名" - **推荐**：使用 `router` 作为变量名 - **支持**：任何变量名都可以，只要类型是 `APIRouter` - **多个路由器**：同一文件中可以定义多个路由器

### 路由前缀最佳实践

```python
# ✅ 推荐：使用路由前缀
router = APIRouter(prefix="/users", tags=["用户"])

@router.get("")  # 对应 /users
@router.get("/{id}")  # 对应 /users/{id}
```

```python
# ❌ 不推荐：完整路径
router = APIRouter(tags=["用户"])

@router.get("/users")
@router.get("/users/{id}")
```

## 📊 模型自动发现

### 工作原理

1. **扫描阶段**：扫描 `apps/*/models.py` 文件
2. **识别阶段**：查找 `tortoise.models.Model` 的子类
3. **注册阶段**：将模型注册到 Tortoise ORM 配置

### 示例代码

```python
# apps/users/models.py
from faster_app.models.base import UUIDModel, DateTimeModel
from tortoise import fields

# 会被自动发现并注册
class User(UUIDModel, DateTimeModel):
    """用户模型"""

    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "users"
        indexes = [("username",), ("email",)]

class UserProfile(UUIDModel, DateTimeModel):
    """用户资料"""

    user = fields.OneToOneField("models.User", related_name="profile")
    nickname = fields.CharField(max_length=50, null=True)
    avatar = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "user_profiles"
```

### 注意事项

!!! warning "文件命名要求" - 模型必须定义在 `models.py` 文件中 - 文件必须位于 `apps/` 目录的子目录下 - 不支持其他文件名（如 `model.py`）

!!! info "抽象模型"
`python
    class BaseModel(Model):
        class Meta:
            abstract = True  # 不会被注册
    `

## ⚡ 命令自动发现

### 工作原理

1. **扫描阶段**：递归扫描 `apps/` 目录下的所有 Python 文件
2. **识别阶段**：查找 `BaseCommand` 的子类
3. **注册阶段**：将命令类注册到 Fire CLI

### 示例代码

```python
# apps/users/commands.py
from faster_app.commands.base import BaseCommand
from .models import User

# 会被自动发现，注册为 "user" 命令组
class UserCommand(BaseCommand):
    """用户管理命令"""

    async def create_admin(self, username: str, email: str):
        """创建管理员账号"""
        user = await User.create(
            username=username,
            email=email,
            is_staff=True
        )
        print(f"✅ 管理员 {username} 创建成功")

    async def count(self):
        """统计用户数量"""
        total = await User.all().count()
        active = await User.filter(is_active=True).count()
        print(f"总用户数: {total}, 活跃用户: {active}")
```

### 使用命令

```bash
# 命令格式: faster <命令组> <方法> [参数]
faster user create_admin --username=admin --email=admin@example.com
faster user count
```

### 命名规则

命令组名称自动从类名推导：

- `UserCommand` → `user`
- `ArticleCommand` → `article`
- `UserProfileCommand` → `user_profile`

规则：移除 `Command` 后缀，转为小写蛇形命名。

## 🔧 中间件自动发现

### 工作原理

1. **扫描阶段**：扫描 `middleware/` 目录下的所有 Python 文件
2. **识别阶段**：查找 `BaseMiddleware` 的子类
3. **注册阶段**：按优先级将中间件注册到 FastAPI 应用

### 示例代码

```python
# middleware/auth.py
from faster_app.middleware.base import BaseMiddleware
from fastapi import Request

class AuthMiddleware(BaseMiddleware):
    """认证中间件"""

    # 优先级：数字越小越先执行
    priority = 100

    async def __call__(self, request: Request, call_next):
        # 前置处理
        token = request.headers.get("Authorization")
        if token:
            request.state.user = await self.get_user(token)

        # 调用下一个中间件/路由
        response = await call_next(request)

        # 后置处理
        response.headers["X-Custom-Header"] = "value"

        return response
```

### 优先级控制

```python
class CorsMiddleware(BaseMiddleware):
    priority = 1  # 最先执行

class AuthMiddleware(BaseMiddleware):
    priority = 100  # 之后执行

class LoggingMiddleware(BaseMiddleware):
    priority = 999  # 最后执行
```

执行顺序：CORS → Auth → Logging → 路由 → Logging → Auth → CORS

## ⚙️ 配置自动发现

### 工作原理

1. **扫描阶段**：扫描 `config/` 目录下的所有 Python 文件
2. **识别阶段**：查找 `BaseSettings` 的子类
3. **合并阶段**：自动合并所有配置类

### 示例代码

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
    CELERY_BROKER: str = "redis://localhost:6379/1"
```

### 使用配置

```python
from faster_app.settings.config import get_settings

settings = get_settings()

print(settings.APP_NAME)  # "My App"
print(settings.DEBUG)     # 继承自内置配置
```

### 配置优先级

1. **环境变量** (最高优先级)
2. **.env 文件**
3. **自定义配置类**
4. **内置默认配置** (最低优先级)

## 🚀 扩展点

### 自定义发现器

如果你需要自定义发现逻辑，可以扩展发现器：

```python
# faster_app/utils/discover.py
from typing import Any
import importlib
import pkgutil

def discover_components(
    base_path: str,
    base_class: type,
    recursive: bool = True
) -> list[Any]:
    """通用组件发现器"""
    components = []

    # 自定义扫描逻辑
    # ...

    return components
```

## 📝 最佳实践

### 1. 遵循命名约定

```python
# ✅ 推荐
apps/users/models.py      # 模型文件
apps/users/routes.py      # 路由文件
apps/users/commands.py    # 命令文件

# ❌ 不推荐
apps/users/user_models.py
apps/users/api.py
apps/users/cmd.py
```

### 2. 保持文件职责单一

```python
# ✅ 推荐：一个文件一个路由器
# apps/users/routes.py
router = APIRouter(prefix="/users", tags=["用户"])

# ❌ 不推荐：一个文件多个不相关的路由器
router1 = APIRouter(prefix="/users")
router2 = APIRouter(prefix="/posts")  # 应该在独立文件
```

### 3. 使用显式配置

对于复杂的场景，可以覆盖自动发现：

```python
# main.py
from faster_app.app import create_app

app = create_app()

# 手动注册额外路由
from my_custom_package import custom_router
app.include_router(custom_router)
```

## 🐛 调试自动发现

### 查看已注册组件

```python
from faster_app.utils.discover import (
    discover_routes,
    discover_models,
    discover_commands
)

# 查看发现的路由
routes = discover_routes("apps")
print(f"发现 {len(routes)} 个路由器")

# 查看发现的模型
models = discover_models("apps")
print(f"发现 {len(models)} 个模型")
```

### 启用调试日志

```bash
# .env
LOG_LEVEL=DEBUG
```

查看启动日志：

```
DEBUG: Discovered router: apps.users.routes.router
DEBUG: Discovered model: apps.users.models.User
DEBUG: Discovered command: apps.users.commands.UserCommand
```

## 下一步

- 了解 [模型基类](models.md)
- 学习 [路由管理](routes.md)
- 掌握 [命令行工具](cli.md)
