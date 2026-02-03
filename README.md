<div align="center">

# 🚀 Faster APP

**FastAPI 最佳实践框架 - 约定优于配置**

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.9-orange.svg)](https://github.com/mautops/faster-app)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://mautops.github.io/faster-app/)

_为 FastAPI 带来 Django 风格的项目结构和开发体验_

<br>

**📚 [完整文档站](https://mautops.github.io/faster-app/)** | [快速开始](#-快速开始) | [核心特性](#-核心特性) | [命令行工具](#️-命令行工具) | [赞助支持](#-赞助支持)

<br>

> 💡 **提示**：README 仅包含快速入门指南,完整的使用教程、API 参考和最佳实践请访问 [📖 在线文档站](https://mautops.github.io/faster-app/)

</div>

---

## 🎯 解决什么问题？

### 💭 FastAPI 的灵活性困扰

FastAPI 非常灵活, 但这种灵活性也带来了问题:

| 问题             | 表现                               | 影响                       |
| ---------------- | ---------------------------------- | -------------------------- |
| **项目结构混乱** | 每个项目都有不同的目录结构         | 团队协作困难, 代码难以维护 |
| **重复造轮子**   | 每次都要重新设计模型基类、路由结构 | 开发效率低, 代码质量不一致 |
| **配置复杂**     | 手动注册路由、中间件、数据库模型   | 容易出错, 启动代码冗长     |
| **缺乏约定**     | 没有统一的开发规范和最佳实践       | 新人上手困难, 项目难以扩展 |

> ### 💡 Faster APP 的解决方案

**核心理念:约定优于配置 (Convention over Configuration)**

借鉴 Django 的成功经验, 为 FastAPI 制定一套标准化的项目结构和开发约定。

---

## ✨ 核心特性

### 🏗️ 标准化项目结构

```
your-project/
├── apps/                    # 应用模块 (Django 风格)
│   ├── users/              # 用户模块
│   │   ├── models.py       # 数据模型
│   │   ├── routes.py       # API 路由
│   │   └── commands.py     # 命令行工具
│   └── posts/              # 文章模块
│       ├── models.py
│       ├── routes.py
│       └── commands.py
├── config/                 # 配置目录
│   └── settings.py         # 自定义配置
└── .env                    # 环境变量
```

### 🔍 智能发现与注册

> 通过智能自动发现, 实现项目 0️⃣ 配置启动

#### 🛣️ 路由自动发现

扫描 `apps/*/*.py` 文件, 递归查找 `APIRouter` 类的实例, 并注册成为 Fastapi 路由

#### 📊 模型自动发现

扫描 `apps/*/models.py` 文件, 递归查找 `tortoise.Model` 类, 并注册到 TORTOISE_ORM 中, 实现模型自动化管理

#### ⚡ 命令自动发现

扫描 `apps/*/*.py` 文件, 递归查找 `BaseCommand` 类实例, 注册给 Fire 库, 实现命令行参数管理

#### 🔧 中间件自动发现

扫描 `apps/middleware/*.py` 文件, 递归查找 `BaseMiddleware` 类, 然后注册到 fastapi 实例, 实现中间件注册

#### ⚙️ 项目配置自动发现

扫描 `apps/config/*.py` 文件, 递归查找 `BaseSettings` 类实例, 自动合并多个配置类, 从 `.env` 中读取配置并注册给应用；

### 🗄️ 企业级模型基类

```python
# 四大基础模型, 覆盖 90% 业务场景
UUIDModel     # UUID 主键
DateTimeModel # 创建/更新时间
EnumModel   # 动态枚举字段
ScopeModel    # 多租户作用域
```

### 🛠️ Django 风格命令行

```bash
faster server start    # 启动开发服务器
faster db migrate      # 数据库迁移
faster db upgrade      # 执行迁移
```

---

## 🚀 快速开始

### 📦 安装

```bash
# 使用 uv (推荐)
uv add faster-app

# 或使用 pip
pip install faster-app
```

### ⚡ 5 分钟快速上手

```bash
# 1. 创建项目
uv init my-project && cd my-project
uv add faster-app

# 2. 创建应用结构
faster app demo

# 3. 启动开发服务器
faster server start
```

✅ **完成！** 访问 http://localhost:8000 查看你的 FastAPI 应用

### 📚 接下来做什么？

<div align="center">

| 📖 [完整安装教程](https://mautops.github.io/faster-app/getting-started/installation/) | ⚡ [快速入门指南](https://mautops.github.io/faster-app/getting-started/quickstart/) | 🏗️ [项目结构说明](https://mautops.github.io/faster-app/getting-started/structure/) |
| :-----------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------: |
|                               详细的安装步骤和环境配置                                |                                 从零创建第一个应用                                  |                               理解目录结构和文件组织                               |

</div>

## 🛠️ 命令行工具

Faster APP 提供完整的 Django 风格命令行工具：

### 📋 常用命令

```bash
# 应用管理
faster app demo              # 创建示例应用
faster app config            # 创建配置目录
faster app env               # 创建环境变量文件

# 数据库管理
faster db init               # 初始化迁移
faster db migrate            # 生成迁移文件
faster db upgrade            # 执行迁移

# 服务器管理
faster server start          # 启动开发服务器
```

### 📖 完整命令参考

想了解所有命令的详细用法？查看完整文档：

<div align="center">

**[📚 查看完整 CLI 文档](https://mautops.github.io/faster-app/cli/app/)**

包含所有命令的参数说明、使用示例和最佳实践

</div>

---

## 📖 文档导航

<div align="center">

<table>
<tr>
<td align="center" width="33%">
<h3>🚀 快速开始</h3>
<a href="https://mautops.github.io/faster-app/getting-started/installation/">安装指南</a><br>
<a href="https://mautops.github.io/faster-app/getting-started/quickstart/">快速入门</a><br>
<a href="https://mautops.github.io/faster-app/getting-started/structure/">项目结构</a>
</td>
<td align="center" width="33%">
<h3>⚙️ 核心功能</h3>
<a href="https://mautops.github.io/faster-app/features/auto-discovery/">自动发现</a><br>
<a href="https://mautops.github.io/faster-app/features/models/">模型基类</a><br>
<a href="https://mautops.github.io/faster-app/features/routes/">路由管理</a>
</td>
<td align="center" width="33%">
<h3>💡 最佳实践</h3>
<a href="https://mautops.github.io/faster-app/best-practices/organization/">项目组织</a><br>
<a href="https://mautops.github.io/faster-app/best-practices/database/">数据库设计</a><br>
<a href="https://mautops.github.io/faster-app/best-practices/api-design/">API 设计</a>
</td>
</tr>
</table>

**[🌐 访问完整文档站 →](https://mautops.github.io/faster-app/)**

</div>

---

<details>
<summary><b>🎯 为什么选择 Faster APP？点击展开</b></summary>

<br>

### 💭 FastAPI 的灵活性困扰

借鉴 Django 的成功经验, 为 FastAPI 制定一套标准化的项目结构和开发约定。

</details>

## 🤝 社区与支持

### 📞 获取帮助

- 📚 **[完整文档](https://mautops.github.io/faster-app/)** - 详细的使用指南、API 参考和最佳实践
  - [快速开始](https://mautops.github.io/faster-app/getting-started/installation/) - 5 分钟快速上手
  - [核心功能](https://mautops.github.io/faster-app/features/auto-discovery/) - 自动发现、模型、路由等
  - [命令行参考](https://mautops.github.io/faster-app/cli/app/) - 完整的 CLI 命令文档
  - [API 参考](https://mautops.github.io/faster-app/api/overview/) - 自动生成的 API 文档
  - [最佳实践](https://mautops.github.io/faster-app/best-practices/organization/) - 项目组织、数据库设计等
- 🐛 [问题反馈](https://github.com/mautops/faster-app/issues) - 报告 Bug 或提出改进建议
- 💬 [讨论区](https://github.com/mautops/faster-app/discussions) - 与社区成员交流讨论

### 🤝 贡献代码

1. 🍴 **Fork 本仓库**
2. 🌱 **创建特性分支**: `git checkout -b feature/amazing-feature`
3. ✨ **提交更改**: `git commit -m 'Add amazing feature'`
4. 🚀 **推送分支**: `git push origin feature/amazing-feature`
5. 📝 **提交 Pull Request**

### 🎨 设计原则

- 📜 **约定优于配置**: 通过约定减少配置
- 🎆 **Django 风格**: 借鉴 Django 的成功经验
- 🚀 **开发者友好**: 提升开发效率和体验
- 🏢 **企业级**: 满足生产环境需求

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🙏 致谢

感谢以下开源项目的启发:

- ⚡ [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- 🐢 [Tortoise ORM](https://tortoise.github.io/) - 异步 ORM 框架
- 🔥 [Fire](https://github.com/google/python-fire) - 命令行接口生成器

---

## 📚 资源链接

- 🌐 **[在线文档](https://mautops.github.io/faster-app/)** - 完整的使用指南和 API 参考
- 📦 **[PyPI 包](https://pypi.org/project/faster-app/)** - 通过 `pip` 或 `uv` 安装
- 💻 **[GitHub 仓库](https://github.com/mautops/faster-app)** - 源代码和问题追踪
- 📝 **[更新日志](https://mautops.github.io/faster-app/about/changelog/)** - 查看版本历史和新功能

---

## 💝 赞助支持

如果 Faster APP 帮你节省了时间、提升了效率,或让你的开发工作变得更轻松,不妨请作者喝杯咖啡 ☕️  
**你的每一份支持,都是我持续优化和添加新功能的动力！** ❤️

<div align="center">

<table>
  <tr>
    <td align="center" width="50%">
      <img src="docs/assets/images/微信收款.jpg" width="250px" alt="微信支付"><br>
      <b>微信支付</b>
    </td>
    <td align="center" width="50%">
      <img src="docs/assets/images/支付宝收款.jpg" width="250px" alt="支付宝"><br>
      <b>支付宝</b>
    </td>
  </tr>
</table>

_感谢每一份支持！你的鼓励是我持续更新的动力_ 🚀

</div>

---

<div align="center">

## 🌟 给个 Star 吧！

**如果 Faster APP 对你有帮助,请给我们一个 ⭐️ Star！**

这是对开源项目最好的支持和鼓励

<br>

[![Star History Chart](https://api.star-history.com/svg?repos=mautops/faster-app&type=Date)](https://star-history.com/#mautops/faster-app&Date)

<br>

---

### 📚 快速链接

**[📖 在线文档](https://mautops.github.io/faster-app/)** · **[📦 PyPI](https://pypi.org/project/faster-app/)** · **[💬 讨论区](https://github.com/mautops/faster-app/discussions)** · **[📝 更新日志](https://mautops.github.io/faster-app/about/changelog/)**

**作者**: [peizhenfei](mailto:peizhenfei@cvte.com) · **微信**: `hsdtsyl` · **[GitHub](https://github.com/mautops)**

<br>

**⚡️ [立即访问完整文档 →](https://mautops.github.io/faster-app/)**

</div>
