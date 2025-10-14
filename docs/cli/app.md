# App 命令参考

`faster app` 命令组用于快速创建项目结构和配置文件。

## 命令列表

| 命令         | 说明             | 使用频率   |
| ------------ | ---------------- | ---------- |
| `demo`       | 创建示例应用     | ⭐⭐⭐⭐⭐ |
| `config`     | 创建配置目录     | ⭐⭐⭐⭐   |
| `env`        | 创建环境变量文件 | ⭐⭐⭐⭐⭐ |
| `main`       | 创建主入口文件   | ⭐⭐⭐     |
| `middleware` | 创建中间件目录   | ⭐⭐⭐     |
| `docker`     | 创建 Docker 配置 | ⭐⭐⭐     |

## faster app demo

创建示例应用模块，包含完整的 CRUD 示例。

**语法**：

```bash
faster app demo
```

**生成文件**：

```
apps/demo/
├── __init__.py
├── models.py      # 数据模型示例
├── routes.py      # API 路由示例
├── schemas.py     # Pydantic 模型示例
├── commands.py    # 命令行工具示例
└── tasks.py       # 异步任务示例
```

**使用场景**：

- 项目初始化时快速搭建骨架
- 学习 Faster APP 的标准结构
- 作为新模块的模板

## faster app config

创建自定义配置目录。

**语法**：

```bash
faster app config
```

**生成文件**：

```
config/
├── __init__.py
└── settings.py    # 配置模板
```

**使用场景**：

- 需要自定义应用配置
- 添加第三方服务配置
- 覆盖默认配置

## faster app env

创建环境变量配置文件。

**语法**：

```bash
faster app env
```

**生成文件**：

```
.env
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

**使用场景**：

- 项目初始化
- 配置数据库连接
- 设置环境特定的参数

更多详细内容...
