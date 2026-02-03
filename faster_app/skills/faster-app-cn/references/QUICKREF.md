# 快速参考

快速查找常用代码片段和常见问题解答。

## 快速开始

```bash
# 安装
uv add faster-app

# 创建应用
faster app demo

# 数据库迁移
faster db migrate --name="init"
faster db upgrade

# 启动服务
faster server start
```

访问 `http://localhost:8000/docs` 查看 API 文档。

## 模型定义

### 基础模型

```python
from faster_app.models.base import UUIDModel, DateTimeModel
from tortoise import fields

# 标准模型（UUID + 时间戳）
class Article(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    content: str = fields.TextField()
    status: str = fields.CharField(max_length=20, default="draft")
```

### 关系字段

```python
# ForeignKey（一对多）
author: fields.ForeignKeyField = fields.ForeignKeyField(
    "models.Author",
    related_name="articles",
    on_delete=fields.CASCADE
)

# ManyToMany（多对多）
tags: fields.ManyToManyField = fields.ManyToManyField(
    "models.Tag",
    related_name="articles"
)

# OneToOne（一对一）
profile: fields.OneToOneField = fields.OneToOneField(
    "models.Profile",
    related_name="user",
    on_delete=fields.CASCADE
)
```

## 查询操作

```python
# 基础查询
await Article.all()
await Article.get(id=id)
await Article.filter(status="published")
await Article.filter(view_count__gt=100)

# 排序和限制
await Article.all().order_by("-created_at").limit(10)

# 预取关系（避免 N+1）
await Article.all().prefetch_related("author", "tags")

# 聚合查询
from tortoise.functions import Count, Sum
await Article.all().annotate(comment_count=Count("comments"))
```

## ViewSet

### 基础 CRUD

```python
from faster_app.viewsets import ModelViewSet

class ArticleViewSet(ModelViewSet):
    model = Article
    schema = ArticleResponse
    create_schema = ArticleCreate
    update_schema = ArticleUpdate

    # 认证和权限
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # 过滤和搜索
    filter_backends = [SearchFilter, OrderingFilter, FieldFilter]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    filter_fields = {"status": "exact"}

    # 限流
    throttle_classes = [UserRateThrottle(), AnonRateThrottle()]

# 注册路由
router = ArticleViewSet.as_router(prefix="/articles", tags=["Article"])
```

### 自定义操作

```python
from faster_app.viewsets import action

@action(detail=True, methods=["POST"])
async def publish(self, request: Request, pk: str):
    """发布文章"""
    article = await self.get_object(pk)
    article.status = "published"
    await article.save()
    return ApiResponse.success(message="发布成功")

@action(detail=False, methods=["GET"])
async def statistics(self, request: Request):
    """统计信息"""
    total = await Article.all().count()
    published = await Article.filter(status="published").count()
    return ApiResponse.success(data={"total": total, "published": published})
```

## 配置

### 环境变量（.env）

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
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# 数据库
DB_URL=sqlite://db.sqlite
# DB_URL=postgresql://user:pass@localhost:5432/dbname
# DB_URL=mysql://user:pass@localhost:3306/dbname

# CORS
CORS_ORIGINS=["*"]
CORS_CREDENTIALS=false

# 生命周期
LIFESPAN_DATABASE=true
LIFESPAN_APPS=false
```

### 访问配置

```python
from faster_app.settings import configs

# 基础配置
configs.DEBUG
configs.PROJECT_NAME

# 服务器配置
configs.SERVER_HOST
configs.SERVER_PORT

# JWT 配置
configs.JWT_SECRET_KEY
configs.JWT_ALGORITHM

# 数据库配置
configs.DB_URL
```

## 常见问题

### 安装和配置

**Q: 生产环境需要修改哪些配置？**
- `JWT_SECRET_KEY`：必须修改为强随机值
- `DEBUG=false`
- `CORS_ORIGINS`：设置具体域名（不要用 `["*"]`）
- `TRUSTED_HOST_ENABLED=true`

**Q: 如何生成 .env 文件？**
```bash
faster app env
```

### 模型相关

**Q: 如何避免 N+1 查询？**
```python
# 使用 prefetch_related 预取关系
articles = await Article.all().prefetch_related("author", "tags")
```

**Q: 如何实现软删除？**
```python
class Article(UUIDModel, DateTimeModel):
    deleted_at: datetime = fields.DatetimeField(null=True)

    async def soft_delete(self):
        self.deleted_at = datetime.now()
        await self.save()

    @classmethod
    def active_objects(cls):
        return cls.filter(deleted_at__isnull=True)
```

### ViewSet 相关

**Q: 如何添加认证？**
```python
from faster_app.viewsets.authentication import JWTAuthentication

class ArticleViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
```

**Q: 如何添加权限控制？**
```python
from faster_app.viewsets.permissions import IsAuthenticated, IsAdminUser

class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]  # 需要登录
    # permission_classes = [IsAdminUser]    # 需要管理员
```

**Q: 如何添加过滤？**
```python
from faster_app.viewsets.filters import FieldFilter

class ArticleViewSet(ModelViewSet):
    filter_backends = [FieldFilter]
    filter_fields = {
        "status": "exact",           # 精确匹配
        "title": "icontains",        # 包含（不区分大小写）
        "view_count": "gt",          # 大于
        "created_at": "gte",         # 大于等于
    }
```

### 错误处理

**Q: 路由未发现？**
- 确保 `APIRouter` 实例在模块作用域（不在函数内）
- 检查文件在 `apps/*/routes.py`
- 验证无导入错误（`python -m apps.your_app.routes`）

**Q: 模型未注册？**
- 检查继承自 `tortoise.Model`
- 文件名必须为 `models.py`
- 运行 `faster db migrate` 生成迁移

**Q: 配置未加载？**
- 检查 `.env` 在项目根目录
- 验证变量名大写（如 `SERVER_HOST`）
- 使用 `configs.DEBUG` 而非 `configs.debug`

**Q: 数据库连接失败？**
- 检查 `DB_URL` 格式是否正确
- 确保数据库服务已启动
- 验证用户名和密码
- 检查 `LIFESPAN_DATABASE=true`

## 命令速查

```bash
# 应用管理
faster app demo              # 创建演示应用
faster app config            # 创建配置目录
faster app env               # 生成 .env 文件

# 数据库管理
faster db init               # 初始化 Aerich
faster db migrate --name=xxx # 生成迁移
faster db upgrade            # 应用迁移
faster db downgrade          # 回滚迁移
faster db history            # 查看迁移历史

# 服务器
faster server start          # 启动开发服务器
faster server start --host 0.0.0.0 --port 9000  # 自定义地址和端口
```

## 生产环境检查清单

- [ ] 修改 `JWT_SECRET_KEY` 为强随机值
- [ ] 设置 `DEBUG=false`
- [ ] 配置 `CORS_ORIGINS` 为具体域名
- [ ] 启用 `TRUSTED_HOST_ENABLED=true`
- [ ] 设置 `TRUSTED_HOSTS` 为允许的主机名
- [ ] 使用生产级数据库（PostgreSQL/MySQL）
- [ ] 配置日志输出到文件（`LOG_TO_FILE=true`）
- [ ] 设置合理的限流规则
- [ ] 配置 HTTPS
- [ ] 设置数据库连接池
- [ ] 配置监控和告警

更多详细信息请查阅完整文档。
