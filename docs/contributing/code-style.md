# 代码规范

本页面介绍 Faster APP 的代码规范。

## 代码风格

使用 Ruff 进行代码检查和格式化：

```bash
# 检查代码
ruff check .

# 自动修复
ruff check --fix .

# 格式化代码
ruff format .
```

## 命名规范

- **模块名**：小写，使用下划线（`user_profile.py`）
- **类名**：帕斯卡命名（`UserProfile`）
- **函数名**：小写，使用下划线（`get_user_profile`）
- **常量**：大写，使用下划线（`MAX_UPLOAD_SIZE`）

## 注释规范

使用 Google 风格的 docstring：

```python
def get_user(user_id: str) -> User:
    """获取用户信息。

    Args:
        user_id: 用户 ID

    Returns:
        User: 用户对象

    Raises:
        HTTPException: 用户不存在时抛出
    """
    pass
```

更多详细内容...
