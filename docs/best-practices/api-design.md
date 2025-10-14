# API 设计最佳实践

本页面介绍 RESTful API 设计的最佳实践。

## RESTful 规范

### 资源命名

```python
# ✅ 推荐：使用名词复数
router = APIRouter(prefix="/users", tags=["用户"])
router = APIRouter(prefix="/articles", tags=["文章"])

# ❌ 不推荐：使用动词
router = APIRouter(prefix="/get_users")
router = APIRouter(prefix="/create_article")
```

### HTTP 方法

| 方法   | 用途     | 示例                 |
| ------ | -------- | -------------------- |
| GET    | 获取资源 | `GET /users`         |
| POST   | 创建资源 | `POST /users`        |
| PUT    | 完整更新 | `PUT /users/{id}`    |
| PATCH  | 部分更新 | `PATCH /users/{id}`  |
| DELETE | 删除资源 | `DELETE /users/{id}` |

## 状态码使用

```python
@router.post("", status_code=201)  # 创建成功
async def create_user(data: UserCreate):
    pass

@router.delete("/{id}", status_code=204)  # 删除成功（无内容）
async def delete_user(id: str):
    pass
```

更多详细内容...
