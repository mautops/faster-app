---
name: faster-app-cn
description: "基于 Django 风格约定的 FastAPI 框架，用于构建生产级 API。使用此 Skill 当用户需要：(1) 创建或开发 FastAPI Web API 项目，(2) 使用 ViewSet（类似 Django REST Framework）实现 CRUD 操作，(3) 配置路由/模型/命令的自动发现系统，(4) 设置中间件、认证、权限、限流、缓存，(5) 定义 Tortoise ORM 模型和数据库关系，(6) 管理应用配置和多环境部署，(7) 从其他框架（FastAPI/DRF）迁移到 Faster APP，(8) 排查 Faster APP 相关错误，(9) 需要遵循约定优于配置原则的标准化项目结构。"
---

# Faster APP 框架使用指南

Faster APP 是遵循"约定优于配置"原则的 FastAPI 框架，采用 Django 风格的项目结构和自动发现机制。

## 核心工作流

### 1. 项目初始化

```bash
# 安装
uv add faster-app

# 创建演示应用
faster app demo

# 启动服务
faster server start
```

访问 `http://localhost:8000/docs` 查看 API 文档。

### 2. 开发 API 的标准流程

1. **定义模型** → 在 `apps/your_app/models.py` 创建数据模型
2. **创建 Schema** → 定义 Pydantic 请求/响应模型
3. **实现 ViewSet** → 使用 ModelViewSet 快速构建 CRUD
4. **数据库迁移** → `faster db migrate` 和 `faster db upgrade`
5. **测试 API** → 访问 `/docs` 测试接口

### 3. 自动发现机制

框架自动扫描并注册：

- **路由**：`apps/*/routes.py` 中的 `APIRouter` 实例
- **模型**：`apps/*/models.py` 中的 Tortoise 模型
- **命令**：`apps/*/commands.py` 中的自定义命令
- **中间件**：根据配置自动应用

## 何时加载参考文档

根据用户的具体需求，按需加载以下参考文档：

### ViewSet 开发（构建 API）

**何时使用**：用户需要创建 REST API、实现 CRUD 操作

- **[basics.md](references/viewset/basics.md)** - ViewSet 基础概念、Mixins 和自定义操作
- **[security.md](references/viewset/security.md)** - 认证、权限和速率限制
- **[data.md](references/viewset/data.md)** - 数据过滤、搜索、排序、分页和缓存

### Model 开发（数据建模）

**何时使用**：用户需要定义数据模型、设置数据库关系、编写查询

- **[basics.md](references/model/basics.md)** - 基础模型、字段类型和数据库关系
- **[queries.md](references/model/queries.md)** - 查询操作和常见模式

### Config 配置（环境和部署）

**何时使用**：用户需要配置应用、设置中间件、准备生产部署

- **[guide.md](references/config/guide.md)** - 完整配置指南，包含基础配置、中间件、日志、生产环境和高级配置

### 辅助资源（快速参考和问题解决）

**何时使用**：根据用户的具体情况选择

- **[QUICKREF.md](references/QUICKREF.md)** - 快速参考和常见问题
- **[EXAMPLES.md](references/EXAMPLES.md)** - 需要完整项目示例
- **[TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)** - 诊断错误和性能问题
- **[MIGRATION.md](references/MIGRATION.md)** - 从其他框架迁移

## 使用原则

1. **渐进式加载**：只加载用户当前任务所需的文档，避免一次性加载所有内容
2. **优先简洁**：先提供简要答案，如需详细信息再加载对应文档
3. **按需深入**：从基础文档开始，根据用户需求逐步加载高级主题

## 快速参考

### 核心概念

- **ViewSet**：类似 DRF 的 CRUD API 构建方式
- **自动发现**：约定目录结构，自动注册路由/模型/命令
- **模型基类**：UUIDModel、DateTimeModel、EnumModel、ScopeModel
- **配置管理**：基于 Pydantic 的扁平化配置，支持环境变量

### 常见任务快速指引

| 任务          | 加载文档                         |
| ------------- | -------------------------------- |
| 创建 CRUD API | viewset/basics.md                |
| 添加认证      | viewset/security.md              |
| 定义模型关系  | model/basics.md                  |
| 数据查询      | model/queries.md                 |
| 配置中间件    | config/guide.md                  |
| 配置生产环境  | config/guide.md                  |
| 多环境部署    | config/guide.md                  |
| 解决错误      | QUICKREF.md → TROUBLESHOOTING.md |
| 快速查代码    | QUICKREF.md                      |
| 迁移项目      | MIGRATION.md                     |

## 最佳实践

1. **项目结构**：按功能组织应用，每个应用专注单一职责
2. **模型设计**：使用 UUIDModel + DateTimeModel 作为基类
3. **API 开发**：优先使用 ViewSet 而非手写路由
4. **配置管理**：使用扁平化配置，不硬编码
5. **安全性**：生产环境必须修改 SECRET_KEY，设置 DEBUG=false
6. **数据库**：每次模型变更后创建迁移
7. **测试**：开发时 DEBUG=true，生产环境 DEBUG=false

---

**记住**：此 Skill 的文档采用渐进式披露模式。根据用户的具体需求，只加载相关的参考文档，保持上下文高效利用。
