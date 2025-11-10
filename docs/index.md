# 🚀 Faster APP

<div align="center" markdown>

**FastAPI 最佳实践框架 - 约定优于配置**

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](about/license.md)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](about/changelog.md)

_为 FastAPI 带来 Django 风格的项目结构和开发体验_

[:material-rocket-launch: 快速开始](getting-started/quickstart.md){ .md-button .md-button--primary }
[:material-github: GitHub](https://github.com/mautops/faster-app){ .md-button }

</div>

---

## 💡 核心理念

**约定优于配置** - 通过标准化的项目结构和智能自动发现，让你专注于业务逻辑而非基础设施搭建

<div class="grid cards" markdown>

- :material-cog-outline:{ .lg } **零配置启动**

  ***

  遵循约定的目录结构，框架自动发现并注册所有组件

- :material-lightning-bolt:{ .lg } **5 分钟上手**

  ***

  内置项目模板和命令行工具，快速搭建完整应用

- :material-shield-check:{ .lg } **生产就绪**

  ***

  企业级模型基类、数据库迁移、日志配置，开箱即用

- :material-code-braces:{ .lg } **开发者友好**

  ***

  Django 风格的命令行、自动 API 文档、热重载支持

</div>

---

## ✨ 核心特性

### 🔍 智能自动发现

自动扫描并注册路由、模型、命令、中间件和配置 - **无需手动配置**

```python
# apps/users/routes.py - 自动发现并注册
router = APIRouter(prefix="/users", tags=["用户"])

@router.get("")
async def list_users():
    return await User.all()
```

[:octicons-arrow-right-24: 了解自动发现机制](features/auto-discovery.md)

---

### 🗄️ 企业级模型基类

开箱即用的模型基类，通过组合快速构建数据模型

```python
# UUID + 时间戳 + 多租户
class Order(UUIDModel, DateTimeModel, ScopeModel):
    order_no = fields.CharField(max_length=50)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
```

[:octicons-arrow-right-24: 探索模型基类](features/models.md)

---

### 🛠️ Django 风格命令行

强大的命令行工具，简化开发流程

```bash
faster app demo      # 创建示例应用
faster db migrate    # 生成数据库迁移
faster server start  # 启动开发服务器
```

[:octicons-arrow-right-24: 查看命令行工具](features/cli.md)

---

## 🚀 快速体验

=== "安装"

    ```bash
    # 使用 uv（推荐）
    uv init my-project
    cd my-project
    uv add faster-app
    rm main.py
    ```

=== "初始化"

    ```bash
    # 创建项目结构
    faster app demo
    faster app env

    # 初始化数据库
    faster db init
    faster db init_db
    ```

=== "启动"

    ```bash
    # 启动开发服务器
    faster server start

    # 访问 http://localhost:8000/docs
    ```

<div align="center" markdown>

[:material-book-open-page-variant: 完整安装指南](getting-started/installation.md){ .md-button }
[:material-play-circle: 快速入门教程](getting-started/quickstart.md){ .md-button .md-button--primary }

</div>

---

## 🎯 设计原则

!!! abstract "六大核心原则"

    1. **约定优于配置** - 标准化结构，自动发现组件
    2. **自动发现优于手动注册** - 消除 80% 的样板代码
    3. **组合优于继承** - 灵活的模型基类组合
    4. **显式优于隐式** - 保留自定义覆盖能力
    5. **开发体验优于配置灵活性** - 开箱即用的功能
    6. **生产就绪优于演示代码** - 可直接用于商业项目

[:octicons-arrow-right-24: 深入了解设计哲学](getting-started/structure.md)

---

## 🌟 适用场景

<div class="grid" markdown style="grid-template-columns: repeat(auto-fit, minmax(min(100%, 12rem), 1fr))">

<div markdown>
:material-flash:{ .lg } **快速原型**  
5 分钟搭建完整后端
</div>

<div markdown>
:material-account-group:{ .lg } **团队协作**  
统一代码结构和规范
</div>

<div markdown>
:material-office-building:{ .lg } **企业应用**  
生产环境最佳实践
</div>

<div markdown>
:material-api:{ .lg } **API 服务**  
RESTful API 开发
</div>

<div markdown>
:material-cloud:{ .lg } **SaaS 应用**  
内置多租户支持
</div>

<div markdown>
:material-graph:{ .lg } **微服务**  
标准化服务结构
</div>

</div>

---

## 🤝 社区与支持

<div class="grid" markdown style="grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr))">

<div markdown>
:material-book-open-variant:{ .lg }  
**[文档中心](getting-started/installation.md)**  
完整的使用指南和 API 参考
</div>

<div markdown>
:material-bug:{ .lg }  
**[问题反馈](https://github.com/mautops/faster-app/issues)**  
报告 Bug 或提出改进建议
</div>

<div markdown>
:material-forum:{ .lg }  
**[讨论区](https://github.com/mautops/faster-app/discussions)**  
与社区成员交流讨论
</div>

<div markdown>
:material-hand-heart:{ .lg }  
**[贡献指南](contributing/how-to-contribute.md)**  
参与开源项目建设
</div>

</div>

---

## 🙏 致谢

感谢以下开源项目的启发：

<div class="grid" markdown style="grid-template-columns: repeat(auto-fit, minmax(min(100%, 10rem), 1fr))">

- ⚡ **[FastAPI](https://fastapi.tiangolo.com/)**  
  现代、快速的 Web 框架

- 🐢 **[Tortoise ORM](https://tortoise.github.io/)**  
  异步 ORM 框架

- 🔥 **[Fire](https://github.com/google/python-fire)**  
  命令行接口生成器

- 🎨 **[Django](https://www.djangoproject.com/)**  
  约定优于配置的理念

</div>

---

## 👨‍💻 开发者

<div class="grid" markdown style="grid-template-columns: 2fr 1fr; gap: 2rem;">

<div markdown>

**裴振飞** · _peizhenfei_

:material-email: **邮箱**：[peizhenfei@cvte.com](mailto:peizhenfei@cvte.com)  
:material-wechat: **微信**：`hsdtsyl` (添加请备注"Faster APP")  
:material-github: **GitHub**：[@mautops](https://github.com/mautops)  
:material-office-building: **公司**：CVTE

:material-bug: **问题反馈**：[GitHub Issues](https://github.com/mautops/faster-app/issues)  
:material-lightbulb: **功能建议**：[GitHub Discussions](https://github.com/mautops/faster-app/discussions)

</div>

<div align="center" markdown>

<img src="assets/images/微信好友.jpg" alt="微信好友" style="width: 100%; max-width: 280px;">

**扫码添加微信**

</div>

</div>

---

## 💝 赞助支持

如果 Faster APP 帮你节省了时间、提升了效率，或让你的开发工作变得更轻松，不妨请作者喝杯咖啡 ☕️  
**你的每一份支持，都是我持续优化和添加新功能的动力！** ❤️

<div align="center" markdown>

<div class="grid" markdown style="grid-template-columns: repeat(2, 1fr); gap: 2.5rem; max-width: 700px; margin: 2rem auto;">

<div align="center" markdown>

**微信支付**

<img src="assets/images/微信收款.jpg" alt="微信收款" style="width: 100%; max-width: 300px;">

</div>

<div align="center" markdown>

**支付宝**

<img src="assets/images/支付宝收款.jpg" alt="支付宝收款" style="width: 100%; max-width: 300px;">

</div>

</div>

_感谢每一份支持！你的鼓励是我持续更新的动力_ 🚀

</div>

---

<div align="center" markdown>

**⭐ 如果这个项目对你有帮助，请给我们一个 Star！**

[:material-github: GitHub](https://github.com/mautops/faster-app){ .md-button .md-button--primary }
[:material-book: 文档](getting-started/installation.md){ .md-button }
[:material-history: Changelog](about/changelog.md){ .md-button }

<small>Copyright © 2024 peizhenfei · [MIT License](about/license.md)</small>

</div>
