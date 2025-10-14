# 命令行工具

Faster APP 提供了完整的 Django 风格命令行工具，基于 [Fire](https://github.com/google/python-fire) 库实现。

## 🎯 命令概览

| 命令组          | 说明       | 主要功能               |
| --------------- | ---------- | ---------------------- |
| `faster app`    | 应用管理   | 创建项目结构、配置文件 |
| `faster db`     | 数据库管理 | 迁移、初始化、回滚     |
| `faster server` | 服务器管理 | 启动开发服务器         |

## 🏗️ App 命令

### `faster app demo`

创建示例应用模块

```bash
faster app demo
```

**输出结果**：

```
✅ apps/demo created successfully
```

**生成文件**：

```
apps/demo/
├── __init__.py
├── models.py      # 示例数据模型
├── routes.py      # 示例 API 路由
├── schemas.py     # 示例 Pydantic 模型
├── commands.py    # 示例命令
└── tasks.py       # 示例异步任务
```

### `faster app config`

创建自定义配置目录

```bash
faster app config
```

**输出结果**：

```
✅ config/ created successfully
```

**生成文件**：

```
config/
├── __init__.py
└── settings.py    # 配置模板
```

### `faster app env`

创建环境变量配置文件

```bash
faster app env
```

**输出结果**：

```
✅ .env created successfully
```

**文件内容**：

```bash
# 应用配置
DEBUG=True
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite://./faster_app.db

# 日志配置
LOG_LEVEL=INFO
```

### `faster app main`

复制框架内置的主入口文件模板

```bash
faster app main
```

**输出结果**：

```
✅ main.py created successfully
```

**使用场景**：

- 需要自定义 FastAPI 应用配置
- 添加自定义中间件或路由
- 特殊的启动逻辑或初始化代码

### `faster app middleware`

创建中间件目录

```bash
faster app middleware
```

**输出结果**：

```
✅ middleware/ created successfully
```

### `faster app docker`

创建 Docker 配置文件

```bash
faster app docker
```

**输出结果**：

```
✅ Dockerfile created successfully
```

**生成的 Dockerfile**：

- 基于多阶段构建
- 优化的镜像大小
- 包含 uv 包管理器
- 适合生产环境部署

## 🗄️ DB 命令

### `faster db init`

初始化数据库迁移配置

```bash
faster db init
```

**功能说明**：

- 创建 `migrations/` 目录
- 初始化 Aerich 配置
- 准备数据库迁移环境

**输出结果**：

```
✅ Successfully created migrations folder
```

### `faster db init_db`

初始化数据库表结构

```bash
faster db init_db
```

**功能说明**：

- 根据模型定义生成数据库表
- 创建初始迁移文件
- 适用于项目首次部署

**输出结果**：

```
✅ Database initialization successful
```

### `faster db migrate`

生成数据库迁移文件

```bash
# 自动生成迁移文件
faster db migrate

# 指定迁移名称
faster db migrate --name="add_user_table"

# 生成空迁移文件
faster db migrate --empty
```

**参数说明**：

- `--name`: 迁移文件名称（可选）
- `--empty`: 生成空迁移文件，用于手动编写 SQL

**输出结果**：

```
✅ Migration file generated successfully
migrations/models/1_20240101120000_add_user_table.py
```

### `faster db upgrade`

执行数据库迁移

```bash
faster db upgrade
```

**功能说明**：

- 执行所有未应用的迁移文件
- 支持事务回滚
- 更新数据库到最新状态

**输出结果**：

```
✅ Database migration execution successful
Applied migrations:
  - 1_20240101120000_add_user_table.py
```

### `faster db downgrade`

回滚数据库迁移

```bash
# 回滚到上一个版本
faster db downgrade

# 回滚到指定版本
faster db downgrade --version=2
```

**参数说明**：

- `--version`: 目标版本号（默认 -1，即上一版本）

**输出结果**：

```
✅ Database downgrade successful
Reverted: 1_20240101120000_add_user_table.py
```

### `faster db history`

查看迁移历史

```bash
faster db history
```

**输出示例**：

```
Migration History:
  ✓ 0_20231225100000_init.py (2023-12-25 10:00:00)
  ✓ 1_20240101120000_add_user_table.py (2024-01-01 12:00:00)
  ✓ 2_20240102080000_add_article_table.py (2024-01-02 08:00:00)
```

### `faster db heads`

查看待应用的迁移

```bash
faster db heads
```

**输出示例**：

```
Pending Migrations:
  - 3_20240103090000_add_comment_table.py
  - 4_20240104100000_add_indexes.py
```

### `faster db dev_clean`

清理开发环境数据 ⚠️

```bash
# 交互式确认
faster db dev_clean

# 强制清理
faster db dev_clean --force
```

**功能说明**：

- **仅在开发环境可用**（`DEBUG=True`）
- 删除数据库文件
- 删除迁移目录
- 用于重置开发环境

**参数说明**：

- `--force`: 跳过确认提示

!!! danger "警告"
此操作会删除所有数据，请谨慎使用！生产环境会自动禁用此命令。

## 🚀 Server 命令

### `faster server start`

启动开发服务器

```bash
faster server start
```

**功能说明**：

- 自动检测项目根目录的 `main.py`
- 优先使用用户自定义配置
- 支持热重载
- 自动应用日志、中间件、路由配置

**启动检测逻辑**：

1. **第一优先级**：检查 `main.py`
   - 存在 `app` 实例 → 使用自定义应用
   - 存在 `main()` 函数 → 执行自定义启动
2. **第二优先级**：使用框架内置配置

**配置参数**（通过 `.env`）：

```bash
HOST=0.0.0.0      # 监听地址
PORT=8000         # 监听端口
DEBUG=True        # 调试模式
```

**输出示例**：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Application startup complete.
```

## 🔧 自定义命令

Faster APP 支持自动发现和注册自定义命令。

### 创建自定义命令

```python
# apps/users/commands.py
from faster_app.commands.base import BaseCommand
from .models import User

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

    async def export(self, format: str = "json"):
        """导出用户数据"""
        users = await User.all()
        if format == "json":
            # 导出为 JSON
            pass
        elif format == "csv":
            # 导出为 CSV
            pass
```

### 使用自定义命令

```bash
# 命令格式: faster <命令组> <方法> [参数]
faster user create_admin --username=admin --email=admin@example.com
faster user count
faster user export --format=csv
```

### 命名规则

命令组名称自动从类名推导：

| 类名                 | 命令组         |
| -------------------- | -------------- |
| `UserCommand`        | `user`         |
| `ArticleCommand`     | `article`      |
| `UserProfileCommand` | `user_profile` |

规则：移除 `Command` 后缀，转为小写蛇形命名。

## 💡 使用技巧

### 查看命令帮助

```bash
# 查看所有命令
faster --help

# 查看命令组帮助
faster db --help

# 查看具体命令帮助
faster db migrate --help
```

### 开发工作流

推荐的项目初始化流程：

```bash
# 1. 创建基础结构
faster app demo          # 创建示例应用
faster app config        # 创建配置目录
faster app env           # 创建环境变量

# 2. 初始化数据库
faster db init           # 初始化迁移配置
faster db init_db        # 创建数据库表

# 3. 启动开发
faster server start      # 启动服务器
```

### 使用环境变量

通过 `.env` 文件配置：

```bash
# 先创建配置文件
faster app env

# 编辑 .env 文件
vim .env

# 再执行数据库操作
faster db init
```

## 下一步

- 查看 [CLI 完整参考](../cli/app.md)
- 了解 [自定义命令](../cli/custom.md)
- 学习 [数据库最佳实践](../best-practices/database.md)
