# 基础模型类

## UUIDModel

UUID 主键模型：

```python
from faster_app.models.base import UUIDModel

class Article(UUIDModel):
    title: str = Field(..., max_length=200)
    content: str = Field(...)
```

**提供功能：**
- `id` (UUID) - 自动生成的主键
- CRUD 方法：create, get, all, filter, save, delete

## DateTimeModel

自动时间戳跟踪：

```python
from faster_app.models.base import DateTimeModel

class Article(DateTimeModel):
    title: str = Field(...)
```

**提供字段：**
- `created_at` - 创建时间（自动）
- `updated_at` - 更新时间（自动）

## EnumModel

枚举字段支持：

```python
from faster_app.models.base import EnumModel
from enum import IntEnum

class PostStatus(IntEnum):
    DRAFT = 0
    PUBLISHED = 1

class Post(EnumModel):
    status: int = Field(default=PostStatus.DRAFT)
    
    @property
    def status_name(self):
        return PostStatus(self.status).name
```

## ScopeModel

多租户支持：

```python
from faster_app.models.base import ScopeModel

class Article(ScopeModel):
    title: str = Field(...)
    
    class Meta:
        scope_field = "tenant_id"
```

**用法：**
```python
ScopeModel.set_scope("tenant_123")
articles = await Article.all()  # 自动过滤
```

## 组合使用

标准模式（推荐）：

```python
class Article(UUIDModel, DateTimeModel):
    """UUID + 时间戳"""
    title: str = Field(...)
```

多租户模式：

```python
class Article(UUIDModel, DateTimeModel, ScopeModel):
    """UUID + 时间戳 + 租户"""
    title: str = Field(...)
```
# 字段类型

Tortoise ORM 支持丰富的字段类型，满足各种数据建模需求。

## 字符串字段

### CharField - 短文本

用于存储固定最大长度的字符串：

```python
from tortoise import fields

class Article(UUIDModel):
    # 基础用法
    title: str = fields.CharField(max_length=200)
    
    # 唯一约束
    slug: str = fields.CharField(max_length=200, unique=True)
    
    # 可选字段
    subtitle: str = fields.CharField(max_length=200, null=True)
    
    # 带默认值
    status: str = fields.CharField(max_length=20, default="draft")
    
    # 添加索引（提高查询性能）
    author: str = fields.CharField(max_length=100, index=True)
    
    # 带描述（用于 API 文档）
    category: str = fields.CharField(
        max_length=50,
        description="文章分类"
    )
```

**注意**：超过 max_length 的值会在数据库层面被截断。

### TextField - 长文本

用于存储大量文本内容：

```python
class Article(UUIDModel):
    # 文章内容
    content: str = fields.TextField()
    
    # Markdown 格式
    markdown_content: str = fields.TextField(null=True)
    
    # 富文本 HTML
    html_content: str = fields.TextField(default="")
```

**TextField vs CharField**：
- TextField 没有长度限制
- TextField 不能设置 unique
- TextField 不建议添加索引（性能差）

## 数字字段

### IntField - 整数

```python
class Article(UUIDModel):
    # 浏览次数
    view_count: int = fields.IntField(default=0)
    
    # 点赞数
    like_count: int = fields.IntField(default=0, ge=0)  # 大于等于0
    
    # 排序值
    sort_order: int = fields.IntField(default=0, index=True)
```

### FloatField - 浮点数

```python
class Product(UUIDModel):
    # 评分（0.0-5.0）
    rating: float = fields.FloatField(default=0.0)
    
    # 重量（千克）
    weight: float = fields.FloatField(null=True)
```

### DecimalField - 精确小数

用于需要精确计算的场景（如货币）：

```python
from decimal import Decimal

class Product(UUIDModel):
    # 价格（精确到分）
    price: Decimal = fields.DecimalField(
        max_digits=10,    # 总位数
        decimal_places=2, # 小数位数
        default=Decimal("0.00")
    )
    
    # 折扣率
    discount: Decimal = fields.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00")
    )
```

**为什么用 DecimalField**：
- FloatField 有精度问题：`0.1 + 0.2 != 0.3`
- DecimalField 精确计算，适合金融场景

## 布尔字段

```python
class Article(UUIDModel):
    # 是否已发布
    is_published: bool = fields.BooleanField(default=False)
    
    # 是否推荐
    is_featured: bool = fields.BooleanField(default=False, index=True)
    
    # 是否允许评论
    allow_comments: bool = fields.BooleanField(default=True)
```

## 日期时间字段

### DatetimeField - 日期时间

```python
from datetime import datetime

class Article(UUIDModel):
    # 发布时间
    published_at: datetime = fields.DatetimeField(null=True)
    
    # 自动设置当前时间
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    
    # 每次保存时更新
    updated_at: datetime = fields.DatetimeField(auto_now=True)
```

### DateField - 日期

```python
from datetime import date

class Event(UUIDModel):
    # 活动日期
    event_date: date = fields.DateField()
    
    # 截止日期
    deadline: date = fields.DateField(null=True)
```

### TimeField - 时间

```python
from datetime import time

class Schedule(UUIDModel):
    # 开始时间
    start_time: time = fields.TimeField()
    
    # 结束时间
    end_time: time = fields.TimeField()
```

## JSON 字段

存储 JSON 数据：

```python
class Article(UUIDModel):
    # 元数据
    metadata: dict = fields.JSONField(default=dict)
    
    # 标签列表
    tags: list = fields.JSONField(default=list)
    
    # 配置信息
    settings: dict = fields.JSONField(default=lambda: {"theme": "default"})
```

**用法示例**：
```python
article = await Article.create(
    title="测试",
    metadata={"author": "张三", "category": "技术"},
    tags=["Python", "FastAPI"]
)

# 访问
print(article.metadata["author"])  # 张三
print(article.tags[0])  # Python
```

## 枚举字段

使用 IntField 配合 Python Enum：

```python
from enum import IntEnum

class ArticleStatus(IntEnum):
    DRAFT = 0
    PUBLISHED = 1
    ARCHIVED = 2

class Article(UUIDModel):
    status: int = fields.IntField(default=ArticleStatus.DRAFT)
    
    @property
    def status_name(self):
        return ArticleStatus(self.status).name
```

## 字段选项总结

### 通用选项

```python
class Article(UUIDModel):
    field = fields.CharField(
        max_length=200,
        
        # 空值
        null=True,              # 允许数据库 NULL
        default="默认值",        # 默认值
        
        # 约束
        unique=True,            # 唯一约束
        index=True,             # 创建索引
        
        # 文档
        description="字段说明",  # API 文档描述
        
        # 验证（Pydantic 层面）
        ge=0,                   # 大于等于
        le=100,                 # 小于等于
        gt=0,                   # 大于
        lt=100,                 # 小于
    )
```

### 特殊选项

```python
# 自动时间戳
created_at = fields.DatetimeField(auto_now_add=True)  # 创建时设置
updated_at = fields.DatetimeField(auto_now=True)       # 保存时更新

# 主键
id = fields.IntField(pk=True)  # 主键

# 生成的字段（计算字段）
# Tortoise ORM 不直接支持，需在应用层实现
```

## 最佳实践

1. **选择合适的字段类型**
   - 固定长度文本用 CharField
   - 长文本用 TextField
   - 金钱用 DecimalField
   - 计数用 IntField

2. **合理使用索引**
   - 频繁查询的字段添加 index=True
   - 不要过度使用（影响写入性能）

3. **NULL vs 空值 vs 默认值**
   - 可选字段：null=True
   - 布尔字段：避免 NULL，使用 default=False
   - 字符串：用 default="" 而非 NULL

4. **命名约定**
   - 使用 snake_case：`created_at` 而非 `createdAt`
   - 布尔字段用 `is_` 或 `has_` 前缀
   - 时间字段用 `_at` 或 `_date` 后缀

5. **添加描述**
   - 为重要字段添加 description
   - 便于 API 文档生成和团队协作
# 模型关系

Tortoise ORM 支持三种关系类型：ForeignKey（多对一）、ManyToMany（多对多）、OneToOne（一对一）。

## ForeignKey - 多对一关系

ForeignKey 用于建立多对一（Many-to-One）关系。

### 基础定义

```python
from tortoise import fields

class Author(UUIDModel):
    name: str = fields.CharField(max_length=100)

class Article(UUIDModel):
    title: str = fields.CharField(max_length=200)
    author: fields.ForeignKeyField = fields.ForeignKeyField(
        "models.Author",
        related_name="articles",
        on_delete=fields.CASCADE
    )
```

### 创建和查询

```python
# 创建
author = await Author.create(name="张三")
article = await Article.create(title="文章", author=author)

# 正向查询
article = await Article.get(id=id).prefetch_related("author")
print(article.author.name)

# 反向查询
author = await Author.get(id=id).prefetch_related("articles")
for article in author.articles:
    print(article.title)

# 跨关系查询
articles = await Article.filter(author__name="张三")
```

### on_delete 选项

- **CASCADE** - 级联删除
- **SET_NULL** - 设为 NULL（需要 null=True）
- **RESTRICT** - 限制删除
- **SET_DEFAULT** - 设为默认值

### 避免 N+1 查询

```python
# ❌ 错误：N+1 查询
articles = await Article.all()
for article in articles:
    print(article.author.name)  # 每次循环查询一次

# ✅ 正确：使用 prefetch_related
articles = await Article.all().prefetch_related("author")
for article in articles:
    print(article.author.name)  # 无额外查询
```

## ManyToMany - 多对多关系

ManyToMany 用于建立多对多关系，如文章和标签。

### 基础定义

```python
class Tag(UUIDModel):
    name: str = fields.CharField(max_length=50, unique=True)

class Article(UUIDModel):
    title: str = fields.CharField(max_length=200)
    tags: fields.ManyToManyField = fields.ManyToManyField(
        "models.Tag",
        related_name="articles",
        through="article_tags"
    )
```

### 添加和移除关系

```python
# 添加
article = await Article.create(title="Python 教程")
tag = await Tag.create(name="Python")
await article.tags.add(tag)

# 添加多个
tags = await Tag.filter(name__in=["Python", "FastAPI"])
await article.tags.add(*tags)

# 移除
await article.tags.remove(tag)

# 清空
await article.tags.clear()
```

### 查询

```python
# 正向查询
article = await Article.get(id=id).prefetch_related("tags")
for tag in article.tags:
    print(tag.name)

# 反向查询
tag = await Tag.get(name="Python").prefetch_related("articles")
for article in tag.articles:
    print(article.title)

# 跨关系查询
articles = await Article.filter(tags__name="Python")
```

### 自定义中间表

```python
class ArticleTag(UUIDModel):
    article: fields.ForeignKeyField = fields.ForeignKeyField("models.Article")
    tag: fields.ForeignKeyField = fields.ForeignKeyField("models.Tag")
    created_at: datetime = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "article_tags"
        unique_together = (("article", "tag"),)

# 访问中间表
article_tags = await ArticleTag.filter(article_id=article.id)
```

## OneToOne - 一对一关系

OneToOne 用于建立一对一关系，每个对象只能关联一个另一个对象。

### 基础定义

```python
class User(UUIDModel):
    username: str = fields.CharField(max_length=50, unique=True)

class Profile(UUIDModel):
    user: fields.OneToOneField = fields.OneToOneField(
        "models.User",
        related_name="profile",
        on_delete=fields.CASCADE
    )
    bio: str = fields.TextField(null=True)
```

### 创建和访问

```python
# 创建
user = await User.create(username="zhangsan")
profile = await Profile.create(user=user, bio="工程师")

# 正向访问
profile = await Profile.get(id=id).prefetch_related("user")
print(profile.user.username)

# 反向访问
user = await User.get(id=id).prefetch_related("profile")
print(user.profile.bio)
```

### 使用场景

1. **用户和个人资料** - 核心数据和扩展资料分离
2. **文章和详细内容** - 列表页只加载摘要，详情页加载完整内容
3. **产品和规格** - 基础信息和详细规格分离
4. **设置和配置** - 主对象和配置分离

### OneToOne vs ForeignKey

- **OneToOne**：双向唯一，用于数据分离、扩展
- **ForeignKey**：多对一，用于层级、分类关系

## 关系查询最佳实践

### 1. 总是使用 prefetch_related

```python
# 避免 N+1 查询
articles = await Article.all().prefetch_related(
    "author",
    "category",
    "tags"
)
```

### 2. 只查询需要的字段

```python
# 使用 values() 减少数据传输
articles = await Article.all().values(
    "id",
    "title",
    "author__name"
)
```

### 3. 批量操作

```python
# 批量添加关系
article = await Article.get(id=id)
tags = await Tag.filter(name__in=["tag1", "tag2"])
await article.tags.add(*tags)
```

### 4. 聚合统计

```python
from tortoise.functions import Count

# 统计每个作者的文章数
authors = await Author.annotate(
    article_count=Count("articles")
).values("name", "article_count")
```

### 5. 去重查询

```python
# 跨关系查询时去重
authors = await Author.filter(
    articles__status="published"
).distinct()
```

## 性能优化

### 问题：N+1 查询

```python
# ❌ 每次循环都查询数据库
articles = await Article.all()
for article in articles:
    print(article.author.name)      # 查询1次
    for tag in article.tags:         # 查询N次
        print(tag.name)
```

### 解决：预取关系

```python
# ✅ 只查询3次（articles + authors + tags）
articles = await Article.all().prefetch_related(
    "author",
    "tags"
)
for article in articles:
    print(article.author.name)       # 无查询
    for tag in article.tags:          # 无查询
        print(tag.name)
```

### 复杂预取

```python
# 预取嵌套关系
articles = await Article.all().prefetch_related(
    "author",
    "author__organization",
    "comments__user"
)
```

## 常见错误

### 1. 忘记 prefetch

```python
# ❌ N+1 问题
articles = await Article.all()

# ✅ 正确
articles = await Article.all().prefetch_related("author")
```

### 2. 在循环中查询

```python
# ❌ 错误
for id in article_ids:
    article = await Article.get(id=id)

# ✅ 正确
articles = await Article.filter(id__in=article_ids)
```

### 3. 不使用 distinct

```python
# ❌ 可能返回重复记录
authors = await Author.filter(articles__status="published")

# ✅ 正确
authors = await Author.filter(articles__status="published").distinct()
```

掌握这三种关系类型和最佳实践，可以高效地构建复杂的数据模型。
