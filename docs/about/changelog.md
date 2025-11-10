# 更新日志

本页面记录 Faster APP 的所有版本更新历史。

---

## v0.1.0 (2025-11-10) ⚠️ Breaking Changes

??? warning "v0.1.0 - 配置系统重大升级（Breaking Changes）🔧"

    ### ⚠️ Breaking Changes

    - **移除独立环境变量支持**：不再支持 `FASTER_DATABASE__*` 配置方式
    - **必须使用 DATABASE_URL**：数据库配置只能通过 `DATABASE_URL` 或 `FASTER_DATABASE_URL`
    - **简化配置结构**：`DatabaseSettings` 移除默认值，必须通过 URL 初始化

    **迁移指南**：

    ```bash
    # ❌ v0.0.x 方式（不再支持）
    export FASTER_DATABASE__TYPE=postgres
    export FASTER_DATABASE__HOST=localhost
    export FASTER_DATABASE__PORT=5432
    export FASTER_DATABASE__USER=user
    export FASTER_DATABASE__PASSWORD=pass
    export FASTER_DATABASE__DATABASE=mydb

    # ✅ v0.1.0+ 方式（必须使用）
    export DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
    # 或
    export FASTER_DATABASE_URL=postgresql://user:pass@localhost:5432/mydb
    ```

    ### 🎉 新增功能

    - 🔐 **敏感信息保护**：使用 `SecretStr` 保护敏感配置
        - 自动隐藏密码、密钥等敏感信息
        - 防止意外日志泄露
        - JSON 序列化时自动脱敏（显示 `***HIDDEN***`）
        - 支持字段：`SECRET_KEY`, `DB_PASSWORD`
        - 文档：[敏感信息保护](../features/settings-security.md)

    - 🔄 **TORTOISE_ORM 配置优化**：从 `__init__` 重构为 `@property`
        - 动态生成配置，支持运行时更新
        - 遵循 Pydantic 最佳实践
        - 根据实际数据库类型生成对应连接
        - 统一使用 `default` 连接名
        - 更好的可测试性
        - 文档：[TORTOISE_ORM 配置](../features/tortoise-orm-config.md)

    - ✅ **生产环境配置验证**：全面的安全检查机制
        - **字段级验证器**：
            - 端口号范围检查（1-65535，SQLite 除外）
            - 日志级别验证
            - JWT 算法白名单
            - Token 过期时间合理性
            - 数据库类型验证
        - **模型级验证器**（生产环境）：
            - Secret Key 安全性检查（长度 >= 32）
            - 数据库密码强度检查（长度 >= 8）
            - 数据库连接配置检查（避免 localhost）
            - 项目名称规范提醒
        - 友好的错误提示和警告
        - 文档：[生产环境验证](../features/production-validation.md)

    - 🏷️ **环境变量前缀**：统一使用 `FASTER_` 前缀
        - 避免多应用环境变量冲突
        - 更清晰的配置管理
        - 主要用于顶层配置和 DATABASE_URL
        - 文档：[环境变量前缀](../features/env-prefix.md)

    - 📦 **配置分组与嵌套**：模块化配置结构
        - **ServerSettings**：服务器配置（host, port）
        - **JWTSettings**：JWT 认证配置（secret_key, algorithm, expire_minutes）
        - **DatabaseSettings**：数据库配置（type, host, port, user, password, database, db_schema）
        - **LogSettings**：日志配置（level, format）
        - 清晰的配置组织，易于维护和扩展
        - IDE 智能提示支持
        - 文档：[配置分组](../features/config-grouping.md)

    - 🗂️ **配置文件重构**：按组拆分到独立文件
        - `faster_app/settings/groups/server.py` - 服务器配置
        - `faster_app/settings/groups/jwt.py` - JWT 配置
        - `faster_app/settings/groups/database.py` - 数据库配置（基于 DATABASE_URL）
        - `faster_app/settings/groups/log.py` - 日志配置
        - `faster_app/settings/groups/__init__.py` - 统一导出
        - 更好的代码组织和模块化
        - 文档：[配置重构](../features/config-refactoring.md)

    - 🔗 **DATABASE_URL 支持**：唯一的数据库配置方式
        - 遵循 [12-Factor App](https://12factor.net/) 最佳实践
        - 支持 PostgreSQL、MySQL、SQLite
        - 支持 `DATABASE_URL` 和 `FASTER_DATABASE_URL`
        - 自动解析连接字符串
        - 特殊字符密码自动 URL 解码
        - 云平台友好（Heroku、Railway、Render 等）
        - 未设置时自动使用 SQLite（开发环境友好）
        - 示例：
            ```bash
            # PostgreSQL
            export DATABASE_URL=postgresql://user:pass@host:5432/database

            # MySQL
            export DATABASE_URL=mysql://user:pass@host:3306/database

            # SQLite（开发环境）
            export DATABASE_URL=sqlite:///dev.db

            # 默认（未设置时）
            # 自动使用: sqlite:///faster_app.db
            ```
        - 文档：[DATABASE_URL 支持](../features/database-url.md)

    - 🏢 **数据库 Schema 支持**：多租户数据隔离
        - 通过 URL 查询参数指定 schema：`?schema=tenant_a`
        - 自动集成到 Tortoise ORM 配置
        - PostgreSQL 完全支持，SQLite 自动忽略
        - 典型场景：
            - 多租户 SaaS 应用（每个租户一个 schema）
            - 微服务数据隔离（每个服务一个 schema）
            - 环境数据隔离（dev/test/staging schema）
        - 示例：
            ```bash
            # 租户 A
            export DATABASE_URL=postgresql://app:pass@db:5432/saas?schema=tenant_a

            # 租户 B
            export DATABASE_URL=postgresql://app:pass@db:5432/saas?schema=tenant_b
            ```
        - 文档：[数据库 Schema 支持](../features/database-schema.md)

    ### 🔧 改进优化

    - 📝 **配置字段命名规范**：统一使用 `snake_case`
        - 更符合 Python 命名规范
        - 更好的可读性
        - 与 Pydantic 推荐一致

    - 🔄 **discover.py 优化**：正确处理 `SecretStr` 类型
        - 使用 `mode='python'` 保留 `SecretStr` 对象
        - 避免配置合并时的类型丢失
        - 更好的类型推断

    - 🎯 **logging.py 适配**：支持嵌套配置访问
        - 从 `configs.LOG_LEVEL` 迁移到 `configs.log.level`
        - 从 `configs.LOG_FORMAT` 迁移到 `configs.log.format`
        - 完全兼容新的配置结构

    - 🗄️ **TORTOISE_ORM 简化**：动态生成数据库连接
        - 根据实际数据库类型只生成对应连接
        - 统一使用 `default` 连接名
        - 支持 SQLite、PostgreSQL、MySQL
        - 自动处理 schema 配置

    - 📚 **配置加载简化**：清晰的配置初始化
        1. 构造函数参数（最高优先级）
        2. `FASTER_DATABASE_URL` 环境变量
        3. `DATABASE_URL` 环境变量
        4. 默认 SQLite（开发友好）

    ### 🐛 Bug 修复

    - 修复 `SecretStr` 在配置合并时的类型丢失问题
    - 修复 Pydantic 字段名冲突（`schema` → `db_schema`）
    - 修复 SQLite 端口验证逻辑（允许端口为 0）
    - 修复 `TORTOISE_ORM` 连接配置错误（KeyError: 'POSTGRES'）
    - 修复配置重构后字段访问不兼容问题
    - 修复生产环境验证的边界条件

    ### 📖 新增文档

    - ✨ [敏感信息保护](../features/settings-security.md) - SecretStr 使用指南
    - ✨ [TORTOISE_ORM 配置](../features/tortoise-orm-config.md) - 动态配置最佳实践
    - ✨ [生产环境验证](../features/production-validation.md) - 安全检查详解
    - ✨ [环境变量前缀](../features/env-prefix.md) - 前缀配置说明
    - ✨ [配置分组](../features/config-grouping.md) - 模块化配置指南
    - ✨ [配置重构](../features/config-refactoring.md) - 文件结构说明
    - ✨ [DATABASE_URL 支持](../features/database-url.md) - 完整使用指南
    - ✨ [数据库 Schema 支持](../features/database-schema.md) - 多租户架构指南
    - ✨ [迁移清单](./migration-checklist.md) - v0.0.x → v0.1.0 详细清单

    ### 💡 升级指南

    **必须操作**：

    ```bash
    # 1. 识别旧配置（如果使用独立环境变量）
    # 旧方式（不再支持）
    FASTER_DATABASE__TYPE=postgres
    FASTER_DATABASE__HOST=prod.db.com
    FASTER_DATABASE__PORT=5432
    FASTER_DATABASE__USER=appuser
    FASTER_DATABASE__PASSWORD=secret123
    FASTER_DATABASE__DATABASE=appdb
    FASTER_DATABASE__DB_SCHEMA=myschema  # 可选

    # 2. 转换为 DATABASE_URL
    # 新方式（必须使用）
    DATABASE_URL=postgresql://appuser:secret123@prod.db.com:5432/appdb?schema=myschema
    ```

    **快速转换公式**：
    ```
    DATABASE_URL={type}://{user}:{password}@{host}:{port}/{database}?schema={schema}
    ```

    ### 🎯 设计原则

    本次配置系统升级遵循以下原则：

    1. **简单第一**：移除复杂的向后兼容，只保留一种配置方式
    2. **安全第一**：敏感信息保护 + 生产环境验证
    3. **标准优先**：遵循 12-Factor App 最佳实践
    4. **模块化**：配置分组便于维护
    5. **云原生**：DATABASE_URL 简化云平台部署
    6. **文档完善**：每个功能都有详细文档

    ### 📊 影响范围

    - **配置系统**：全面简化，更清晰、更易用
    - **数据库配置**：只支持 DATABASE_URL 方式
    - **多租户支持**：Schema 支持使多租户架构更简单
    - **部署友好**：符合云平台标准，一行配置搞定
    - **开发体验**：配置分组和 IDE 提示提升开发效率
    - **维护成本**：代码更简洁，测试用例更少

    ### 🔗 相关资源

    - 📋 [完整迁移清单](./migration-checklist.md)
    - 📖 [DATABASE_URL 文档](../features/database-url.md)
    - 📖 [Schema 支持文档](../features/database-schema.md)
    - 💬 [讨论和反馈](https://github.com/mautops/faster-app/discussions)

---

## v0.0.41 (2025-10-14)

??? success "v0.0.42 - 文档站建设与设计哲学完善"

    ### 🎉 新增功能

    - ✨ **MkDocs 文档站**：完整的文档系统
        - 使用 Material for MkDocs 主题
        - 支持中文搜索和语法高亮
        - 自动生成 API 文档（mkdocstrings）
        - 日间/夜间模式切换
    - 📖 **完整文档内容**：
        - 快速开始指南（安装、快速入门、项目结构）
        - 核心功能详解（自动发现、模型基类、路由、CLI、中间件、配置）
        - 命令行工具参考
        - API 参考文档
        - 最佳实践指南
        - 贡献指南
    - 🎨 **设计哲学抽象**：六大核心设计原则
        - 约定优于配置
        - 自动发现优于手动注册
        - 组合优于继承
        - 显式优于隐式
        - 开发体验优于配置灵活性
        - 生产就绪优于演示代码

    ### 🔧 改进优化

    - 📝 在 `Makefile` 中添加文档相关命令
    - 🎯 完善项目设计理念和适用场景说明
    - 📚 添加设计灵感和框架对比

    ### 🐛 Bug 修复

    - 修复文档构建警告

---

## v0.0.37 (2025-10-13)

??? note "v0.0.37 - 枚举模型与 Docker 支持"

    ### 🎉 新增功能

    - ✨ **EnumModel 基类**：枚举字段支持
        - 支持 Python Enum 类型
        - 适用于状态机、分类等场景
        - 类型安全的枚举值
    - 🐳 **Docker 构建命令**：`make image`
        - 多阶段构建优化
        - 基于 uv 的依赖管理
        - 生产环境就绪

    ### 🔧 改进优化

    - 优化 Docker 镜像大小
    - 改进构建流程

---

## v0.0.36 (2025-10-12)

??? note "v0.0.36 - 内置中间件与后台任务"

    ### 🎉 新增功能

    - ⚡ **内置中间件系统**
        - 请求追踪中间件
        - 日志中间件
        - CORS 中间件
        - 中间件优先级控制
    - 🔄 **后台任务支持**
        - 异步任务示例
        - 任务队列集成
        - Celery 支持
    - 🔍 **路由调试规则**：改进路由发现的调试输出

    ### 🔧 改进优化

    - 禁用默认内置中间件（可选启用）
    - 优化中间件注册流程
    - 完善文档和配置说明

    ### 🐛 Bug 修复

    - 修复 runtime 文件夹打包问题
    - 添加 runtime 到 package data

---

## v0.0.35 (2025-09-30)

??? note "v0.0.35 - 统一 API 输出格式"

    ### 🎉 新增功能

    - 📤 **统一的 API 输出格式**
        - 标准化的响应结构
        - 成功/失败响应封装
        - 统一的错误处理
        - 分页数据格式化

    ### 🔧 改进优化

    - 优化响应工具函数
    - 改进错误消息格式

    ### 🐛 Bug 修复

    - 修复 demo 参数异常问题

---

## v0.0.34 (2025-09-24)

??? note "v0.0.34 - 中间件自动发现"

    ### 🎉 新增功能

    - 🔍 **中间件自动发现**
        - 扫描 `middleware/` 目录
        - 自动注册 `BaseMiddleware` 子类
        - 支持优先级排序
    - 📚 **完善文档**
        - 中间件使用文档
        - 配置说明
        - 最佳实践

    ### 🔧 改进优化

    - 移除旧中间件文件
    - 新增标准化的 `middlewares.py`
    - 优化路由发现逻辑

    ### 🐛 Bug 修复

    - 添加 asyncpg 依赖
    - 更新 demo 路由

---

## v0.0.33 (2025-09-24)

??? note "v0.0.33 - 分页功能集成"

    ### 🎉 新增功能

    - 📄 **分页支持**：集成 fastapi-pagination
        - 自动分页装饰器
        - 多种分页策略
        - 统一的分页响应格式

    ### 🔧 改进优化

    - 优化分页配置
    - 改进查询性能

    ### 🐛 Bug 修复

    - 修复找不到 apps 路径的问题
    - 修复日志配置问题

---

## v0.0.32 - v0.0.25 (2025-09-22 至 2025-09-24)

??? note "配置系统与异常处理优化"

    ### 🎉 新增功能

    - 🔧 **配置系统完善**
        - 基于 PROJECT_NAME 扫描配置文件
        - 改进 DefaultSettings 继承机制
        - 动态创建 SQLite 数据库文件
    - ⚠️ **全局异常处理**
        - 自定义异常类
        - 统一错误响应格式
        - 异常测试示例
    - 🐳 **Docker 支持**：添加 Dockerfile 和部署文档

    ### 🔧 改进优化

    - 完善 discover 相关逻辑
    - 调整 settings 结构
    - 移除统一返回格式（保持灵活性）
    - **Python 版本要求**：升级到 >= 3.12

    ### 🐛 Bug 修复

    - 修复数据库装饰器异常
    - 修复 DB 命令 BUG
    - 修复循环导入错误
    - 修复 DefaultSettings 类方法和属性继承
    - 修复 SQLite 数据库文件创建

---

## v0.0.24 - v0.0.17 (2025-09-12 至 2025-09-14)

??? note "数据库迁移与分页功能"

    ### 🎉 新增功能

    - 📄 **分页功能**：添加基础分页支持
    - 🗄️ **数据库命令改进**
        - 优化内置 DB 命令
        - 改进迁移功能
        - 添加元类支持

    ### 🔧 改进优化

    - 优化数据库迁移流程
    - 改进命令基类

    ### 🐛 Bug 修复

    - 修复 DB 迁移功能错误
    - 修复命令基类 Python path
    - 修复 FastAPI 启动时的环境变量

---

## v0.0.16 - v0.0.12 (2025-09-10 至 2025-09-12)

??? note "命令系统与配置优化"

    ### 🎉 新增功能

    - 🛠️ **命令基类优化**
        - 添加 Python path 修正
        - 元类支持
        - 改进命令注册

    ### 🔧 改进优化

    - 移除 `main.py` 到包内部
    - 优化 config 目录拷贝
    - 改进 `.env.example` 文件

    ### 🐛 Bug 修复

    - 修复 DB migrate 功能错误
    - 修复 FastAPI 启动环境变量
    - 修复配置目录拷贝问题

---

## v0.0.11 - v0.0.8 (2025-09-10)

??? note "命令行工具与项目初始化"

    ### 🎉 新增功能

    - 🚀 **faster-app 命令**：添加全局命令支持
    - 🎬 **init 子命令**：项目初始化工具
    - 📦 **main.py 集成**：移动 main.py 到包内

    ### 🔧 改进优化

    - 优化命令行工具结构
    - 改进项目初始化流程

    ### 🐛 Bug 修复

    - 修复 .env.example 问题
    - 修复命令行工具 bug

---

## v0.0.7 - v0.0.6 (2025-09-10)

??? note "应用模板系统"

    ### 🎉 新增功能

    - 🚀 **App 命令系统**
        - `faster app demo`: 创建演示应用
        - `faster app config`: 生成配置文件
        - `faster app env`: 创建环境配置
    - 📁 **模板系统**
        - Demo 应用模板（完整 MVC 结构）
        - 配置模板
        - 标准化应用结构
    - 🔧 **命令基类优化**
        - 添加 BASE_PATH 支持
        - 模板定位功能

    ### 🔧 改进优化

    - 数据库命令增强
    - 改进配置管理

    ### 💡 影响

    这些功能让开发者能够快速搭建标准化的应用结构，极大提升开发效率。

---

## v0.0.5 (2025-09-10)

??? note "v0.0.5 - 项目重命名"

    ### 🎉 重大变更

    - 🔄 **项目重命名**：Faster API → **Faster APP**
        - 更名反映项目定位（完整应用框架而非仅 API）
        - 更新所有文档和配置
        - 修正 GitHub 仓库链接

    ### 🔧 改进优化

    - 修复导入路径：使用完整的 `faster_app.settings` 路径
    - 更新配置：主机地址调整
    - 添加 pydantic 配置 `extra="ignore"` 提升兼容性
    - 简化默认 API 响应消息

    ### 📝 文档更新

    - 同步更新所有文档
    - 更新 README
    - 修正配置示例

---

## v0.0.4 - v0.0.1 (2025-09-09)

??? note "早期版本 - 项目初始化"

    ### 🎉 核心功能

    - 🏗️ **基础框架搭建**
        - FastAPI 集成
        - Tortoise ORM 集成
        - 基础项目结构
    - 🔍 **自动发现机制**
        - 路由自动发现
        - 模型自动发现
        - 命令自动发现
    - 🗄️ **模型基类**
        - UUIDModel
        - DateTimeModel
        - StatusModel
    - 🛠️ **命令行工具**
        - DB 命令（init, migrate, upgrade）
        - Server 命令
        - 基础命令系统
    - ⚙️ **配置系统**
        - 环境变量支持
        - BaseSettings 集成
        - 配置自动发现

    ### 🐛 Bug 修复

    - 修复各种初期 bug
    - 优化代码结构
    - 改进错误处理

    ### 📝 文档

    - 创建 README
    - 添加基础文档
    - 示例代码

---

## 版本规划

### 🚀 即将推出

- **v0.1.0** (计划中)
  - 🔐 认证授权系统
  - 📧 邮件发送支持
  - 📦 文件上传组件
  - 🔄 WebSocket 支持
  - 📊 性能监控集成

### 💡 未来展望

- **v0.2.0** (规划中)
  - 🧪 测试框架集成
  - 📈 监控和追踪
  - 🌐 国际化支持
  - 🎨 Admin 后台界面
  - 🔌 插件系统

---

## 👨‍💻 开发者信息

**裴振飞 (peizhenfei)**

- 📧 **邮箱**: [peizhenfei@cvte.com](mailto:peizhenfei@cvte.com)
- 💬 **微信**: `hsdtsyl` (黑色的碳酸饮料)
- 🐙 **GitHub**: [@mautops](https://github.com/mautops)
- 🏢 **组织**: CVTE

!!! tip "联系方式"
如有问题或建议，欢迎通过以下方式联系：

    - 📮 **邮件咨询**: peizhenfei@cvte.com
    - 💬 **微信交流**: hsdtsyl (添加时请备注"Faster APP")
    - 🐛 **问题反馈**: [GitHub Issues](https://github.com/mautops/faster-app/issues)
    - 💡 **功能建议**: [GitHub Discussions](https://github.com/mautops/faster-app/discussions)

---

## 🤝 贡献

感谢所有为 Faster APP 做出贡献的开发者！

如果你想参与贡献，请阅读 [贡献指南](../contributing/how-to-contribute.md)。

---

## 📦 获取最新版本

```bash
# 使用 uv
uv add faster-app --upgrade

# 使用 pip
pip install --upgrade faster-app
```

查看 [GitHub Releases](https://github.com/mautops/faster-app/releases) 获取详细的发布说明。
