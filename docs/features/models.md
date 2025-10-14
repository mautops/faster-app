# 模型基类

Faster APP 提供了一套开箱即用的模型基类，覆盖 90% 的业务场景，让你无需重复编写常用字段。

## 🎯 设计理念

!!! quote "核心思想"
**通过组合基类，快速构建满足业务需求的数据模型，减少重复代码。**

## 📦 基类概览

| 基类            | 功能      | 主要字段                   | 适用场景              |
| --------------- | --------- | -------------------------- | --------------------- |
| `UUIDModel`     | UUID 主键 | `id` (UUID)                | 大部分业务表          |
| `DateTimeModel` | 时间戳    | `created_at`, `updated_at` | 需要追踪创建/更新时间 |
| `EnumModel`     | 枚举字段  | 动态枚举                   | 状态机、分类等        |
| `ScopeModel`    | 多租户    | `scope_id`                 | SaaS 应用             |

## 🔑 UUIDModel - UUID 主键

### 基本用法

```python
from faster_app.models.base import UUIDModel
from tortoise import fields

class User(UUIDModel):
    """用户模型"""
    username = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100)

    class Meta:
        table = "users"
```

生成的表结构：

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL
);
```

### 为什么使用 UUID？

!!! success "UUID 的优势" - ✅ **全局唯一**：分布式系统中无冲突 - ✅ **安全性高**：不会泄露数据量信息 - ✅ **可离线生成**：无需依赖数据库 - ✅ **便于合并数据**：多个数据源合并时无冲突

!!! warning "注意事项" - ❌ **存储空间**：比整型占用更多空间（16 字节） - ❌ **性能**：索引和查询略慢于整型 - ❌ **可读性**：不如自增 ID 直观

### 使用示例

```python
# 创建记录
user = await User.create(username="alice", email="alice@example.com")
print(user.id)  # UUID('550e8400-e29b-41d4-a716-446655440000')

# 查询记录
user = await User.get(id="550e8400-e29b-41d4-a716-446655440000")

# 批量查询
users = await User.filter(
    id__in=[
        "550e8400-e29b-41d4-a716-446655440000",
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
    ]
)
```

## ⏰ DateTimeModel - 时间戳

### 基本用法

```python
from faster_app.models.base import DateTimeModel
from tortoise import fields

class Article(DateTimeModel):
    """文章模型"""
    title = fields.CharField(max_length=200)
    content = fields.TextField()

    class Meta:
        table = "articles"
```

生成的表结构：

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 字段说明

- **`created_at`**: 创建时间，自动设置，不可修改
- **`updated_at`**: 更新时间，每次保存时自动更新

### 使用示例

```python
# 创建文章
article = await Article.create(
    title="Python 最佳实践",
    content="..."
)
print(article.created_at)  # 2024-01-01 10:00:00
print(article.updated_at)  # 2024-01-01 10:00:00

# 更新文章
article.title = "Python 进阶"
await article.save()
print(article.created_at)  # 2024-01-01 10:00:00 (不变)
print(article.updated_at)  # 2024-01-01 10:30:00 (自动更新)
```

### 查询示例

```python
from datetime import datetime, timedelta

# 查询最近 7 天的文章
week_ago = datetime.now() - timedelta(days=7)
recent_articles = await Article.filter(created_at__gte=week_ago)

# 查询今天更新的文章
today = datetime.now().date()
today_updated = await Article.filter(
    updated_at__gte=today,
    updated_at__lt=today + timedelta(days=1)
)
```

## 🎨 EnumModel - 枚举字段

### 基本用法

```python
from faster_app.models.base import EnumModel
from tortoise import fields
from enum import Enum

class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(EnumModel):
    """订单模型"""
    order_no = fields.CharField(max_length=50, unique=True)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    status = fields.CharEnumField(OrderStatus, default=OrderStatus.PENDING)

    class Meta:
        table = "orders"
```

### 使用示例

```python
# 创建订单
order = await Order.create(
    order_no="ORD20240101001",
    amount=99.99,
    status=OrderStatus.PENDING
)

# 更新状态
order.status = OrderStatus.PAID
await order.save()

# 查询特定状态的订单
pending_orders = await Order.filter(status=OrderStatus.PENDING)

# 查询多个状态的订单
active_orders = await Order.filter(
    status__in=[OrderStatus.PENDING, OrderStatus.PAID]
)
```

### 状态机模式

```python
class Order(EnumModel):
    """订单模型（带状态机）"""

    # 状态转换规则
    STATUS_TRANSITIONS = {
        OrderStatus.PENDING: [OrderStatus.PAID, OrderStatus.CANCELLED],
        OrderStatus.PAID: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
        OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
        OrderStatus.DELIVERED: [],
        OrderStatus.CANCELLED: [],
    }

    async def change_status(self, new_status: OrderStatus):
        """安全的状态转换"""
        allowed = self.STATUS_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"无法从 {self.status} 转换到 {new_status}"
            )

        self.status = new_status
        await self.save()
```

## 🏢 ScopeModel - 多租户

### 基本用法

```python
from faster_app.models.base import ScopeModel
from tortoise import fields

class Product(ScopeModel):
    """商品模型（多租户）"""
    name = fields.CharField(max_length=100)
    price = fields.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table = "products"
```

生成的表结构：

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    scope_id UUID NOT NULL,  -- 租户 ID
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    INDEX idx_scope_id (scope_id)
);
```

### 使用示例

```python
# 创建商品（指定租户）
product = await Product.create(
    scope_id="tenant-001",
    name="笔记本电脑",
    price=5999.00
)

# 查询当前租户的商品
tenant_products = await Product.filter(scope_id="tenant-001")

# 租户隔离查询
async def get_tenant_products(tenant_id: str):
    """获取指定租户的商品"""
    return await Product.filter(scope_id=tenant_id).all()
```

### 中间件集成

```python
# middleware/tenant.py
from faster_app.middleware.base import BaseMiddleware

class TenantMiddleware(BaseMiddleware):
    """租户识别中间件"""

    async def __call__(self, request, call_next):
        # 从请求头获取租户 ID
        tenant_id = request.headers.get("X-Tenant-ID")

        # 存储到请求上下文
        request.state.tenant_id = tenant_id

        response = await call_next(request)
        return response

# 在路由中使用
@router.post("/products")
async def create_product(
    request: Request,
    name: str,
    price: float
):
    """创建商品（自动隔离）"""
    product = await Product.create(
        scope_id=request.state.tenant_id,
        name=name,
        price=price
    )
    return product
```

## 🎭 组合使用

### 常见组合

```python
from faster_app.models.base import UUIDModel, DateTimeModel
from tortoise import fields

# 最常用组合：UUID + 时间戳
class User(UUIDModel, DateTimeModel):
    """用户模型"""
    username = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100)

    class Meta:
        table = "users"

# 完整组合：UUID + 时间戳 + 多租户
class Order(UUIDModel, DateTimeModel, ScopeModel):
    """订单模型（多租户）"""
    order_no = fields.CharField(max_length=50)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table = "orders"
```

### 自定义基类

```python
from faster_app.models.base import UUIDModel, DateTimeModel
from tortoise import fields

class BaseModel(UUIDModel, DateTimeModel):
    """项目通用基类"""

    is_deleted = fields.BooleanField(default=False, description="软删除")
    remark = fields.TextField(null=True, description="备注")

    class Meta:
        abstract = True  # 抽象模型，不创建表

class User(BaseModel):
    """用户模型（继承通用字段）"""
    username = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100)

    class Meta:
        table = "users"
```

## 📝 最佳实践

### 1. 选择合适的主键类型

```python
# ✅ 推荐：大多数场景使用 UUID
class User(UUIDModel):
    pass

# ⚠️ 特殊场景：超高性能要求，使用自增 ID
class Log(Model):
    id = fields.BigIntField(pk=True)
```

### 2. 始终添加时间戳

```python
# ✅ 推荐：几乎所有表都应该有时间戳
class Article(UUIDModel, DateTimeModel):
    pass

# ❌ 不推荐：缺少审计信息
class Article(UUIDModel):
    pass
```

### 3. 合理使用枚举

```python
# ✅ 推荐：固定的状态值使用枚举
class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"

class Order(Model):
    status = fields.CharEnumField(OrderStatus)

# ❌ 不推荐：使用字符串或整数
class Order(Model):
    status = fields.CharField(max_length=20)  # 容易出错
```

### 4. 多租户隔离

```python
# ✅ 推荐：使用 ScopeModel
class Product(ScopeModel):
    pass

# ⚠️ 手动实现（灵活但容易遗漏）
class Product(Model):
    tenant_id = fields.UUIDField()
```

## 下一步

- 学习 [路由管理](routes.md)
- 了解 [CRUD 工具](../api/utils.md)
- 掌握 [数据库最佳实践](../best-practices/database.md)
