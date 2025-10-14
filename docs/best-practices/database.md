# 数据库设计最佳实践

本页面介绍数据库设计的最佳实践。

## 模型设计

### 使用合适的基类

```python
# ✅ 推荐：大多数业务表
class User(UUIDModel, DateTimeModel):
    pass

# ✅ 推荐：多租户应用
class Order(UUIDModel, DateTimeModel, ScopeModel):
    pass
```

### 添加索引

```python
class User(UUIDModel):
    username = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100)

    class Meta:
        table = "users"
        indexes = [
            ("username",),
            ("email",),
            ("username", "email"),  # 复合索引
        ]
```

## 迁移管理

### 命名规范

```bash
# ✅ 推荐：描述性名称
faster db migrate --name="add_user_email_index"
faster db migrate --name="create_order_table"

# ❌ 不推荐：无意义名称
faster db migrate --name="update1"
faster db migrate --name="fix"
```

更多详细内容...
