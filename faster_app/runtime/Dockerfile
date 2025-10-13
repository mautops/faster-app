# 这是一个用于部署基于 faster-app 框架开发的应用的 Dockerfile 模板
# 请将此文件复制到您的应用项目根目录并根据需要修改

FROM python:3.12-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 设置文件权限
RUN chown -R appuser:appuser /app

# 使用 UV 安装 Python 依赖
RUN pip install uv && uv sync

# 切换到非 root 用户
USER appuser

# 健康检查 (根据您的应用调整端口和路径)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/docs || exit 1

# 暴露端口 (根据您的应用配置调整)
EXPOSE ${PORT:-8000}

# 启动命令 (根据您的应用入口调整)
CMD ["faster", "server", "start"]
