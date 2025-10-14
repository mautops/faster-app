# 部署指南

本页面介绍如何将 Faster APP 应用部署到生产环境。

## 部署方式

### Docker 部署

```bash
# 创建 Dockerfile
faster app docker

# 构建镜像
docker build -t my-app:latest .

# 运行容器
docker run -d \
  -p 8000:8000 \
  --env-file .env.production \
  my-app:latest
```

### 使用 uv 部署

```bash
# 安装生产依赖
uv sync --no-dev

# 启动应用
uv run faster server start
```

## 生产环境配置

```bash
# .env.production
DEBUG=False
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql://user:pass@db:5432/myapp
```

更多详细内容...
