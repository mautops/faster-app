# 中间件

Faster APP 支持中间件的自动发现和注册，让你轻松扩展应用功能。

## 🎯 基本概念

中间件是处理请求和响应的组件，可以在请求到达路由之前或响应返回之后执行额外逻辑。

## 创建中间件

```python
# middleware/auth.py
from faster_app.middleware.base import BaseMiddleware
from fastapi import Request
from starlette.middleware.base import RequestResponseEndpoint

class AuthMiddleware(BaseMiddleware):
    """认证中间件"""

    priority = 100  # 优先级（数字越小越先执行）

    async def __call__(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ):
        # 请求前处理
        token = request.headers.get("Authorization")
        if token:
            request.state.user = await self.authenticate(token)

        # 调用下一个中间件/路由
        response = await call_next(request)

        # 响应后处理
        response.headers["X-Process-Time"] = str(time.time())

        return response

    async def authenticate(self, token: str):
        """认证逻辑"""
        # 实现你的认证逻辑
        pass
```

更多内容请查看完整文档...
