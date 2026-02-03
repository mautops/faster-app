# ViewSet 基础

本文档涵盖 ViewSet 的基础概念、Mixins 使用、自定义操作和钩子函数。

## 快速开始

```python
from faster_app.viewsets import ModelViewSet
from .models import Article
from .schemas import ArticleCreate, ArticleUpdate, ArticleResponse

class ArticleViewSet(ModelViewSet):
    model = Article                      # 必需：Tortoise 模型
    schema = ArticleResponse             # 必需：响应 schema
    create_schema = ArticleCreate        # 可选：创建 schema
    update_schema = ArticleUpdate        # 可选：更新 schema

# 注册路由
router = ArticleViewSet.as_router(prefix="/articles", tags=["文章"])
```

**生成的端点：**

- `GET /articles/` - 列出所有
- `POST /articles/` - 创建
- `GET /articles/{id}/` - 获取单个
- `PUT /articles/{id}/` - 更新
- `DELETE /articles/{id}/` - 删除

## 预构建的 ViewSet

### ModelViewSet - 完整 CRUD

```python
from faster_app.viewsets import ModelViewSet

class ArticleViewSet(ModelViewSet):
    # 包括：List + Create + Retrieve + Update + Destroy
    model = Article
    schema = ArticleResponse
```

### ReadOnlyModelViewSet - 只读

```python
from faster_app.viewsets import ReadOnlyModelViewSet

class ArticleViewSet(ReadOnlyModelViewSet):
    # 仅包括：List + Retrieve
    model = Article
    schema = ArticleResponse
```

## 自定义查询集

### 基础过滤

```python
class ArticleViewSet(ModelViewSet):
    model = Article
    schema = ArticleResponse

    def get_queryset(self):
        """仅返回已发布的文章"""
        return self.model.filter(status="published")
```

### 按操作过滤

```python
class ArticleViewSet(ModelViewSet):
    def get_queryset_for_action(self, action: str):
        """不同操作使用不同的查询集"""
        if action == "list":
            return self.model.filter(status="published")
        return self.model.all()
```

### 基于用户过滤

```python
class ArticleViewSet(ModelViewSet):
    def get_queryset(self):
        """返回当前用户的文章"""
        user_id = self.request.state.user.get("user_id")
        return self.model.filter(author_id=user_id)
```

## ViewSet Mixins

通过组合 mixins 构建自定义 ViewSet，实现精确的功能控制。

### Mixins 组合

```python
from faster_app.viewsets import (
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin
)

class ArticleViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    # 自定义 ViewSet，仅包含 List + Create + Retrieve
    model = Article
    schema = ArticleResponse
```

### 可用的 Mixins

#### ListModelMixin

提供列表查询功能：

```python
from faster_app.viewsets import GenericViewSet, ListModelMixin

class ArticleViewSet(ListModelMixin, GenericViewSet):
    model = Article
    schema = ArticleResponse

    # 生成端点：GET /articles/
```

#### CreateModelMixin

提供创建功能：

```python
from faster_app.viewsets import GenericViewSet, CreateModelMixin

class ArticleViewSet(CreateModelMixin, GenericViewSet):
    model = Article
    create_schema = ArticleCreate

    # 生成端点：POST /articles/
```

#### RetrieveModelMixin

提供单个资源查询：

```python
from faster_app.viewsets import GenericViewSet, RetrieveModelMixin

class ArticleViewSet(RetrieveModelMixin, GenericViewSet):
    model = Article
    schema = ArticleResponse

    # 生成端点：GET /articles/{id}/
```

#### UpdateModelMixin

提供更新功能：

```python
from faster_app.viewsets import GenericViewSet, UpdateModelMixin

class ArticleViewSet(UpdateModelMixin, GenericViewSet):
    model = Article
    update_schema = ArticleUpdate

    # 生成端点：PUT /articles/{id}/
```

#### DestroyModelMixin

提供删除功能：

```python
from faster_app.viewsets import GenericViewSet, DestroyModelMixin

class ArticleViewSet(DestroyModelMixin, GenericViewSet):
    model = Article

    # 生成端点：DELETE /articles/{id}/
```

### 常见组合模式

#### 只读 + 创建

```python
class ArticleViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    GenericViewSet
):
    # 可以列表、创建、查看，但不能更新或删除
    pass
```

#### 完全自定义

```python
class ArticleViewSet(GenericViewSet):
    # 不包含任何 mixin，完全自定义实现
    model = Article
    schema = ArticleResponse

    # 手动实现需要的方法
```

## 自定义操作

使用 `@action` 装饰器添加自定义端点，扩展 ViewSet 的标准 CRUD 功能。

### 实例级操作

对单个资源的操作（detail=True）：

```python
from faster_app.viewsets import ModelViewSet, action
from fastapi import Request

class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["POST"])
    async def publish(self, request: Request, pk: str):
        """
        发布文章
        路由：POST /articles/{pk}/publish
        """
        article = await self.get_object(pk)
        article.status = "published"
        article.published_at = datetime.now()
        await article.save()

        schema = self.get_schema("retrieve")
        return await schema.from_orm_model(article)
```

### 集合级操作

对资源集合的操作（detail=False）：

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["GET"])
    async def recent(self, request: Request):
        """
        获取最近文章
        路由：GET /articles/recent
        """
        articles = await self.model.filter(
            status="published"
        ).order_by("-created_at").limit(10)

        schema = self.get_schema("list")
        return [await schema.from_orm_model(a) for a in articles]
```

### 多 HTTP 方法

一个操作支持多个方法：

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["GET", "POST"])
    async def stats(self, request: Request, pk: str):
        """
        GET /articles/{pk}/stats - 查看统计
        POST /articles/{pk}/stats - 更新统计
        """
        article = await self.get_object(pk)

        if request.method == "GET":
            return {
                "views": article.view_count,
                "likes": article.like_count
            }
        else:  # POST
            article.view_count += 1
            await article.save()
            return {"status": "updated"}
```

### 自定义路径和名称

```python
class ArticleViewSet(ModelViewSet):
    @action(
        detail=True,
        methods=["POST"],
        url_path="make-public",
        url_name="make_public"
    )
    async def make_public(self, request: Request, pk: str):
        """
        路由：POST /articles/{pk}/make-public
        """
        article = await self.get_object(pk)
        article.is_public = True
        await article.save()
        return {"status": "public"}
```

### 操作参数

- `detail=True/False` - 实例级或集合级
- `methods=["GET", "POST"]` - HTTP 方法列表
- `url_path="custom"` - 自定义 URL 路径
- `url_name="custom_name"` - 自定义 URL 名称

### 访问请求数据

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["POST"])
    async def rate(self, request: Request, pk: str):
        """评分"""
        data = await request.json()
        rating = data.get("rating", 0)

        article = await self.get_object(pk)
        article.rating = rating
        await article.save()

        return {"rating": rating}
```

## 钩子函数

ViewSet 提供了多个钩子函数，允许在操作的不同阶段插入自定义逻辑。

### perform_create

在创建对象时执行额外逻辑：

```python
class ArticleViewSet(ModelViewSet):
    async def perform_create(self, data: dict):
        """创建前添加额外字段"""
        user_id = self.request.state.user.get("user_id")
        data["author_id"] = user_id
        data["status"] = "draft"
        return await self.model.create(**data)
```

### perform_update

在更新对象时执行额外逻辑：

```python
class ArticleViewSet(ModelViewSet):
    async def perform_update(self, instance, data: dict):
        """更新前记录修改时间"""
        data["updated_at"] = datetime.now()
        for key, value in data.items():
            setattr(instance, key, value)
        await instance.save()
```

### perform_destroy

在删除对象时执行额外逻辑：

```python
class ArticleViewSet(ModelViewSet):
    async def perform_destroy(self, instance):
        """软删除而非硬删除"""
        instance.deleted_at = datetime.now()
        await instance.save()
```

### get_object

自定义对象获取逻辑：

```python
class ArticleViewSet(ModelViewSet):
    async def get_object(self, pk: str):
        """获取对象时预加载关联数据"""
        return await self.model.get(id=pk).prefetch_related(
            "author", "tags", "comments"
        )
```

### get_schema

动态选择响应 schema：

```python
class ArticleViewSet(ModelViewSet):
    def get_schema(self, action: str):
        """根据操作返回不同的 schema"""
        if action == "list":
            return ArticleListResponse
        elif action == "retrieve":
            return ArticleDetailResponse
        return self.schema
```

## 最佳实践

1. **选择合适的 ViewSet** - 使用 ModelViewSet 或 ReadOnlyModelViewSet，避免不必要的端点
2. **组合 Mixins** - 需要精确控制时，使用 Mixins 组合而非完整 ViewSet
3. **合理使用 @action** - 为业务逻辑添加语义化的自定义操作
4. **利用钩子函数** - 在标准操作中注入业务逻辑，保持代码整洁
5. **查询集优化** - 使用 get_queryset 进行权限过滤和性能优化
6. **Schema 分离** - 为不同操作使用不同的 schema，提供精确的数据验证
7. **异步优先** - 所有数据库操作使用 async/await
8. **错误处理** - 在自定义操作中妥善处理异常情况
