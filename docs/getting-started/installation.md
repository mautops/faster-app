# 安装

本页面介绍如何安装 Faster APP。

## 系统要求

- **Python**: >= 3.12
- **数据库**: PostgreSQL (推荐) 或 SQLite
- **包管理器**: uv (推荐) 或 pip

## 使用 uv 安装（推荐）

[uv](https://github.com/astral-sh/uv) 是一个极快的 Python 包管理器，我们强烈推荐使用它。

### 1. 安装 uv

=== "macOS/Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

### 2. 创建项目

```bash
# 初始化新项目
uv init my-project
cd my-project

# 添加 Faster APP
uv add faster-app

# 移除默认的 main.py
rm main.py
```

### 3. 验证安装

```bash
faster --help
```

如果看到 Faster APP 的命令列表，说明安装成功！

## 使用 pip 安装

如果你更习惯使用 pip，也可以这样安装：

### 1. 创建虚拟环境

```bash
# 创建项目目录
mkdir my-project
cd my-project

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

### 2. 安装 Faster APP

```bash
pip install faster-app
```

### 3. 验证安装

```bash
faster --help
```

## 数据库准备

Faster APP 默认使用 SQLite，无需额外配置。如果需要使用 PostgreSQL：

### PostgreSQL 安装

=== "macOS"

    ```bash
    brew install postgresql@15
    brew services start postgresql@15
    ```

=== "Ubuntu/Debian"

    ```bash
    sudo apt update
    sudo apt install postgresql postgresql-contrib
    sudo systemctl start postgresql
    ```

=== "使用 Docker"

    ```bash
    docker run -d \
      --name faster-postgres \
      -e POSTGRES_PASSWORD=password \
      -e POSTGRES_DB=faster_app \
      -p 5432:5432 \
      postgres:15-alpine
    ```

### 创建数据库

```bash
# 连接到 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE faster_app;

# 创建用户
CREATE USER faster_user WITH PASSWORD 'password';

# 授权
GRANT ALL PRIVILEGES ON DATABASE faster_app TO faster_user;
```

## 开发工具（可选）

推荐安装以下开发工具：

```bash
# 使用 uv
uv add --dev ruff black mypy

# 使用 pip
pip install ruff black mypy
```

## 下一步

安装完成后，继续阅读 [快速入门](quickstart.md) 开始你的第一个 Faster APP 项目。

## 常见问题

??? question "如何升级到最新版本？"

    === "uv"
        ```bash
        uv add faster-app --upgrade
        ```

    === "pip"
        ```bash
        pip install --upgrade faster-app
        ```

??? question "安装失败怎么办？"

    1. 检查 Python 版本：`python --version`（需要 >= 3.12）
    2. 升级 pip：`pip install --upgrade pip`
    3. 查看详细错误信息：`pip install faster-app --verbose`
    4. 在 [GitHub Issues](https://github.com/mautops/faster-app/issues) 寻求帮助

??? question "是否支持 Python 3.10？"

    目前 Faster APP 要求 Python >= 3.12，因为我们使用了一些新特性（如 tomllib）。
