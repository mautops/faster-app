# 环境变量前缀

## 概述

Faster APP 使用 `FASTER_` 作为环境变量前缀，避免与其他应用或系统环境变量产生命名冲突。

## 为什么需要前缀？

### ❌ 没有前缀的问题

```bash
# 多个应用可能使用相同的环境变量名
export DEBUG=true       # 你的应用
export DEBUG=false      # 另一个应用
export PORT=8000        # 你的应用  
export PORT=3000        # 另一个应用
export HOST=0.0.0.0     # 你的应用
export HOST=localhost   # 另一个应用

# 会发生冲突！最后一个会覆盖前面的
```

### ✅ 使用前缀的优势

```bash
# 使用前缀，每个应用都有自己的命名空间
export FASTER_DEBUG=true
export FASTER_PORT=8000
export FASTER_HOST=0.0.0.0

export ANOTHER_APP_DEBUG=false
export ANOTHER_APP_PORT=3000
export ANOTHER_APP_HOST=localhost

# 不会冲突！各自独立
```

## 使用方式

### 方式 1: .env 文件（推荐）

创建 `.env` 文件，所有配置项都需要 `FASTER_` 前缀：

```bash
# .env

# 基础配置
FASTER_PROJECT_NAME=My App
FASTER_VERSION=1.0.0
FASTER_DEBUG=false

# 服务器配置
FASTER_HOST=0.0.0.0
FASTER_PORT=8000

# API 配置
FASTER_API_V1_STR=/api/v1

# JWT 配置
FASTER_SECRET_KEY=your-super-secret-key-with-at-least-32-chars
FASTER_ALGORITHM=HS256
FASTER_ACCESS_TOKEN_EXPIRE_MINUTES=60

# 数据库配置
FASTER_DB_TYPE=postgres
FASTER_DB_HOST=db.production.com
FASTER_DB_PORT=5432
FASTER_DB_USER=prod_user
FASTER_DB_PASSWORD=Str0ng!P@ssw0rd
FASTER_DB_DATABASE=production_db

# 日志配置
FASTER_LOG_LEVEL=INFO
FASTER_LOG_FORMAT=STRING
```

### 方式 2: 系统环境变量

```bash
# Linux/macOS
export FASTER_DEBUG=false
export FASTER_SECRET_KEY=your-secret-key
export FASTER_DB_PASSWORD=your-password

# Windows CMD
set FASTER_DEBUG=false
set FASTER_SECRET_KEY=your-secret-key

# Windows PowerShell
$env:FASTER_DEBUG="false"
$env:FASTER_SECRET_KEY="your-secret-key"
```

### 方式 3: Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    image: faster-app:latest
    environment:
      - FASTER_DEBUG=false
      - FASTER_SECRET_KEY=${FASTER_SECRET_KEY}
      - FASTER_DB_HOST=postgres
      - FASTER_DB_PASSWORD=${FASTER_DB_PASSWORD}
    env_file:
      - .env.production
```

### 方式 4: Kubernetes ConfigMap/Secret

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: faster-app-config
data:
  FASTER_DEBUG: "false"
  FASTER_DB_HOST: "postgres-service"
  FASTER_DB_PORT: "5432"
  FASTER_LOG_LEVEL: "INFO"

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: faster-app-secrets
type: Opaque
stringData:
  FASTER_SECRET_KEY: "your-secret-key-here"
  FASTER_DB_PASSWORD: "your-db-password-here"
```

## 配置项映射

| 环境变量 | 配置字段 | 类型 | 默认值 |
|----------|----------|------|--------|
| `FASTER_PROJECT_NAME` | PROJECT_NAME | str | "Faster APP" |
| `FASTER_VERSION` | VERSION | str | "0.0.1" |
| `FASTER_DEBUG` | DEBUG | bool | true |
| `FASTER_HOST` | HOST | str | "0.0.0.0" |
| `FASTER_PORT` | PORT | int | 8000 |
| `FASTER_API_V1_STR` | API_V1_STR | str | "/api/v1" |
| `FASTER_SECRET_KEY` | SECRET_KEY | SecretStr | "..." |
| `FASTER_ALGORITHM` | ALGORITHM | str | "HS256" |
| `FASTER_ACCESS_TOKEN_EXPIRE_MINUTES` | ACCESS_TOKEN_EXPIRE_MINUTES | int | 30 |
| `FASTER_DB_TYPE` | DB_TYPE | str | "sqlite" |
| `FASTER_DB_ENGINE` | DB_ENGINE | str | "tortoise.backends.asyncpg" |
| `FASTER_DB_HOST` | DB_HOST | str | "localhost" |
| `FASTER_DB_PORT` | DB_PORT | int | 5432 |
| `FASTER_DB_USER` | DB_USER | str | "postgres" |
| `FASTER_DB_PASSWORD` | DB_PASSWORD | SecretStr | "postgres" |
| `FASTER_DB_DATABASE` | DB_DATABASE | str | "faster_app" |
| `FASTER_LOG_LEVEL` | LOG_LEVEL | str | "INFO" |
| `FASTER_LOG_FORMAT` | LOG_FORMAT | str | "STRING" |

## 重要注意事项

### ⚠️ 前缀是必需的

从配置系统启用前缀后，**所有**环境变量都必须使用 `FASTER_` 前缀：

```bash
# ❌ 错误：不带前缀的变量会被忽略
export DEBUG=false
export SECRET_KEY=my-key

# ✅ 正确：使用前缀
export FASTER_DEBUG=false
export FASTER_SECRET_KEY=my-key
```

### 📝 .env 文件也需要前缀

即使在 `.env` 文件中，也必须使用前缀：

```bash
# .env

# ❌ 错误
DEBUG=false
SECRET_KEY=my-key

# ✅ 正确
FASTER_DEBUG=false
FASTER_SECRET_KEY=my-key
```

### 🔄 类型自动转换

Pydantic 会自动转换环境变量的类型：

```bash
# 布尔值
FASTER_DEBUG=true    # → True
FASTER_DEBUG=false   # → False
FASTER_DEBUG=1       # → True
FASTER_DEBUG=0       # → False

# 整数
FASTER_PORT=8000     # → 8000 (int)

# 字符串
FASTER_PROJECT_NAME="My App"  # → "My App" (str)
```

## 验证前缀功能

### 测试是否正确使用前缀

```python
import os
from faster_app.settings.builtins.settings import DefaultSettings

# 测试 1: 设置不带前缀的环境变量（应该被忽略）
os.environ["DEBUG"] = "false"
os.environ["PORT"] = "9000"

settings = DefaultSettings()
print(settings.DEBUG)  # 输出: True（使用默认值，忽略环境变量）
print(settings.PORT)   # 输出: 8000（使用默认值，忽略环境变量）

# 测试 2: 设置带前缀的环境变量（应该被使用）
os.environ["FASTER_DEBUG"] = "false"
os.environ["FASTER_PORT"] = "9000"

settings = DefaultSettings()
print(settings.DEBUG)  # 输出: False（使用环境变量）
print(settings.PORT)   # 输出: 9000（使用环境变量）
```

## 迁移指南

### 从无前缀迁移到有前缀

如果你已经在使用 Faster APP 且环境变量没有前缀，需要执行以下迁移：

#### 步骤 1: 更新 .env 文件

```bash
# 旧的 .env（无前缀）
DEBUG=false
SECRET_KEY=my-key
DB_PASSWORD=my-password

# 新的 .env（有前缀）
FASTER_DEBUG=false
FASTER_SECRET_KEY=my-key
FASTER_DB_PASSWORD=my-password
```

#### 步骤 2: 更新部署脚本

```bash
# 旧脚本
export DEBUG=false
export SECRET_KEY=$SECRET_KEY

# 新脚本
export FASTER_DEBUG=false
export FASTER_SECRET_KEY=$SECRET_KEY
```

#### 步骤 3: 更新 Docker/K8s 配置

```yaml
# 旧的 docker-compose.yml
environment:
  - DEBUG=false
  - SECRET_KEY=${SECRET_KEY}

# 新的 docker-compose.yml
environment:
  - FASTER_DEBUG=false
  - FASTER_SECRET_KEY=${SECRET_KEY}
```

#### 步骤 4: 更新 CI/CD 配置

```yaml
# GitHub Actions 示例
# 旧的
env:
  DEBUG: false
  SECRET_KEY: ${{ secrets.SECRET_KEY }}

# 新的
env:
  FASTER_DEBUG: false
  FASTER_SECRET_KEY: ${{ secrets.SECRET_KEY }}
```

### 批量迁移脚本

如果你有大量环境变量需要迁移，可以使用脚本：

```bash
#!/bin/bash
# migrate_env.sh

# 读取旧的 .env 文件并添加前缀
while IFS='=' read -r key value; do
  # 跳过空行和注释
  if [[ -z "$key" ]] || [[ "$key" =~ ^# ]]; then
    continue
  fi
  
  # 添加前缀并输出
  echo "FASTER_${key}=${value}"
done < .env > .env.new

echo "迁移完成！请检查 .env.new 文件"
```

## 最佳实践

### ✅ 推荐做法

1. **始终使用前缀**
   ```bash
   export FASTER_DEBUG=false
   ```

2. **在 .env.example 中也使用前缀**
   ```bash
   # .env.example
   FASTER_SECRET_KEY=change-me
   FASTER_DB_PASSWORD=change-me
   ```

3. **文档中说明前缀要求**
   ```markdown
   ## 环境变量
   
   所有环境变量都需要 `FASTER_` 前缀：
   - FASTER_DEBUG
   - FASTER_SECRET_KEY
   - ...
   ```

4. **在错误消息中提示前缀**
   ```python
   # 如果配置加载失败，提示用户检查前缀
   print("提示：环境变量需要 FASTER_ 前缀")
   ```

### ❌ 避免的做法

1. ❌ 混用带前缀和不带前缀的变量
2. ❌ 在不同环境使用不同的前缀规则
3. ❌ 忘记在 .env.example 中添加前缀
4. ❌ 部署脚本中使用不带前缀的变量

## 故障排查

### 问题 1: 环境变量不生效

**症状：** 设置了环境变量，但应用仍使用默认值

**原因：** 可能忘记添加前缀

**解决：**
```bash
# ❌ 错误
export DEBUG=false

# ✅ 正确
export FASTER_DEBUG=false
```

### 问题 2: 部署后配置错误

**症状：** 本地运行正常，部署后出错

**原因：** 部署环境的环境变量没有添加前缀

**解决：** 检查并更新部署配置（Docker、K8s、CI/CD等）

### 问题 3: 敏感信息未加载

**症状：** SECRET_KEY 或 DB_PASSWORD 使用默认值

**原因：** 忘记在环境变量名前添加 FASTER_ 前缀

**解决：**
```bash
# ❌ 错误
export SECRET_KEY=my-secret

# ✅ 正确
export FASTER_SECRET_KEY=my-secret
```

## 技术细节

### Pydantic 配置

前缀是通过 Pydantic Settings 的 `env_prefix` 配置实现的：

```python
class DefaultSettings(BaseSettings):
    # ... 字段定义 ...
    
    class Config:
        env_file = ".env"
        env_prefix = "FASTER_"  # 所有环境变量必须有此前缀
        extra = "ignore"
```

### 工作原理

1. Pydantic 读取环境变量时，会自动查找带 `FASTER_` 前缀的变量
2. 例如，`PROJECT_NAME` 字段会从 `FASTER_PROJECT_NAME` 环境变量读取
3. 不带前缀的变量会被忽略

### 自定义前缀

如果需要使用不同的前缀，可以在自定义配置中覆盖：

```python
# config/settings.py
from faster_app.settings.builtins.settings import DefaultSettings

class Settings(DefaultSettings):
    class Config:
        env_prefix = "MYAPP_"  # 使用自定义前缀
```

## 总结

环境变量前缀是一个简单但强大的功能：

- ✅ 避免命名冲突
- ✅ 提高配置清晰度
- ✅ 便于多应用共存
- ✅ 符合最佳实践

**记住：所有 Faster APP 的环境变量都需要 `FASTER_` 前缀！**

