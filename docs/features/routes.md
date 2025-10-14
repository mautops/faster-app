# 路由管理

本页面介绍 Faster APP 中的路由管理和最佳实践。

## 🎯 基本概念

Faster APP 使用 FastAPI 的 `APIRouter` 进行路由管理，并通过自动发现机制实现零配置路由注册。

## 📁 路由组织

### 标准结构

```python
# apps/users/routes.py
from fastapi import APIRouter, Depends, HTTPException
from .models import User
from .schemas import UserCreate, UserResponse

router = APIRouter(
    prefix="/users",        # 路由前缀
    tags=["用户"],          # API 文档分组
    responses={404: {"description": "未找到"}}
)

@router.get("", response_model=list[UserResponse])
async def list_users(skip: int = 0, limit: int = 10):
    """获取用户列表"""
    users = await User.all().offset(skip).limit(limit)
    return users

@router.post("", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate):
    """创建用户"""
    user = await User.create(**data.dict())
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """获取用户详情"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, data: UserCreate):
    """更新用户"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    await user.update_from_dict(data.dict())
    await user.save()
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str):
    """删除用户"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    await user.delete()
    return None
```

## 详细内容请查看完整文档...
