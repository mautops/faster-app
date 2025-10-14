# CRUD Router - 三种开发模式

Faster APP 提供了强大的 CRUD Router 功能，让你可以用**最少 5 行代码**完成标准的增删改查接口。Demo 应用展示了三种不同的开发模式，满足从快速原型到复杂业务的各种需求。

## 📊 三种模式对比

| 模式         | 代码量   | 灵活性     | 适用场景            | 推荐度     |
| ------------ | -------- | ---------- | ------------------- | ---------- |
| **快速模式** | 5 行     | ⭐         | 快速原型、标准 CRUD | ⭐⭐⭐     |
| **平衡模式** | 10-20 行 | ⭐⭐⭐     | 大多数业务场景      | ⭐⭐⭐⭐⭐ |
| **完全控制** | 50+ 行   | ⭐⭐⭐⭐⭐ | 复杂业务逻辑        | ⭐⭐⭐     |

---

## 🚀 模式一：快速模式

**5 行代码完成标准 CRUD**，适合快速原型开发和标准业务场景。

### 代码示例

```python
from faster_app.apps.demo.models import DemoModel
from faster_app.utils.crud import CRUDRouter

# 创建路由 - 自动生成所有 CRUD 接口
demo_quick_router = CRUDRouter(
    model=DemoModel,
    prefix="/demos-quick",
    tags=["Demo - 快速模式"],
    operations="CRUDL",  # C:创建 R:读取 U:更新 D:删除 L:列表
).get_router()
```

### 自动生成的接口

| 方法     | 路径                | 功能             | 操作符 |
| -------- | ------------------- | ---------------- | ------ |
| `GET`    | `/demos-quick/`     | 列表查询（分页） | L      |
| `POST`   | `/demos-quick/`     | 创建记录         | C      |
| `GET`    | `/demos-quick/{id}` | 查询单个         | R      |
| `PUT`    | `/demos-quick/{id}` | 更新记录         | U      |
| `DELETE` | `/demos-quick/{id}` | 删除记录         | D      |

### 参数说明

```python
CRUDRouter(
    model=DemoModel,              # 必填：Tortoise ORM 模型
    prefix="/demos-quick",        # 必填：路由前缀
    tags=["Demo"],                # 可选：Swagger 标签
    operations="CRUDL",           # 可选：指定开放的操作，默认全部
    create_schema=None,           # 可选：自定义创建 Schema
    update_schema=None,           # 可选：自定义更新 Schema
    response_schema=None,         # 可选：自定义响应 Schema
    paginate=True,                # 可选：是否启用分页，默认 True
)
```

### 操作符组合

你可以通过 `operations` 参数灵活控制开放哪些接口：

```python
# 只读模式：仅查询和列表
operations="RL"

# 不允许删除：创建、读取、更新、列表
operations="CRUL"

# 仅创建和查询
operations="CR"

# 完整 CRUD（默认值）
operations="CRUDL"
```

### 适用场景

- ✅ 快速原型开发
- ✅ 标准的数据管理界面
- ✅ 内部管理系统
- ✅ 简单的资源 API

---

## ⚖️ 模式二：平衡模式（推荐）

使用**自定义 Schema**，保留灵活性，适合大多数业务场景。

### 代码示例

```python
from faster_app.apps.demo.models import DemoModel
from faster_app.apps.demo.schemas import DemoCreate, DemoUpdate
from faster_app.utils.crud import CRUDRouter

# 使用自定义 Schema
demo_balanced_router = CRUDRouter(
    model=DemoModel,
    create_schema=DemoCreate,  # 自定义创建 Schema（带验证）
    update_schema=DemoUpdate,  # 自定义更新 Schema（带验证）
    prefix="/demos",
    tags=["Demo - 平衡模式"],
).get_router()


# 在自动生成的基础上，添加自定义路由
@demo_balanced_router.get("/statistics")
async def get_statistics():
    """获取统计信息 - 自定义端点"""
    total = await DemoModel.all().count()
    active = await DemoModel.filter(status=1).count()

    return {
        "total": total,
        "active": active,
    }


@demo_balanced_router.post("/batch-create")
async def batch_create(items_data: list[DemoCreate]):
    """批量创建 - 自定义端点"""
    created_records = []
    for create_data in items_data:
        record = await DemoModel.create(**create_data.model_dump())
        created_records.append(record)

    return {"count": len(created_records)}
```

### 自定义 Schema 示例

#### 创建 Schema

```python
from pydantic import BaseModel, Field, field_validator

class DemoCreate(BaseModel):
    """创建 Demo 的请求 Schema - 自定义验证和描述"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Demo 名称",
        examples=["我的第一个 Demo"],
    )
    status: int = Field(
        default=1,
        description="状态：1-激活，0-未激活",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """自定义验证：名称不能包含特殊字符"""
        if any(char in v for char in ["<", ">", "&", "'"]):
            raise ValueError("名称不能包含特殊字符")
        return v.strip()
```

#### 更新 Schema

```python
class DemoUpdate(BaseModel):
    """更新 Demo 的请求 Schema - 所有字段可选"""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Demo 名称"
    )
    status: int | None = Field(
        None,
        description="状态：1-激活，0-未激活"
    )
```

### 核心优势

| 特性           | 说明                               |
| -------------- | ---------------------------------- |
| **自动 CRUD**  | 标准接口自动生成，省时省力         |
| **自定义验证** | Schema 支持 Pydantic 验证规则      |
| **扩展路由**   | 可以在自动路由基础上添加自定义端点 |
| **类型安全**   | 完整的类型提示和 IDE 支持          |

### 适用场景

- ✅ **大多数业务场景**（推荐）
- ✅ 需要数据验证
- ✅ 需要自定义字段描述
- ✅ 需要额外的业务接口

---

## 🎯 模式三：完全控制模式

使用 **CRUDBase 工具类**，手动定义所有路由，适合需要完全控制的复杂业务场景。

### 代码示例

```python
from fastapi import APIRouter
from faster_app.apps.demo.models import DemoModel
from faster_app.apps.demo.schemas import DemoCreate, DemoUpdate
from faster_app.utils.crud import CRUDBase
from faster_app.utils.response import ApiResponse
from http import HTTPStatus

# 手动创建路由
demo_custom_router = APIRouter(
    prefix="/demos-custom",
    tags=["Demo - 完全控制模式"]
)

# 使用 CRUD 工具类处理数据操作
demo_crud = CRUDBase(
    model=DemoModel,
    create_schema=DemoCreate,
    update_schema=DemoUpdate,
)


@demo_custom_router.get("/")
async def list_demos(
    skip: int = 0,
    limit: int = 100,
    status: int | None = None,
):
    """
    自定义列表查询
    - 支持按状态筛选
    - 自定义分页参数
    - 自定义响应格式
    """
    filters = {}
    if status is not None:
        filters["status"] = status

    # 使用 CRUD 工具类查询
    records = await demo_crud.get_multi(
        skip=skip,
        limit=limit,
        filters=filters,
        order_by=["-created_at"],  # 按创建时间倒序
    )

    total = await DemoModel.filter(**filters).count()

    return ApiResponse.success(
        data={
            "items": [
                await demo_crud.response_schema.from_tortoise_orm(record)
                for record in records
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }
    )


@demo_custom_router.post("/")
async def create_demo(create_data: DemoCreate):
    """
    自定义创建接口
    - 添加业务逻辑
    - 自定义响应格式
    """
    # 业务逻辑：检查名称是否重复
    existing = await DemoModel.filter(name=create_data.name).first()
    if existing:
        return ApiResponse.error(
            message="名称已存在",
            status_code=HTTPStatus.BAD_REQUEST
        )

    # 使用 CRUD 工具类创建
    record = await demo_crud.create(create_data)

    return ApiResponse.success(
        data=await demo_crud.response_schema.from_tortoise_orm(record),
        message="创建成功",
    )


@demo_custom_router.get("/{record_id}")
async def get_demo(record_id: str):
    """自定义查询单个接口"""
    record = await demo_crud.get(record_id)
    if not record:
        return ApiResponse.error(
            message="记录不存在",
            status_code=HTTPStatus.NOT_FOUND
        )

    return ApiResponse.success(
        data=await demo_crud.response_schema.from_tortoise_orm(record)
    )


@demo_custom_router.put("/{record_id}")
async def update_demo(record_id: str, update_data: DemoUpdate):
    """自定义更新接口"""
    record = await demo_crud.update(record_id, update_data)
    if not record:
        return ApiResponse.error(
            message="记录不存在",
            status_code=HTTPStatus.NOT_FOUND
        )

    return ApiResponse.success(
        data=await demo_crud.response_schema.from_tortoise_orm(record),
        message="更新成功",
    )


@demo_custom_router.delete("/{record_id}")
async def delete_demo(record_id: str):
    """自定义删除接口"""
    success = await demo_crud.delete(record_id)
    if not success:
        return ApiResponse.error(
            message="记录不存在",
            status_code=HTTPStatus.NOT_FOUND
        )

    return ApiResponse.success(message="删除成功")
```

### CRUDBase 工具类方法

| 方法                                        | 说明         | 返回值            |
| ------------------------------------------- | ------------ | ----------------- |
| `get(id)`                                   | 查询单个记录 | Model 对象或 None |
| `get_multi(skip, limit, filters, order_by)` | 查询多个记录 | List[Model]       |
| `create(schema)`                            | 创建记录     | Model 对象        |
| `update(id, schema)`                        | 更新记录     | Model 对象或 None |
| `delete(id)`                                | 删除记录     | bool              |

### 适用场景

- ✅ 复杂的业务逻辑
- ✅ 需要自定义错误处理
- ✅ 需要精细的权限控制
- ✅ 非标准的 REST 接口
- ✅ 需要添加日志、监控等横切关注点

---

## 🎨 实战示例

### 示例 1：只读 API

```python
# 只提供查询接口，不允许修改
readonly_router = CRUDRouter(
    model=DemoModel,
    prefix="/demos-readonly",
    tags=["只读模式"],
    operations="RL",  # 只有 Read 和 List
).get_router()
```

### 示例 2：结合权限控制

```python
from fastapi import Depends
from faster_app.utils.auth import get_current_user

protected_router = CRUDRouter(
    model=DemoModel,
    prefix="/demos-protected",
    tags=["需要认证"],
).get_router()

# 为所有路由添加依赖
protected_router.dependencies = [Depends(get_current_user)]
```

### 示例 3：自定义分页

```python
from fastapi_pagination import Page, add_pagination

# 使用 fastapi-pagination
demo_router = CRUDRouter(
    model=DemoModel,
    prefix="/demos",
    paginate=True,  # 启用分页
).get_router()

add_pagination(demo_router)
```

---

## 💡 最佳实践

### 1️⃣ 选择合适的模式

```python
# ✅ 推荐：优先使用平衡模式
# 兼顾开发效率和业务灵活性
demo_router = CRUDRouter(
    model=DemoModel,
    create_schema=DemoCreate,
    update_schema=DemoUpdate,
    prefix="/demos",
).get_router()

# ❌ 不推荐：过度使用完全控制模式
# 除非真的需要复杂逻辑，否则会增加维护成本
```

### 2️⃣ 合理组织 Schema

```python
# 创建 Schema - 必填字段
class DemoCreate(BaseModel):
    name: str
    description: str

# 更新 Schema - 所有字段可选
class DemoUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

# 响应 Schema - 包含额外字段
class DemoResponse(BaseModel):
    id: UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
```

### 3️⃣ 添加业务验证

```python
from pydantic import field_validator

class DemoCreate(BaseModel):
    name: str
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("邮箱格式不正确")
        return v.lower()
```

### 4️⃣ 统一响应格式

```python
from faster_app.utils.response import ApiResponse

@demo_router.post("/")
async def create_demo(data: DemoCreate):
    record = await DemoModel.create(**data.model_dump())

    # 使用统一响应格式
    return ApiResponse.success(
        data=record,
        message="创建成功"
    )
```

---

## 🔗 相关链接

- [模型基类](models.md) - 了解 UUIDModel、DateTimeModel 等基类
- [路由管理](routes.md) - 路由自动发现机制
- [API 工具](../api/utils.md) - CRUDRouter 和 CRUDBase API 参考
- [最佳实践](../best-practices/api-design.md) - API 设计最佳实践

---

## 🎯 小结

| 模式         | 何时使用                      |
| ------------ | ----------------------------- |
| **快速模式** | 标准 CRUD，快速原型，内部工具 |
| **平衡模式** | 大多数业务场景（推荐）        |
| **完全控制** | 复杂业务，特殊需求，精细控制  |

!!! tip "推荐做法"
从**平衡模式**开始，遇到特殊需求时再考虑**完全控制模式**。避免过早优化和过度设计。

现在你已经掌握了 Faster APP 的 CRUD Router 三种开发模式，赶快在你的项目中尝试吧！🚀
