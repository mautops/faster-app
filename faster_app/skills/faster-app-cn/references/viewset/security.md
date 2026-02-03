# ViewSet 安全

本文档涵盖 ViewSet 的认证、权限控制和限流配置。

## 认证

认证用于识别用户身份，是安全系统的第一道防线。

### JWT 认证

#### 基础使用

```python
from faster_app.viewsets import ModelViewSet
from faster_app.viewsets.authentication import JWTAuthentication

class ArticleViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]

    model = Article
    schema = ArticleResponse
```

#### JWT 配置

```bash
# .env
JWT_SECRET_KEY=你的密钥
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

#### 生成 Token

```python
from datetime import datetime, timedelta
import jwt
from faster_app.settings import configs

def create_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=configs.JWT_EXPIRE_MINUTES
    )
    payload = {
        "user_id": user_id,
        "exp": expire
    }
    return jwt.encode(
        payload,
        configs.JWT_SECRET_KEY,
        algorithm=configs.JWT_ALGORITHM
    )
```

#### 使用 Token

```bash
# HTTP 请求头
Authorization: Bearer <token>
```

### 自定义认证

#### API Key 认证

```python
from faster_app.viewsets.authentication import BaseAuthentication
from fastapi import Request

class APIKeyAuthentication(BaseAuthentication):
    async def authenticate(self, request: Request) -> dict | None:
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return None

        # 验证 API key
        user = await verify_api_key(api_key)
        if user:
            return {
                "user_id": user.id,
                "username": user.username
            }
        return None

class ArticleViewSet(ModelViewSet):
    authentication_classes = [APIKeyAuthentication]
```

#### Session 认证

```python
class SessionAuthentication(BaseAuthentication):
    async def authenticate(self, request: Request) -> dict | None:
        session_id = request.cookies.get("session_id")
        if not session_id:
            return None

        # 验证 session
        user = await get_user_from_session(session_id)
        if user:
            return {"user_id": user.id}
        return None
```

### 多重认证

按顺序尝试多种认证方式：

```python
class ArticleViewSet(ModelViewSet):
    authentication_classes = [
        JWTAuthentication,
        APIKeyAuthentication,
        SessionAuthentication
    ]
    # 先尝试 JWT，然后 API key，最后 Session
```

### 访问认证信息

```python
class ArticleViewSet(ModelViewSet):
    @action(detail=False, methods=["GET"])
    async def my_articles(self, request: Request):
        """获取当前用户的文章"""
        user_id = request.state.user.get("user_id")
        articles = await self.model.filter(author_id=user_id)
        return articles
```

### 可选认证

某些操作可选认证：

```python
from faster_app.viewsets.permissions import AllowAny

class ArticleViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]

    permission_classes_by_action = {
        "list": [AllowAny],  # 列表无需认证
        "create": [IsAuthenticated],  # 创建需要认证
    }
```

## 权限

权限控制决定已认证用户可以执行哪些操作。

### 内置权限

#### IsAuthenticated

要求用户已认证：

```python
from faster_app.viewsets.permissions import IsAuthenticated

class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    # 所有操作都需要认证
```

#### AllowAny

允许任何人访问：

```python
from faster_app.viewsets.permissions import AllowAny

class ArticleViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    # 所有操作都公开
```

#### IsAdminUser

要求管理员权限：

```python
from faster_app.viewsets.permissions import IsAdminUser

class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    # 仅管理员可访问
```

### 按操作设置权限

不同操作使用不同权限：

```python
class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]  # 默认

    permission_classes_by_action = {
        "list": [AllowAny],            # 公开列表
        "retrieve": [AllowAny],        # 公开查看
        "create": [IsAuthenticated],   # 需要认证才能创建
        "update": [IsOwner],           # 仅所有者可更新
        "destroy": [IsAdminUser],      # 仅管理员可删除
    }
```

### 自定义权限

#### 所有者权限

```python
from faster_app.viewsets.permissions import BasePermission
from fastapi import Request

class IsOwner(BasePermission):
    async def has_permission(
        self,
        request: Request,
        view,
        obj=None
    ) -> bool:
        if not obj:
            return True  # 允许列表/创建

        # 检查用户是否拥有该对象
        user_id = request.state.user.get("user_id")
        return obj.owner_id == user_id
```

#### 角色权限

```python
class CanPublish(BasePermission):
    async def has_permission(
        self,
        request: Request,
        view,
        obj=None
    ) -> bool:
        user = request.state.user
        return user.get("role") in ["editor", "admin"]
```

#### 基于字段的权限

```python
class CanEditStatus(BasePermission):
    async def has_permission(
        self,
        request: Request,
        view,
        obj=None
    ) -> bool:
        if request.method != "PUT":
            return True

        data = await request.json()
        if "status" in data:
            # 只有管理员可以修改状态
            user = request.state.user
            return user.get("role") == "admin"
        return True
```

### 组合权限

多个权限同时检查（AND）：

```python
class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    # 必须同时满足：已认证 AND 是所有者
```

### 自定义操作权限

为特定操作设置权限：

```python
from faster_app.viewsets import action

class ArticleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[IsAdminUser]
    )
    async def feature(self, request: Request, pk: str):
        """仅管理员可以推荐文章"""
        article = await self.get_object(pk)
        article.is_featured = True
        await article.save()
        return {"status": "featured"}
```

### 权限检查时机

权限在以下时机检查：

1. **请求开始时** - 检查基础权限
2. **获取对象后** - 检查对象级权限（如 IsOwner）
3. **自定义操作前** - 检查操作特定权限

## 限流

限流用于防止 API 滥用，保护系统资源。

### 基础限流

#### 用户和匿名限流

```python
from faster_app.viewsets.throttling import (
    UserRateThrottle,
    AnonRateThrottle,
)

class ArticleViewSet(ModelViewSet):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
```

#### 配置速率

```bash
# .env
THROTTLE_RATES={"user":"100/hour","anon":"20/hour"}
```

### 速率格式

```bash
# 每秒
"10/second"

# 每分钟
"60/minute"

# 每小时
"100/hour"

# 每天
"1000/day"
```

### 作用域限流

#### 配置作用域

```python
class ArticleViewSet(ModelViewSet):
    throttle_classes = [UserRateThrottle]
    throttle_scope = "articles"
```

```bash
# .env
THROTTLE_RATES={"articles":"50/hour"}
```

#### 多个作用域

```bash
THROTTLE_RATES={
  "user":"100/hour",
  "anon":"20/hour",
  "articles":"50/hour",
  "comments":"30/hour",
  "uploads":"10/hour"
}
```

### 按操作限流

不同操作使用不同限流：

```python
from faster_app.viewsets import action

class ArticleViewSet(ModelViewSet):
    throttle_classes = [UserRateThrottle]

    @action(
        detail=False,
        methods=["POST"],
        throttle_classes=[AnonRateThrottle]
    )
    async def newsletter(self, request: Request):
        """此操作使用更严格的限流"""
        pass
```

### 自定义限流

#### 自定义速率

```python
from faster_app.viewsets.throttling import SimpleRateThrottle

class BurstRateThrottle(SimpleRateThrottle):
    scope = "burst"
    rate = "10/minute"  # 硬编码速率
```

#### 自定义缓存键

```python
class CustomThrottle(SimpleRateThrottle):
    scope = "custom"

    def get_cache_key(self, request: Request, view) -> str:
        # 基于 IP + 用户的组合键
        user_id = request.state.user.get("user_id", "anon")
        ip = request.client.host
        return f"throttle_custom_{user_id}_{ip}"
```

#### 动态速率

```python
class DynamicRateThrottle(SimpleRateThrottle):
    def get_rate(self, view):
        # 根据用户等级返回不同速率
        user = self.request.state.user
        if user.get("is_premium"):
            return "1000/hour"
        return "100/hour"
```

### 限流响应

当超过限流时，返回 429 状态码：

```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

### 禁用限流

#### 整个 ViewSet

```python
class ArticleViewSet(ModelViewSet):
    throttle_classes = []  # 禁用所有限流
```

#### 特定操作

```python
class ArticleViewSet(ModelViewSet):
    throttle_classes = [UserRateThrottle]

    @action(detail=False, methods=["GET"], throttle_classes=[])
    async def public_stats(self, request: Request):
        """此操作无限流"""
        pass
```

## 安全最佳实践

### 认证

1. **使用 HTTPS** - 生产环境必须使用 HTTPS 传输 token
2. **Token 过期** - 设置合理的过期时间，避免永久 token
3. **刷新机制** - 实现 token 刷新机制，提升用户体验
4. **安全存储** - 客户端安全存储 token，避免 XSS 攻击
5. **多因素认证** - 敏感操作考虑多因素认证

### 权限

1. **最小权限原则** - 默认拒绝，显式授权
2. **对象级权限** - 不仅检查操作权限，还要检查对象所有权
3. **权限分离** - 读写权限分离，管理权限独立
4. **审计日志** - 记录权限检查失败的尝试
5. **定期审查** - 定期审查权限配置，移除不必要的权限

### 限流

1. **合理设置速率** - 根据实际负载能力设置限流
2. **区分用户类型** - 付费用户更高限额
3. **关键操作限流** - 如登录、注册、上传等操作严格限流
4. **监控限流** - 记录被限流的请求，分析异常流量
5. **友好提示** - 告知用户何时可以重试，提供 Retry-After 头

### 综合安全

1. **深度防御** - 认证、权限、限流多层防护
2. **输入验证** - 使用 Pydantic schema 严格验证输入
3. **错误处理** - 避免泄露敏感信息的错误消息
4. **CORS 配置** - 正确配置跨域资源共享
5. **依赖更新** - 定期更新依赖，修复安全漏洞
