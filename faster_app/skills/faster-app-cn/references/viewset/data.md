# ViewSet 数据处理

本文档涵盖 ViewSet 的过滤、搜索、排序、分页、缓存和高级数据处理模式。

## 过滤

过滤允许客户端通过查询参数筛选数据。

### 过滤集

#### 基础过滤

```python
from faster_app.viewsets import ModelViewSet
from faster_app.viewsets.filters import FilterSet

class ArticleFilterSet(FilterSet):
    fields = {
        "status": ["exact", "in"],
        "author": ["exact"],
        "created_at": ["gte", "lte"],
        "title": ["contains", "icontains"],
    }

class ArticleViewSet(ModelViewSet):
    filterset_class = ArticleFilterSet
```

#### 查询示例

```bash
# 精确匹配
?status=published

# 在列表中
?status__in=draft,published

# 日期范围
?created_at__gte=2024-01-01&created_at__lte=2024-12-31

# 包含
?title__contains=Python
```

### 过滤操作符

#### 比较操作符

- `exact` - 精确匹配：`?field=value`
- `in` - 在列表中：`?field__in=val1,val2`
- `gt` - 大于：`?field__gt=10`
- `gte` - 大于等于：`?field__gte=10`
- `lt` - 小于：`?field__lt=10`
- `lte` - 小于等于：`?field__lte=10`

#### 字符串操作符

- `contains` - 包含（区分大小写）：`?field__contains=text`
- `icontains` - 包含（不区分大小写）：`?field__icontains=text`
- `startswith` - 开始于：`?field__startswith=prefix`
- `endswith` - 结束于：`?field__endswith=suffix`

#### 空值操作符

- `isnull` - 为空：`?field__isnull=true`
- `not_isnull` - 不为空：`?field__not_isnull=true`

### 自定义过滤

#### 方法过滤

```python
class ArticleFilterSet(FilterSet):
    fields = {
        "status": ["exact"],
    }

    async def filter_author(self, queryset, value):
        """自定义作者过滤"""
        if value:
            return queryset.filter(author__name__icontains=value)
        return queryset
```

#### 多字段过滤

```python
class ArticleFilterSet(FilterSet):
    async def filter_query(self, queryset, value):
        """在多个字段中搜索"""
        if value:
            return queryset.filter(
                Q(title__icontains=value) | Q(content__icontains=value)
            )
        return queryset
```

### 关系过滤

跨关系过滤：

```python
class ArticleFilterSet(FilterSet):
    fields = {
        "author__name": ["exact", "icontains"],
        "tags__name": ["in"],
        "category__slug": ["exact"],
    }

# 查询示例
# ?author__name__icontains=zhang
# ?tags__name__in=python,fastapi
# ?category__slug=tech
```

### 动态过滤

根据用户动态过滤：

```python
class ArticleViewSet(ModelViewSet):
    filterset_class = ArticleFilterSet

    def get_queryset(self):
        queryset = super().get_queryset()

        # 非管理员只能看到已发布的
        user = self.request.state.user
        if user.get("role") != "admin":
            queryset = queryset.filter(status="published")

        return queryset
```

## 搜索

搜索允许在多个字段中进行全文搜索。

### 基础搜索

跨多个字段搜索：

```python
class ArticleViewSet(ModelViewSet):
    search_fields = ["title", "content"]

    # 用法：?search=python
```

### 跨关系搜索

```python
class ArticleViewSet(ModelViewSet):
    search_fields = [
        "title",
        "content",
        "author__name",
        "tags__name"
    ]

    # 用法：?search=张三
```

### 自定义搜索

```python
class ArticleViewSet(ModelViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(author__name__icontains=search)
            )

        return queryset
```

### 搜索优化

#### 添加索引

```python
class Article(UUIDModel, DateTimeModel):
    title: str = Field(..., max_length=200, index=True)
    content: str = Field(..., index=True)
```

#### 限制搜索字段

```python
class ArticleViewSet(ModelViewSet):
    search_fields = ["title"]  # 只搜索标题，提高性能
```

## 排序

排序允许客户端指定结果的排序方式。

### 基础排序

```python
class ArticleViewSet(ModelViewSet):
    ordering_fields = ["created_at", "title", "view_count"]
    ordering = ["-created_at"]  # 默认：最新优先
```

### 查询示例

```bash
# 升序
?ordering=title

# 降序
?ordering=-created_at

# 多字段排序
?ordering=-created_at,title
```

### 跨关系排序

```python
class ArticleViewSet(ModelViewSet):
    ordering_fields = [
        "created_at",
        "title",
        "author__name",
        "view_count"
    ]

    # 用法：?ordering=author__name
```

### 默认排序

#### 模型级别

```python
class Article(UUIDModel, DateTimeModel):
    title: str = Field(...)

    class Meta:
        table = "articles"
        ordering = ["-created_at", "title"]
```

#### ViewSet 级别

```python
class ArticleViewSet(ModelViewSet):
    ordering = ["-is_featured", "-created_at"]
    # 先按推荐排序，再按时间排序
```

### 组合搜索和排序

```python
class ArticleViewSet(ModelViewSet):
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "view_count", "title"]
    ordering = ["-created_at"]

# 查询示例
# ?search=python&ordering=-view_count
```

## 分页

分页自动应用于列表操作，避免一次返回过多数据。

### 自动分页

列表操作自动分页：

```python
class ArticleViewSet(ModelViewSet):
    model = Article
    schema = ArticleResponse

    # 列表端点自动分页
```

### 响应格式

```json
{
  "items": [
    {"id": "1", "title": "文章1"},
    {"id": "2", "title": "文章2"}
  ],
  "total": 100,
  "page": 1,
  "size": 50,
  "pages": 2
}
```

### 查询参数

```bash
# 获取第一页，每页 20 条
?page=1&size=20

# 获取第二页，每页 50 条
?page=2&size=50
```

### 默认配置

框架使用 `fastapi-pagination` 提供分页：

- **默认每页大小**：50
- **最大每页大小**：100
- **页码从 1 开始**

### 自定义分页大小

#### 请求时指定

```bash
?page=1&size=10
```

#### ViewSet 级别配置

```python
from fastapi_pagination import Page

class ArticleViewSet(ModelViewSet):
    # 使用自定义分页配置
    pagination_class = Page
```

### 禁用分页

某些操作可能不需要分页：

```python
from faster_app.viewsets import action

class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["GET"])
    async def all(self, request: Request):
        """获取所有文章（不分页）"""
        articles = await self.model.all()
        return articles
```

### 分页与过滤组合

```bash
# 过滤已发布的文章，第一页，每页 20 条
?status=published&page=1&size=20
```

### 分页与排序组合

```bash
# 按时间降序，第二页，每页 10 条
?ordering=-created_at&page=2&size=10
```

### 分页最佳实践

1. **合理的页面大小**：通常 20-50 条
2. **限制最大值**：避免一次查询过多数据
3. **总是排序**：确保分页结果一致
4. **使用索引**：为排序字段添加数据库索引
5. **缓存总数**：对于大数据集，可以缓存 total 值

## 缓存

缓存可以显著提升 API 性能，减少数据库查询。

### 基础缓存

#### 启用缓存

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 300  # 缓存 5 分钟
```

### 缓存行为

#### 自动缓存

以下方法自动缓存：
- `list()` - 列表查询
- `retrieve()` - 单个资源查询

#### 自动失效

以下操作自动清除缓存：
- `create()` - 创建资源
- `update()` - 更新资源
- `destroy()` - 删除资源

### 自定义缓存键

#### 基于用户

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 300

    def get_cache_key(self, action: str, **kwargs) -> str:
        if action == "list":
            user_id = self.request.state.user.get("user_id", "anon")
            return f"articles_list_{user_id}"
        return super().get_cache_key(action, **kwargs)
```

#### 基于查询参数

```python
class ArticleViewSet(ModelViewSet):
    def get_cache_key(self, action: str, **kwargs) -> str:
        if action == "list":
            status = self.request.query_params.get("status", "all")
            page = self.request.query_params.get("page", "1")
            return f"articles_list_{status}_{page}"
        return super().get_cache_key(action, **kwargs)
```

### 手动缓存控制

#### 清除特定缓存

```python
from faster_app.viewsets import action

class ArticleViewSet(ModelViewSet):
    cache_timeout = 300

    @action(detail=True, methods=["POST"])
    async def publish(self, request: Request, pk: str):
        article = await self.get_object(pk)
        article.status = "published"
        await article.save()

        # 清除列表缓存
        self.clear_cache("list")

        return {"status": "published"}
```

#### 预热缓存

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["POST"])
    async def warm_cache(self, request: Request):
        """预热热门文章缓存"""
        articles = await self.model.filter(
            is_featured=True
        ).limit(10)

        # 缓存每篇文章
        for article in articles:
            cache_key = self.get_cache_key("retrieve", pk=article.id)
            await self.set_cache(cache_key, article)

        return {"status": "cache warmed"}
```

### 禁用缓存

#### 整个 ViewSet

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 0  # 禁用缓存
```

#### 特定操作

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 300

    @action(detail=False, methods=["GET"])
    async def realtime_stats(self, request: Request):
        """实时统计，不使用缓存"""
        # 此方法不会被缓存
        pass
```

### 缓存策略

#### 短缓存（热数据）

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 60  # 1 分钟
    # 适用于经常变化的数据
```

#### 长缓存（冷数据）

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 3600  # 1 小时
    # 适用于很少变化的数据
```

#### 永久缓存

```python
class ArticleViewSet(ModelViewSet):
    cache_timeout = 86400 * 30  # 30 天
    # 适用于几乎不变的数据
```

### 条件缓存

#### 基于用户角色

```python
class ArticleViewSet(ModelViewSet):
    def get_cache_timeout(self, action: str) -> int:
        user = self.request.state.user
        if user.get("role") == "admin":
            return 0  # 管理员不缓存
        return 300  # 普通用户缓存 5 分钟
```

#### 基于数据状态

```python
class ArticleViewSet(ModelViewSet):
    async def retrieve(self, request: Request, pk: str):
        article = await self.get_object(pk)

        # 已发布的文章缓存更长时间
        if article.status == "published":
            self.cache_timeout = 3600
        else:
            self.cache_timeout = 60

        return await super().retrieve(request, pk)
```

### 缓存最佳实践

1. **合理设置超时**：根据数据更新频率
2. **细粒度缓存键**：包含相关查询参数
3. **及时清除**：数据变更时清除相关缓存
4. **监控命中率**：跟踪缓存效果
5. **避免缓存雪崩**：使用随机化的过期时间

## 高级模式

### 嵌套资源

#### 基础嵌套

```python
class CommentViewSet(ModelViewSet):
    model = Comment
    schema = CommentResponse

    def get_queryset(self):
        article_id = self.request.path_params.get("article_id")
        return self.model.filter(article_id=article_id)

# 路由：/articles/{article_id}/comments
router = CommentViewSet.as_router(
    prefix="/articles/{article_id}/comments",
    tags=["评论"]
)
```

#### 创建嵌套资源

```python
class CommentViewSet(ModelViewSet):
    @action(detail=False, methods=["POST"])
    async def create_comment(self, request: Request):
        article_id = request.path_params.get("article_id")
        data = await request.json()

        comment = await Comment.create(
            article_id=article_id,
            **data
        )
        return await CommentResponse.from_orm_model(comment)
```

### 批量操作

#### 批量创建

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["POST"])
    async def batch_create(self, request: Request):
        """批量创建文章"""
        data = await request.json()
        articles = data.get("articles", [])

        created = []
        for article_data in articles:
            article = await self.model.create(**article_data)
            created.append(article)

        return {"created": len(created)}
```

#### 批量更新

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["POST"])
    async def batch_publish(self, request: Request):
        """批量发布"""
        data = await request.json()
        ids = data.get("ids", [])

        await self.model.filter(id__in=ids).update(
            status="published",
            published_at=datetime.now()
        )

        return {"updated": len(ids)}
```

#### 批量删除

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["DELETE"])
    async def batch_delete(self, request: Request):
        """批量删除"""
        data = await request.json()
        ids = data.get("ids", [])

        deleted = await self.model.filter(id__in=ids).delete()
        return {"deleted": deleted}
```

### 软删除

#### 实现软删除

```python
class ArticleViewSet(ModelViewSet):
    def get_queryset(self):
        """排除软删除的项"""
        return self.model.filter(deleted_at__isnull=True)

    async def perform_destroy(self, instance):
        """软删除而非硬删除"""
        instance.deleted_at = datetime.now()
        await instance.save()
```

#### 恢复软删除

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["POST"])
    async def restore(self, request: Request, pk: str):
        """恢复软删除的项"""
        instance = await self.model.get(id=pk)
        instance.deleted_at = None
        await instance.save()
        return {"status": "restored"}
```

### 文件上传

#### 单文件上传

```python
from fastapi import UploadFile, File

class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["POST"])
    async def upload_image(
        self,
        request: Request,
        pk: str,
        file: UploadFile = File(...)
    ):
        """上传文章图片"""
        article = await self.get_object(pk)

        # 保存文件
        file_path = f"uploads/{pk}/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        article.image_url = file_path
        await article.save()

        return {"image_url": file_path}
```

#### 多文件上传

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["POST"])
    async def upload_images(
        self,
        request: Request,
        pk: str,
        files: list[UploadFile] = File(...)
    ):
        """上传多张图片"""
        article = await self.get_object(pk)

        uploaded = []
        for file in files:
            file_path = f"uploads/{pk}/{file.filename}"
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            uploaded.append(file_path)

        article.images = uploaded
        await article.save()

        return {"images": uploaded}
```

### 版本控制

#### 记录版本

```python
class ArticleViewSet(ModelViewSet):
    async def perform_update(self, instance, data):
        """更新前记录版本"""
        # 保存历史版本
        await ArticleHistory.create(
            article_id=instance.id,
            version=instance.version,
            data=instance.to_dict()
        )

        # 更新实例
        instance.version += 1
        for key, value in data.items():
            setattr(instance, key, value)
        await instance.save()
```

#### 查看版本历史

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=True, methods=["GET"])
    async def history(self, request: Request, pk: str):
        """查看版本历史"""
        history = await ArticleHistory.filter(
            article_id=pk
        ).order_by("-created_at")

        return [h.to_dict() for h in history]
```

## 数据处理最佳实践

### 过滤和搜索

1. **添加索引** - 为常用过滤和搜索字段添加数据库索引
2. **限制字段** - 只在必要字段上启用搜索，避免性能问题
3. **验证输入** - 验证过滤参数，防止注入攻击
4. **文档化** - 清晰文档化可用的过滤和搜索选项

### 排序和分页

1. **默认排序** - 总是提供默认排序，确保结果一致性
2. **限制页面大小** - 设置合理的最大页面大小
3. **索引排序字段** - 为排序字段添加索引
4. **缓存总数** - 大数据集考虑缓存 total 计数

### 缓存

1. **分层缓存** - 结合应用缓存和 CDN
2. **缓存预热** - 系统启动时预热热门数据
3. **监控** - 监控缓存命中率和性能
4. **版本化** - 缓存键包含版本信息，便于失效

### 高级模式

1. **嵌套资源** - 保持 URL 层次清晰，不超过 3 层
2. **批量操作** - 限制批量操作数量，防止滥用
3. **软删除** - 重要数据总是使用软删除
4. **文件上传** - 验证文件类型和大小，使用对象存储
5. **版本控制** - 关键数据保留历史版本
6. **事务** - 批量操作使用数据库事务保证一致性
7. **异步处理** - 大批量操作考虑后台任务队列
