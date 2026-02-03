# Faster APP 配置完整指南

Faster APP 使用扁平化配置系统，支持环境变量和多环境部署。本指南涵盖从基础配置到高级用法的所有内容。

## 配置基础和中间件

### 配置访问

#### 基本用法

```python
from faster_app.settings import configs

# 基础配置
configs.DEBUG
configs.PROJECT_NAME
configs.VERSION

# 服务器配置
configs.SERVER_HOST
configs.SERVER_PORT

# JWT 配置
configs.JWT_SECRET_KEY
configs.JWT_ALGORITHM
configs.JWT_EXPIRE_MINUTES

# 数据库配置
configs.DB_URL
```

### 环境变量

#### .env 文件

在项目根目录创建 `.env` 文件：

```bash
# 基础配置
DEBUG=true
PROJECT_NAME=MyAPI
VERSION=1.0.0

# 服务器
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 安全
JWT_SECRET_KEY=your-secret-key-change-in-production

# 数据库
DB_URL=sqlite://db.sqlite
# DB_URL=postgresql://user:pass@localhost:5432/dbname
# DB_URL=mysql://user:pass@localhost:3306/dbname
```

#### 环境变量优先级

1. 操作系统环境变量（最高优先级）
2. `.env` 文件
3. 默认值（最低优先级）

```bash
# 通过环境变量覆盖
export DEBUG=false
export SERVER_PORT=9000
faster server start
```

### 中间件配置

Faster APP 内置多个中间件，可通过环境变量控制。

#### CORS 配置

跨域资源共享配置：

```bash
# 开发环境
CORS_ORIGINS=["*"]
CORS_CREDENTIALS=false
CORS_METHODS=["*"]
CORS_HEADERS=["*"]

# 生产环境（推荐）
CORS_ORIGINS=["https://example.com","https://app.example.com"]
CORS_CREDENTIALS=true
CORS_METHODS=["GET","POST","PUT","DELETE"]
CORS_HEADERS=["Content-Type","Authorization"]
```

**安全提示**：
- 生产环境**不要**使用 `["*"]`
- 如果设置 `CORS_CREDENTIALS=true`，必须指定具体域名

#### TrustedHost 配置

防止 Host header 攻击：

```bash
# 启用
TRUSTED_HOST_ENABLED=true

# 允许的主机
TRUSTED_HOSTS=["example.com","*.example.com","localhost"]
```

#### GZip 压缩

启用响应压缩：

```bash
GZIP_ENABLED=true
GZIP_MINIMUM_SIZE=1000  # 最小压缩大小（字节）
```

#### 限流配置

API 速率限制：

```bash
# 限流规则
THROTTLE_USER_RATE=100/hour
THROTTLE_ANON_RATE=20/hour
THROTTLE_DEFAULT_RATE=100/hour
```

### 数据库配置

#### 连接 URL 格式

```bash
# SQLite（开发）
DB_URL=sqlite://db.sqlite
DB_URL=sqlite:///absolute/path/db.sqlite

# PostgreSQL
DB_URL=postgresql://user:password@localhost:5432/database
DB_URL=postgresql://user:password@localhost:5432/database?schema=public

# MySQL
DB_URL=mysql://user:password@localhost:3306/database
DB_URL=mysql://user:password@localhost:3306/database?charset=utf8mb4
```

#### 连接池配置（生产环境）

```bash
DB_URL=postgresql://user:pass@localhost:5432/db?min_size=1&max_size=5
```

#### 生命周期配置

```bash
# 启用数据库生命周期管理
LIFESPAN_DATABASE=true

# 启用应用生命周期钩子
LIFESPAN_APPS=false

# 启用用户自定义生命周期
LIFESPAN_USER=false
```

### 配置结构

#### 扁平化配置

Faster APP 使用扁平化配置，所有配置项使用命名空间前缀：

```python
from faster_app.settings import configs

# 基础配置
configs.DEBUG              # bool
configs.PROJECT_NAME       # str
configs.VERSION            # str
configs.VALIDATE_ROUTES    # bool

# 服务器配置（SERVER_ 前缀）
configs.SERVER_HOST        # str
configs.SERVER_PORT        # int

# JWT 配置（JWT_ 前缀）
configs.JWT_SECRET_KEY     # str
configs.JWT_ALGORITHM      # str
configs.JWT_EXPIRE_MINUTES # int

# 数据库配置（DB_ 前缀）
configs.DB_URL             # str

# 日志配置（LOG_ 前缀）
configs.LOG_LEVEL          # str
configs.LOG_FORMAT         # str
configs.LOG_TO_FILE        # bool
configs.LOG_FILE_PATH      # str
configs.LOG_FILE_BACKUP_COUNT  # int

# 生命周期配置（LIFESPAN_ 前缀）
configs.LIFESPAN_DATABASE  # bool
configs.LIFESPAN_APPS      # bool
configs.LIFESPAN_USER      # bool

# 限流配置（THROTTLE_ 前缀）
configs.THROTTLE_USER_RATE     # str
configs.THROTTLE_ANON_RATE     # str
configs.THROTTLE_DEFAULT_RATE  # str

# CORS 配置（CORS_ 前缀）
configs.CORS_ORIGINS       # list[str]
configs.CORS_CREDENTIALS   # bool
configs.CORS_METHODS       # list[str]
configs.CORS_HEADERS       # list[str]
configs.CORS_EXPOSE_HEADERS    # list[str]
configs.CORS_MAX_AGE       # int

# 可信主机配置（TRUSTED_HOST_ 前缀）
configs.TRUSTED_HOST_ENABLED   # bool
configs.TRUSTED_HOSTS      # list[str]

# 性能监控配置（TIMING_ 前缀）
configs.TIMING_ENABLED     # bool
configs.TIMING_SLOW_THRESHOLD  # float

# 请求日志配置（REQUEST_LOGGING_ 前缀）
configs.REQUEST_LOGGING_ENABLED      # bool
configs.REQUEST_LOGGING_LOG_BODY     # bool
configs.REQUEST_LOGGING_LOG_RESPONSE # bool

# GZip 配置（GZIP_ 前缀）
configs.GZIP_ENABLED       # bool
configs.GZIP_MINIMUM_SIZE  # int
```

### 配置验证

Pydantic 自动验证配置：

```python
# 自动类型转换
DEBUG=true          # → configs.DEBUG = True (bool)
SERVER_PORT=8000    # → configs.SERVER_PORT = 8000 (int)

# 无效值会抛出异常
SERVER_PORT=abc     # ValidationError: value is not a valid integer
```

### 最佳实践

#### 1. 敏感信息

**不要**将敏感信息提交到版本控制：

```bash
# .gitignore
.env
.env.local
.env.*.local
```

提供示例文件：

```bash
# .env.example
DEBUG=true
JWT_SECRET_KEY=change-this-in-production
DB_URL=sqlite://db.sqlite
```

#### 2. 环境分离

为不同环境创建配置文件：

```bash
.env.development
.env.staging
.env.production
```

#### 3. 配置检查

启动时检查必需配置：

```python
from faster_app.settings import configs

if not configs.DEBUG:
    # 生产环境检查
    assert configs.JWT_SECRET_KEY != "your-secret-key-here-change-in-production", \
        "必须修改 JWT_SECRET_KEY"
    assert "*" not in configs.CORS_ORIGINS, \
        "生产环境不能使用 CORS_ORIGINS=['*']"
```

#### 4. 文档化配置

在 `.env.example` 中添加注释：

```bash
# API 服务器配置
SERVER_HOST=0.0.0.0       # 监听地址，0.0.0.0 表示所有接口
SERVER_PORT=8000          # 监听端口

# 安全配置
JWT_SECRET_KEY=your-secret-key  # JWT 密钥，生产环境必须修改
```

#### 5. 使用配置验证

```python
from faster_app.settings.builtins.settings import DefaultSettings
from pydantic import model_validator

class CustomSettings(DefaultSettings):
    @model_validator(mode="after")
    def validate_production(self):
        if not self.DEBUG:
            if self.JWT_SECRET_KEY == "your-secret-key-here-change-in-production":
                raise ValueError("生产环境必须修改 JWT_SECRET_KEY")
        return self
```

## 日志和生产环境

### 日志配置

#### 基础配置

```bash
# 日志级别
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# 日志格式
LOG_FORMAT=STRING  # STRING 或 JSON

# 文件日志
LOG_TO_FILE=false
LOG_FILE_PATH=logs/app.log
LOG_FILE_MAX_BYTES=10485760  # 10MB
LOG_FILE_BACKUP_COUNT=10
```

#### 日志级别说明

- **DEBUG** - 详细的调试信息（开发环境）
- **INFO** - 一般信息（默认，适合生产环境）
- **WARNING** - 警告信息
- **ERROR** - 错误信息
- **CRITICAL** - 严重错误

#### 日志格式

**STRING 格式**（易读）：

```
2024-01-09 10:30:45 - INFO - faster_app.routes.discover - 发现路由: /api/users
```

**JSON 格式**（结构化，适合日志分析）：

```json
{
  "timestamp": "2024-01-09T10:30:45.123Z",
  "level": "INFO",
  "logger": "faster_app.routes.discover",
  "message": "发现路由: /api/users"
}
```

#### 代码中使用日志

```python
from faster_app.utils.logger import logger

# 不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")

# 带异常信息
try:
    result = await some_operation()
except Exception as e:
    logger.error(f"操作失败: {e}", exc_info=True)
```

#### 文件日志配置

```bash
# 启用文件日志
LOG_TO_FILE=true
LOG_FILE_PATH=logs/app.log

# 日志轮转
LOG_FILE_MAX_BYTES=10485760      # 10MB
LOG_FILE_BACKUP_COUNT=10         # 保留 10 个备份

# 结果：
# logs/app.log
# logs/app.log.1
# logs/app.log.2
# ...
```

#### 生产环境日志建议

```bash
# 生产环境配置
LOG_LEVEL=WARNING    # 只记录警告和错误
LOG_FORMAT=JSON      # 结构化日志
LOG_TO_FILE=true     # 启用文件日志
LOG_FILE_PATH=/var/log/faster-app/app.log
```

### 生产环境检查清单

#### 1. 安全配置

```bash
# ✅ 必须修改
SECRET_KEY=使用强随机密钥  # 至少 32 字符

# ✅ 关闭调试模式
DEBUG=false

# ✅ 配置具体的 CORS 域名
CORS_ALLOW_ORIGINS=["https://example.com"]
CORS_ALLOW_CREDENTIALS=true

# ✅ 启用 TrustedHost
TRUSTED_HOST_ENABLED=true
TRUSTED_HOSTS=["example.com","*.example.com"]

# ✅ 使用 HTTPS
# 在反向代理（Nginx/Traefik）配置 SSL
```

#### 2. 数据库配置

```bash
# ✅ 使用生产数据库
DB_URL=postgresql://user:pass@db-server:5432/production_db

# ✅ 配置连接池
DB_URL=postgresql://user:pass@db-server:5432/production_db?min_size=2&max_size=10

# ✅ 定期备份数据库
# 使用 pg_dump / mysqldump 等工具
```

#### 3. 日志配置

```bash
# ✅ 合适的日志级别
LOG_LEVEL=WARNING  # 或 INFO

# ✅ 结构化日志
LOG_FORMAT=JSON

# ✅ 文件日志
LOG_TO_FILE=true
LOG_FILE_PATH=/var/log/faster-app/app.log

# ✅ 日志轮转
LOG_FILE_MAX_BYTES=10485760
LOG_FILE_BACKUP_COUNT=10
```

#### 4. 性能配置

```bash
# ✅ 启用 GZip
GZIP_ENABLED=true

# ✅ 配置限流
THROTTLE_RATES='{"user":"1000/hour","anon":"100/hour"}'

# ✅ 使用生产级 ASGI 服务器
# Uvicorn with workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 或 Gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

#### 5. 监控配置

```bash
# ✅ 健康检查端点
# 访问 /health 检查应用状态

# ✅ 配置监控工具
# - Prometheus + Grafana
# - Sentry（错误追踪）
# - NewRelic / DataDog
```

### 部署方式

#### Docker 部署

**Dockerfile**：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY pyproject.toml ./
RUN pip install .

# 复制代码
COPY . .

# 设置环境变量
ENV DEBUG=false
ENV HOST=0.0.0.0
ENV PORT=8000

# 启动应用
CMD ["faster", "server", "start"]
```

**docker-compose.yml**：

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - SECRET_KEY=${SECRET_KEY}
      - DB_URL=postgresql://user:pass@db:5432/app
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Systemd 服务

**`/etc/systemd/system/faster-app.service`**：

```ini
[Unit]
Description=Faster APP Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/faster-app
Environment="PATH=/opt/faster-app/.venv/bin"
EnvironmentFile=/opt/faster-app/.env
ExecStart=/opt/faster-app/.venv/bin/faster server start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name example.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;
    
    # SSL 配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 反向代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态文件（如果有）
    location /static {
        alias /opt/faster-app/static;
        expires 30d;
    }
}
```

### 监控和告警

#### 健康检查

```python
# Faster APP 自动提供健康检查端点
# GET /health
{
    "status": "healthy",
    "database": "connected",
    "timestamp": "2024-01-09T10:30:45Z"
}
```

#### 错误追踪（Sentry）

```bash
# 安装
uv add sentry-sdk

# 配置
export SENTRY_DSN=https://xxx@sentry.io/xxx
```

```python
# config/settings.py
import sentry_sdk

if not configs.DEBUG and configs.SENTRY_DSN:
    sentry_sdk.init(
        dsn=configs.SENTRY_DSN,
        environment="production"
    )
```

#### 性能监控

```bash
# 使用 Prometheus
uv add prometheus-fastapi-instrumentator

# 访问指标端点
# GET /metrics
```

### 备份策略

#### 数据库备份

```bash
# PostgreSQL
pg_dump -U user -d database > backup_$(date +%Y%m%d).sql

# MySQL
mysqldump -u user -p database > backup_$(date +%Y%m%d).sql

# 定时备份（crontab）
0 2 * * * /path/to/backup.sh
```

#### 配置备份

```bash
# 备份 .env 文件
cp .env .env.backup

# 版本控制配置模板
git add .env.example
```

### 性能优化

#### 1. 数据库优化

- 添加索引
- 使用连接池
- 优化查询（避免 N+1）

#### 2. 缓存

- Redis 缓存查询结果
- CDN 缓存静态资源

#### 3. 负载均衡

```bash
# 多个 worker
uvicorn main:app --workers 4

# Nginx 负载均衡
upstream faster_app {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

## 高级配置

### 多环境配置

#### 环境文件

为不同环境创建独立的配置文件：

```bash
# 项目结构
.
├── .env                  # 默认（开发）
├── .env.development      # 开发环境
├── .env.staging          # 预发布环境
├── .env.production       # 生产环境
└── .env.example          # 示例文件（提交到 git）
```

#### 加载特定环境

**方式1：通过环境变量**

```bash
# 指定环境文件
export ENV_FILE=.env.production
faster server start

# 或一行命令
ENV_FILE=.env.production faster server start
```

**方式2：通过符号链接**

```bash
# 开发环境
ln -sf .env.development .env

# 生产环境
ln -sf .env.production .env
```

#### 环境配置示例

**`.env.development`**：

```bash
DEBUG=true
HOST=0.0.0.0
PORT=8000
SECRET_KEY=dev-secret-key
DB_URL=sqlite://db.sqlite
CORS_ALLOW_ORIGINS=["*"]
LOG_LEVEL=DEBUG
```

**`.env.staging`**：

```bash
DEBUG=false
HOST=0.0.0.0
PORT=8000
SECRET_KEY=${STAGING_SECRET_KEY}
DB_URL=postgresql://user:pass@staging-db:5432/app
CORS_ALLOW_ORIGINS=["https://staging.example.com"]
LOG_LEVEL=INFO
```

**`.env.production`**：

```bash
DEBUG=false
HOST=0.0.0.0
PORT=8000
SECRET_KEY=${PRODUCTION_SECRET_KEY}
DB_URL=postgresql://user:pass@prod-db:5432/app
CORS_ALLOW_ORIGINS=["https://example.com"]
TRUSTED_HOST_ENABLED=true
TRUSTED_HOSTS=["example.com"]
LOG_LEVEL=WARNING
LOG_FORMAT=JSON
LOG_TO_FILE=true
```

### Docker 多环境

**docker-compose.yml**：

```yaml
version: '3.8'

services:
  app:
    build: .
    env_file:
      - .env.${ENVIRONMENT:-development}
    ports:
      - "${PORT:-8000}:8000"
```

**使用**：

```bash
# 开发环境
docker-compose up

# 生产环境
ENVIRONMENT=production docker-compose up
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: faster-app-config
data:
  DEBUG: "false"
  HOST: "0.0.0.0"
  PORT: "8000"
  DB_URL: "postgresql://user:pass@db:5432/app"
---
apiVersion: v1
kind: Secret
metadata:
  name: faster-app-secrets
type: Opaque
stringData:
  SECRET_KEY: "your-secret-key"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: faster-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: faster-app:latest
        envFrom:
        - configMapRef:
            name: faster-app-config
        - secretRef:
            name: faster-app-secrets
```

### 自定义配置

#### 扩展配置类

```python
# config/settings.py
from faster_app.settings.config import DefaultSettings
from pydantic import Field

class CustomSettings(DefaultSettings):
    """自定义配置"""
    
    # 添加新配置项
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )
    
    cache_ttl: int = Field(
        default=300,
        validation_alias="CACHE_TTL"
    )
    
    feature_flags: dict = Field(
        default_factory=dict,
        validation_alias="FEATURE_FLAGS"
    )

# 使用自定义配置
from config.settings import CustomSettings
configs = CustomSettings()
```

#### 嵌套配置

**注意：** Faster APP 使用扁平化配置结构，不推荐使用嵌套配置。所有配置项应使用大写命名空间前缀。

```python
from pydantic import BaseModel, Field

class CustomSettings(DefaultSettings):
    """自定义配置 - 扁平化结构"""

    # 邮件配置（扁平化）
    SMTP_HOST: str = Field(default="localhost")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    FROM_EMAIL: str = Field(default="noreply@example.com")

# 环境变量
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=user@example.com
# SMTP_PASSWORD=password
# FROM_EMAIL=noreply@example.com

# 访问
configs.SMTP_HOST
configs.SMTP_PORT
```

#### 配置验证

```python
from pydantic import model_validator

class CustomSettings(DefaultSettings):
    redis_url: str = Field(validation_alias="REDIS_URL")
    
    @model_validator(mode="after")
    def validate_redis(self):
        """验证 Redis 配置"""
        if not self.DEBUG:
            # 生产环境检查 Redis
            if "localhost" in self.redis_url:
                raise ValueError("生产环境不能使用 localhost Redis")
        return self
    
    @model_validator(mode="after")
    def validate_production(self):
        """生产环境验证"""
        if not self.DEBUG:
            # 检查必需配置
            assert self.JWT_SECRET_KEY != "test-secret-key"
            assert self.CORS_ORIGINS != ["*"]
            assert self.TRUSTED_HOST_ENABLED
        return self
```

### 密钥管理

#### 环境变量注入

```bash
# 从密钥管理系统读取
export SECRET_KEY=$(vault kv get -field=secret_key secret/faster-app)
export DB_PASSWORD=$(vault kv get -field=password secret/faster-app)

# 启动应用
faster server start
```

#### Docker Secrets

```yaml
version: '3.8'

services:
  app:
    image: faster-app:latest
    secrets:
      - secret_key
      - db_password
    environment:
      - SECRET_KEY_FILE=/run/secrets/secret_key
      - DB_PASSWORD_FILE=/run/secrets/db_password

secrets:
  secret_key:
    external: true
  db_password:
    external: true
```

#### AWS Secrets Manager

```python
import boto3
import json

def get_secrets():
    """从 AWS Secrets Manager 读取密钥"""
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='faster-app/prod')
    return json.loads(response['SecretString'])

# 在应用启动时加载
secrets = get_secrets()
os.environ['SECRET_KEY'] = secrets['secret_key']
os.environ['DB_PASSWORD'] = secrets['db_password']
```

### 动态配置

#### 运行时修改

```python
from faster_app.settings import configs

# 读取
current_level = configs.LOG_LEVEL

# 运行时修改（谨慎使用）
configs.LOG_LEVEL = "DEBUG"
```

#### 配置热更新

```python
import signal

def reload_config(signum, frame):
    """重新加载配置"""
    global configs
    configs = CustomSettings()
    logger.info("配置已重新加载")

# 注册信号处理
signal.signal(signal.SIGHUP, reload_config)
```

### 配置文件格式

#### YAML 配置（可选）

```python
import yaml

class YAMLSettings(DefaultSettings):
    @classmethod
    def from_yaml(cls, file_path: str):
        """从 YAML 文件加载"""
        with open(file_path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

# config.yaml
# debug: false
# server:
#   host: 0.0.0.0
#   port: 8000

configs = YAMLSettings.from_yaml('config.yaml')
```

#### JSON 配置（可选）

```python
import json

class JSONSettings(DefaultSettings):
    @classmethod
    def from_json(cls, file_path: str):
        """从 JSON 文件加载"""
        with open(file_path) as f:
            data = json.load(f)
        return cls(**data)
```

### 最佳实践

#### 1. 环境隔离

- 开发/预发布/生产环境完全隔离
- 使用不同的数据库和服务

#### 2. 密钥安全

- 不要将密钥提交到 Git
- 使用密钥管理服务
- 定期轮换密钥

#### 3. 配置验证

- 启动时验证所有必需配置
- 生产环境强制检查

#### 4. 文档化

- 在 `.env.example` 中注释所有配置项
- 维护配置文档

#### 5. 版本控制

- `.env` 加入 `.gitignore`
- `.env.example` 提交到 Git
- 配置模板版本化

通过合理的配置管理和最佳实践，可以确保应用在不同环境下稳定、安全地运行。