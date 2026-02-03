# 数据查询

Tortoise ORM 提供丰富的查询 API，支持基础查询、高级过滤、聚合统计等操作。

## 基础查询方法

### all() - 获取所有记录

```python
articles = await Article.all()
articles = await Article.all().order_by("-created_at").limit(10)
```

### get() - 获取单条记录

```python
# 按 ID
article = await Article.get(id=article_id)

# 按其他字段
article = await Article.get(slug="python-tutorial")

# 不存在会抛出异常
try:
    article = await Article.get(id="不存在")
except Article.DoesNotExist:
    print("未找到")
```

### get_or_none() - 安全获取

```python
article = await Article.get_or_none(slug="python-tutorial")
if article:
    print(article.title)
```

### filter() - 过滤

```python
# 单条件
articles = await Article.filter(status="published")

# 多条件（AND）
articles = await Article.filter(status="published", author="张三")

# 链式过滤
articles = await Article.filter(status="published").filter(view_count__gt=100)
```

### exclude() - 排除

```python
articles = await Article.exclude(status="draft")
articles = await Article.exclude(status="draft").exclude(is_deleted=True)
```

### first() / count() / exists()

```python
# 第一条
article = await Article.filter(status="published").first()

# 计数
count = await Article.filter(status="published").count()

# 检查存在
has_articles = await Article.filter(author="张三").exists()
```

## 比较操作符

```python
# 精确匹配
articles = await Article.filter(status="published")

# 大于 / 大于等于
articles = await Article.filter(view_count__gt=100)
articles = await Article.filter(view_count__gte=100)

# 小于 / 小于等于
articles = await Article.filter(view_count__lt=100)
articles = await Article.filter(view_count__lte=100)

# 不等于
articles = await Article.filter(status__not="draft")

# 范围
from datetime import datetime, timedelta
start = datetime.now() - timedelta(days=7)
articles = await Article.filter(created_at__range=(start, datetime.now()))
```

## 字符串操作符

```python
# 包含（区分大小写）
articles = await Article.filter(title__contains="Python")

# 包含（不区分大小写）
articles = await Article.filter(title__icontains="python")

# 开始于
articles = await Article.filter(title__startswith="如何")

# 结束于
articles = await Article.filter(title__endswith="指南")
```

## 列表操作符

```python
# 在列表中
articles = await Article.filter(status__in=["published", "featured"])

# 不在列表中
articles = await Article.filter(status__not_in=["draft", "archived"])
```

## 空值检查

```python
# 为空
articles = await Article.filter(published_at__isnull=True)

# 不为空
articles = await Article.filter(published_at__isnull=False)
```

## 排序

```python
# 升序
articles = await Article.all().order_by("created_at")

# 降序
articles = await Article.all().order_by("-created_at")

# 多字段排序
articles = await Article.all().order_by("-is_featured", "-created_at")
```

## 限制和偏移

```python
# 限制数量
articles = await Article.all().limit(10)

# 偏移
articles = await Article.all().offset(20).limit(10)

# 切片
articles = await Article.all()[10:20]
```

## 值查询

### values() - 字典列表

```python
# 返回字典列表
articles = await Article.all().values("id", "title", "status")
# [{"id": "...", "title": "...", "status": "..."}, ...]

# 跨关系查询
articles = await Article.all().values("title", "author__name")
```

### values_list() - 元组列表

```python
# 返回元组列表
titles = await Article.all().values_list("title", flat=False)
# [("标题1",), ("标题2",), ...]

# flat=True 返回扁平列表
titles = await Article.all().values_list("title", flat=True)
# ["标题1", "标题2", ...]
```

## 去重

```python
# 去除重复
authors = await Article.all().distinct().values_list("author", flat=True)
```

## Q 对象 - 复杂查询

### OR 查询

```python
from tortoise.expressions import Q

# 状态为 published 或 featured
articles = await Article.filter(
    Q(status="published") | Q(status="featured")
)
```

### AND 查询

```python
# 等同于多个 filter
articles = await Article.filter(
    Q(status="published") & Q(view_count__gt=100)
)
```

### 复杂组合

```python
# (A AND B) OR C
articles = await Article.filter(
    (Q(status="published") & Q(view_count__gt=100)) |
    Q(is_featured=True)
)

# NOT 查询
articles = await Article.filter(~Q(status="draft"))
```

## 聚合查询

```python
from tortoise.functions import Count, Sum, Avg, Max, Min

# 计数
authors = await Author.annotate(
    article_count=Count("articles")
).values("name", "article_count")

# 求和
result = await Article.all().annotate(
    total_views=Sum("view_count")
).values("total_views")

# 平均值
result = await Article.filter(status="published").annotate(
    avg_rating=Avg("rating")
).values("avg_rating")

# 最大/最小值
result = await Article.all().annotate(
    max_views=Max("view_count"),
    min_views=Min("view_count")
).values("max_views", "min_views")
```

## 分组查询

```python
# 按状态分组统计
results = await Article.group_by("status").annotate(
    count=Count("id")
).values("status", "count")

# 多字段分组
results = await Article.group_by("author", "status").annotate(
    count=Count("id"),
    total_views=Sum("view_count")
).values("author", "status", "count", "total_views")
```

## 批量操作

### bulk_create() - 批量创建

```python
articles = [
    Article(title=f"文章{i}", content=f"内容{i}")
    for i in range(100)
]
await Article.bulk_create(articles)
```

### update() - 批量更新

```python
# 更新符合条件的记录
count = await Article.filter(status="draft").update(
    status="published",
    published_at=datetime.now()
)
```

### delete() - 批量删除

```python
deleted_count = await Article.filter(status="archived").delete()
```

## 原始 SQL

```python
from tortoise import Tortoise

# 获取连接
conn = Tortoise.get_connection("default")

# 执行查询
results = await conn.execute_query_dict(
    "SELECT author, COUNT(*) as count FROM articles GROUP BY author"
)

# 带参数（防止 SQL 注入）
results = await conn.execute_query_dict(
    "SELECT * FROM articles WHERE status = ? AND view_count > ?",
    ["published", 100]
)
```

## 事务

```python
from tortoise.transactions import in_transaction

# 自动事务
async with in_transaction():
    article = await Article.create(title="测试")
    await article.tags.add(tag1, tag2)
    # 如果出错，自动回滚
```

## 性能优化技巧

### 1. 只查询需要的字段

```python
# ❌ 查询所有字段
articles = await Article.all()

# ✅ 只查询需要的字段
articles = await Article.all().values("id", "title")
```

### 2. 使用 count() 而非 len()

```python
# ❌ 加载所有数据再计数
count = len(await Article.all())

# ✅ 数据库层面计数
count = await Article.all().count()
```

### 3. 使用 exists() 检查存在

```python
# ❌ 查询再判断
articles = await Article.filter(author="张三")
if articles:
    ...

# ✅ 直接检查存在
if await Article.filter(author="张三").exists():
    ...
```

### 4. 批量查询

```python
# ❌ 循环查询
articles = []
for id in ids:
    article = await Article.get(id=id)
    articles.append(article)

# ✅ 一次查询
articles = await Article.filter(id__in=ids)
```

### 5. 使用 prefetch_related

```python
# ❌ N+1 查询
articles = await Article.all()
for article in articles:
    print(article.author.name)  # 每次查询

# ✅ 预取关系
articles = await Article.all().prefetch_related("author")
for article in articles:
    print(article.author.name)  # 无查询
```

## 查询链式组合

```python
# 组合多个条件
articles = (
    await Article.filter(status="published")
    .exclude(is_deleted=True)
    .filter(view_count__gte=100)
    .prefetch_related("author", "tags")
    .order_by("-created_at")
    .limit(10)
)
```

## 调试查询

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 会打印执行的 SQL
articles = await Article.filter(status="published")
```

掌握这些查询方法，可以高效地操作数据库。
# 自定义方法和常见模式

为模型添加自定义方法，封装业务逻辑，并使用常见设计模式。

## 自定义方法

### 实例方法

操作单个对象的方法：

```python
class Article(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    status: str = fields.CharField(max_length=20, default="draft")
    view_count: int = fields.IntField(default=0)
    
    async def publish(self):
        """发布文章"""
        self.status = "published"
        self.published_at = datetime.now()
        await self.save()
    
    async def increment_views(self):
        """增加浏览量"""
        self.view_count += 1
        await self.save(update_fields=["view_count"])
    
    async def can_edit_by(self, user_id: str) -> bool:
        """检查用户是否可以编辑"""
        if self.author_id == user_id:
            return True
        user = await User.get(id=user_id)
        return user.role == "admin"
```

### 类方法

操作整个模型类：

```python
class Article(UUIDModel, DateTimeModel):
    @classmethod
    async def get_published(cls):
        """获取所有已发布文章"""
        return await cls.filter(status="published").order_by("-published_at")
    
    @classmethod
    async def get_trending(cls, days: int = 7, limit: int = 10):
        """获取热门文章"""
        date_from = datetime.now() - timedelta(days=days)
        return await cls.filter(
            created_at__gte=date_from,
            status="published"
        ).order_by("-view_count").limit(limit)
    
    @classmethod
    async def search(cls, keyword: str):
        """搜索文章"""
        return await cls.filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ).filter(status="published")
```

### 属性方法

提供计算字段：

```python
class Article(UUIDModel, DateTimeModel):
    content: str = fields.TextField()
    status: str = fields.CharField(max_length=20)
    published_at: datetime = fields.DatetimeField(null=True)
    
    @property
    def is_published(self) -> bool:
        """是否已发布"""
        return self.status == "published"
    
    @property
    def word_count(self) -> int:
        """字数统计"""
        return len(self.content)
    
    @property
    def read_time(self) -> int:
        """阅读时间（分钟）"""
        words = len(self.content.split())
        return max(1, words // 200)
```

### 生命周期钩子

在保存/删除前后执行自定义逻辑：

```python
class Article(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    slug: str = fields.CharField(max_length=200, unique=True)
    
    async def save(self, *args, **kwargs):
        """保存前自动处理"""
        # 生成 slug
        if not self.slug:
            from slugify import slugify
            self.slug = slugify(self.title)
        
        # 调用父类 save
        await super().save(*args, **kwargs)
        
        # 保存后的操作
        await self.update_search_index()
    
    async def delete(self, *args, **kwargs):
        """删除前清理"""
        await self.cleanup_related_data()
        await super().delete(*args, **kwargs)
        await self.remove_from_search_index()
```

## 常见模式

### 软删除模式

不物理删除数据，标记为已删除：

```python
class Article(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    deleted_at: datetime = fields.DatetimeField(null=True)
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
    
    async def soft_delete(self):
        """软删除"""
        self.deleted_at = datetime.now()
        await self.save(update_fields=["deleted_at"])
    
    async def restore(self):
        """恢复"""
        self.deleted_at = None
        await self.save(update_fields=["deleted_at"])
    
    @classmethod
    async def get_active(cls):
        """获取未删除的记录"""
        return await cls.filter(deleted_at__isnull=True)
```

### 版本控制模式

记录数据变更历史：

```python
class Article(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    version: int = fields.IntField(default=1)
    
    async def save(self, *args, **kwargs):
        """保存时自动增加版本号"""
        if self.id:  # 更新时
            self.version += 1
        await super().save(*args, **kwargs)

class ArticleHistory(UUIDModel):
    """历史记录"""
    article: fields.ForeignKeyField = fields.ForeignKeyField("models.Article")
    version: int = fields.IntField()
    title: str = fields.CharField(max_length=200)
    content: str = fields.TextField()
    changed_at: datetime = fields.DatetimeField(auto_now_add=True)
    changed_by: str = fields.CharField(max_length=100)
```

### 审计追踪模式

记录谁创建、谁修改：

```python
class AuditModel(UUIDModel):
    """审计基类"""
    created_by: str = fields.CharField(max_length=100)
    updated_by: str = fields.CharField(max_length=100)
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    async def save(self, user_id: str = None, *args, **kwargs):
        """保存时记录操作者"""
        user_id = user_id or get_current_user_id()
        if not self.id:
            self.created_by = user_id
        self.updated_by = user_id
        await super().save(*args, **kwargs)

class Article(AuditModel):
    title: str = fields.CharField(max_length=200)
```

### 状态机模式

管理对象的状态转换：

```python
from enum import IntEnum

class ArticleStatus(IntEnum):
    DRAFT = 0
    UNDER_REVIEW = 1
    PUBLISHED = 2
    ARCHIVED = 3

class Article(UUIDModel, DateTimeModel):
    title: str = fields.CharField(max_length=200)
    status: int = fields.IntField(default=ArticleStatus.DRAFT)
    
    @property
    def status_name(self) -> str:
        return ArticleStatus(self.status).name
    
    async def submit_for_review(self, user_id: str):
        """提交审核"""
        if self.status != ArticleStatus.DRAFT:
            raise ValueError("只能提交草稿")
        self.status = ArticleStatus.UNDER_REVIEW
        await self.save()
        await self.notify_reviewers()
    
    async def publish(self, user_id: str):
        """发布"""
        if self.status != ArticleStatus.UNDER_REVIEW:
            raise ValueError("只能发布审核通过的文章")
        self.status = ArticleStatus.PUBLISHED
        self.published_at = datetime.now()
        await self.save()
    
    def can_transition_to(self, new_status: ArticleStatus) -> bool:
        """检查是否可以转换到新状态"""
        transitions = {
            ArticleStatus.DRAFT: [ArticleStatus.UNDER_REVIEW],
            ArticleStatus.UNDER_REVIEW: [ArticleStatus.PUBLISHED, ArticleStatus.DRAFT],
            ArticleStatus.PUBLISHED: [ArticleStatus.ARCHIVED],
            ArticleStatus.ARCHIVED: [],
        }
        return new_status in transitions.get(ArticleStatus(self.status), [])
```

### 树形结构模式

实现分类、评论等树形结构：

```python
class Category(UUIDModel):
    name: str = fields.CharField(max_length=100)
    parent: fields.ForeignKeyField = fields.ForeignKeyField(
        "models.Category",
        related_name="children",
        null=True,
        on_delete=fields.CASCADE
    )
    
    async def get_ancestors(self):
        """获取所有祖先"""
        ancestors = []
        current = self
        while current.parent_id:
            await current.fetch_related("parent")
            current = current.parent
            ancestors.append(current)
        return ancestors
    
    async def get_descendants(self):
        """获取所有后代"""
        descendants = []
        children = await self.children.all()
        for child in children:
            descendants.append(child)
            descendants.extend(await child.get_descendants())
        return descendants
```

### 计数器缓存模式

缓存统计数据：

```python
class Author(UUIDModel):
    name: str = fields.CharField(max_length=100)
    article_count: int = fields.IntField(default=0)
    total_views: int = fields.IntField(default=0)
    
    async def update_counters(self):
        """更新计数器"""
        self.article_count = await Article.filter(author_id=self.id).count()
        result = await Article.filter(author_id=self.id).annotate(
            total=Sum("view_count")
        ).values("total")
        self.total_views = result[0]["total"] if result else 0
        await self.save(update_fields=["article_count", "total_views"])

class Article(UUIDModel):
    async def save(self, *args, **kwargs):
        """保存时更新作者计数器"""
        is_new = self.id is None
        await super().save(*args, **kwargs)
        if is_new:
            author = await Author.get(id=self.author_id)
            author.article_count += 1
            await author.save(update_fields=["article_count"])
```

## 最佳实践

### 1. 方法命名

- 实例方法：动词开头（publish、archive）
- 类方法：get_ 开头（get_published、get_trending）
- 属性方法：名词或 is_/has_ 开头

### 2. 异步方法

- 涉及数据库操作的用 async
- 纯计算用同步方法

### 3. 错误处理

```python
async def publish(self):
    if self.status != "draft":
        raise ValueError("只能发布草稿状态的文章")
    # ...
```

### 4. 性能考虑

- 避免在属性中查询数据库
- 复杂计算考虑缓存
- 使用 update_fields 只更新变化的字段

### 5. 单一职责

- 每个方法只做一件事
- 复杂逻辑拆分为多个方法

通过自定义方法和设计模式，可以构建清晰、可维护的业务逻辑。
