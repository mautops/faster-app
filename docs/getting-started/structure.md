# 项目结构

Faster APP 采用约定优于配置的理念，为 FastAPI 项目定义了一套标准化的目录结构。

## 完整项目结构

```
your-project/
├── apps/                      # 应用目录（核心）
│   ├── users/                # 用户模块
│   │   ├── __init__.py
│   │   ├── models.py         # 数据模型
│   │   ├── routes.py         # API 路由
│   │   ├── schemas.py        # Pydantic 模型
│   │   ├── commands.py       # 命令行工具
│   │   ├── tasks.py          # 异步任务
│   │   └── utils.py          # 工具函数
│   ├── posts/                # 文章模块
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── ...
│   └── ...                   # 更多应用模块
├── config/                    # 配置目录
│   ├── __init__.py
│   └── settings.py           # 自定义配置
├── middleware/                # 中间件目录
│   ├── __init__.py
│   └── auth.py               # 认证中间件
├── migrations/                # 数据库迁移
│   └── models/
│       └── 0_*.py            # 迁移文件
├── .env                       # 环境变量
├── .env.example              # 环境变量示例
├── main.py                   # 自定义入口（可选）
├── pyproject.toml            # 项目配置
└── README.md
```

## 核心目录说明

### `apps/` - 应用目录

这是项目的核心，所有业务逻辑都组织在这里。每个子目录代表一个功能模块（类似 Django 的 app）。

#### 标准模块结构

每个应用模块遵循统一的文件组织：

```
apps/users/
├── __init__.py         # 模块初始化
├── models.py          # 数据模型（Tortoise ORM）
├── routes.py          # API 路由（FastAPI Router）
├── schemas.py         # 数据验证模型（Pydantic）
├── commands.py        # 命令行工具
├── tasks.py           # 异步任务
└── utils.py           # 工具函数
```

#### 各文件职责

##### `models.py` - 数据模型

定义数据库模型，使用 Tortoise ORM：

```python
from faster_app.models.base import UUIDModel, DateTimeModel

class User(UUIDModel, DateTimeModel):
    """用户模型"""
    username: str = Field(..., max_length=50)
    email: str = Field(..., max_length=100)

    class Meta:
        table = "users"
```

!!! tip "自动发现"
所有继承自 `tortoise.Model` 的类会被自动发现并注册。

##### `routes.py` - API 路由

定义 HTTP 接口：

```python
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["用户"])

@router.get("")
async def list_users():
    """获取用户列表"""
    return {"users": []}
```

!!! tip "自动注册"
所有 `APIRouter` 实例会被自动发现并注册到 FastAPI 应用。

##### `schemas.py` - 数据验证

定义请求和响应的数据结构：

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """创建用户请求"""
    username: str
    email: EmailStr

class UserResponse(BaseModel):
    """用户响应"""
    id: str
    username: str
    email: str
```

##### `commands.py` - 命令行工具

定义自定义命令：

```python
from faster_app.commands.base import BaseCommand

class UserCommand(BaseCommand):
    """用户管理命令"""

    async def create_admin(self):
        """创建管理员"""
        pass
```

!!! tip "自动注册"
所有 `BaseCommand` 子类会被自动注册为命令。

##### `tasks.py` - 异步任务

定义后台任务：

```python
async def send_welcome_email(user_id: str):
    """发送欢迎邮件"""
    pass
```

##### `utils.py` - 工具函数

模块内部使用的工具函数：

```python
def hash_password(password: str) -> str:
    """密码哈希"""
    pass
```

### `config/` - 配置目录

存放自定义配置：

```python
# config/settings.py
from faster_app.settings.config import BaseSettings

class CustomSettings(BaseSettings):
    """自定义配置"""
    APP_NAME: str = "My App"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
```

!!! tip "自动合并"
所有 `BaseSettings` 子类会被自动发现并合并到全局配置。

### `middleware/` - 中间件目录

存放自定义中间件：

```python
# middleware/auth.py
from faster_app.middleware.base import BaseMiddleware

class AuthMiddleware(BaseMiddleware):
    """认证中间件"""

    async def __call__(self, request, call_next):
        # 中间件逻辑
        response = await call_next(request)
        return response
```

### `migrations/` - 数据库迁移

由 Aerich 自动生成和管理：

```
migrations/
├── models/
│   ├── 0_20240101000000_init.py
│   └── 1_20240102000000_add_user_table.py
└── pyproject.toml
```

!!! warning "注意"
不要手动修改迁移文件，除非你知道自己在做什么。

## 配置文件

### `.env` - 环境变量

存放敏感配置和环境相关配置：

```bash
# 应用配置
DEBUG=True
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=postgres://user:pass@localhost/db

# 日志配置
LOG_LEVEL=INFO
```

### `pyproject.toml` - 项目配置

Python 项目的标准配置文件：

```toml
[project]
name = "my-app"
version = "0.1.0"
dependencies = [
    "faster-app",
]

[dependency-groups]
dev = [
    "mkdocs-material",
    "ruff",
]
```

### `main.py` - 自定义入口（可选）

如果需要自定义 FastAPI 应用，可以创建此文件：

```python
from faster_app.app import create_app

# 获取应用实例
app = create_app()

# 自定义中间件
@app.middleware("http")
async def custom_middleware(request, call_next):
    response = await call_next(request)
    return response
```

!!! tip "优先级"
如果存在 `main.py`，`faster server start` 会优先使用它。

## 目录创建命令

Faster APP 提供了命令快速创建这些目录：

```bash
faster app demo        # 创建示例应用
faster app config      # 创建配置目录
faster app middleware  # 创建中间件目录
faster app env         # 创建 .env 文件
faster app main        # 创建 main.py 模板
```

## 最佳实践

### 1. 模块化组织

将相关功能组织在同一个应用模块下：

```
apps/
├── auth/          # 认证相关
├── users/         # 用户管理
├── posts/         # 文章管理
└── comments/      # 评论管理
```

### 2. 保持模块独立

每个模块应该尽可能独立，避免循环依赖。

### 3. 使用命名约定

- 模块名：小写，使用下划线（如 `user_profile`）
- 模型名：帕斯卡命名（如 `UserProfile`）
- 路由前缀：小写，使用连字符（如 `/user-profiles`）

### 4. 合理划分粒度

- 小型项目：少量模块，功能集中
- 大型项目：细粒度模块，职责单一

## 下一步

- 了解 [自动发现机制](../features/auto-discovery.md)
- 学习 [模型基类](../features/models.md)
- 掌握 [路由管理](../features/routes.md)
