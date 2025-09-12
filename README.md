# Faster APP

一个轻量级、高性能的 Python Web 框架，基于 FastAPI 和 Tortoise ORM 构建，提供自动发现、模型基类、命令行工具等企业级功能。

## ✨ 核心特性

- 🔍 **智能自动发现**: 自动扫描和加载模块、模型、路由和命令
- 🗄️ **丰富模型基类**: 基于 Tortoise ORM 的企业级模型基类
- 🛠️ **强大命令行工具**: 基于 Fire 的异步命令行工具框架
- 🌐 **统一路由管理**: FastAPI 路由的标准化返回格式
- 📦 **即插即用**: 模块化设计，开箱即用
- ⚡ **高性能**: 异步架构，支持高并发
- 🔧 **开发友好**: 内置数据库迁移、开发服务器等工具

## 🚀 快速安装

```bash
pip install faster_app
```

# 📖 快速开始

## 1. 项目结构

```
your-project/
├── apps/                    # 应用目录
│   ├── auth/
│   │   ├── models.py       # 模型定义
│   │   ├── routes.py       # 路由定义
│   │   └── commands.py     # 命令定义
│   └── user/
│       ├── models.py
│       ├── routes.py
│       └── commands.py
├── config/
└──── settings.py           # 配置文件
```

### 2. 模型定义

```python
# models.py
from faster_app.models import UUIDModel, DateTimeModel, StatusModel
from tortoise import fields

class User(UUIDModel, DateTimeModel, StatusModel):
    """用户模型"""
    name = fields.CharField(max_length=50, description="用户名")
    email = fields.CharField(max_length=100, unique=True, description="邮箱")

    class Meta:
        table = "users"
        table_description = "用户表"
```

### 3. 路由定义

```python
# routes.py
from fastapi import APIRouter
from faster_app.routes import ApiResponse

router = APIRouter(prefix="/api/v1/users", tags=["用户管理"])

@router.get("/", response_model=ApiResponse)
async def get_users():
    """获取用户列表"""
    users = await User.all()
    return ApiResponse(
        message="获取用户列表成功",
        data={"users": users, "total": len(users)}
    )

@router.post("/", response_model=ApiResponse)
async def create_user(name: str, email: str):
    """创建用户"""
    user = await User.create(name=name, email=email)
    return ApiResponse(
        message="用户创建成功",
        data={"user": user}
    )
```

### 4. 命令定义

```python
# commands.py
from faster_app.commands import BaseCommand

class UserCommand(BaseCommand):
    """用户管理命令"""

    async def create_user(self, name: str, email: str):
        """创建用户"""
        user = await User.create(name=name, email=email)
        print(f"✅ 用户创建成功: {user.name} ({user.email})")

    async def list_users(self):
        """列出所有用户"""
        users = await User.all()
        print(f"📋 共找到 {len(users)} 个用户:")
        for user in users:
            print(f"  - {user.name} ({user.email})")
```

# 🛠️ 内置工具

### 1. 数据库管理

```bash
# 初始化数据库
python main.py db init_db

# 生成迁移文件
python main.py db migrate

# 执行迁移
python main.py db upgrade

# 回滚迁移
python main.py db downgrade

# 查看迁移历史
python main.py db history

# 清理开发环境
python main.py db dev_clean
```

### 2. 开发服务器

```bash
# 启动开发服务器
python main.py fastapi start

# 指定主机和端口
python main.py fastapi start --host=0.0.0.0 --port=8080
```

# ⚙️ 配置管理

> 默认配置，可以通过

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = ""
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # API 配置
    API_V1_STR: str = "/api/v1"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库配置
    DB_ENGINE: str = "tortoise.backends.asyncpg"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_DATABASE: str = "mydb"
```

### 环境变量支持

创建 `.env` 文件：

```env
PROJECT_NAME=My API Project
DEBUG=true
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_DATABASE=mydb
SECRET_KEY=your-secret-key-here
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 报告问题

如果您发现了 bug 或有功能建议，请在 [Issues](https://github.com/your-org/faster_app/issues) 中提交。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [Tortoise ORM](https://tortoise.github.io/) - 异步 ORM 框架
- [Fire](https://github.com/google/python-fire) - 命令行接口生成器
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库
- [Rich](https://rich.readthedocs.io/) - 终端美化库

**作者**: peizhenfei (peizhenfei@hotmail.com)

**项目主页**: [https://github.com/mautops/faster-app.git](https://github.com/mautops/faster-app.git)
