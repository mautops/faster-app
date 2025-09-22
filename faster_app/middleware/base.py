"""
中间件基类 - 符合 FastAPI 最佳实践
"""

from starlette.middleware.base import BaseHTTPMiddleware


class BaseMiddleware(BaseHTTPMiddleware):
    """
    中间件基类

    符合 FastAPI/Starlette 标准的中间件基类
    """

    # 中间件优先级，用于排序
    priority: int = 100

    def __init__(self, app, **kwargs):
        """
        初始化中间件

        Args:
            app: ASGI 应用
            **kwargs: 中间件配置参数
        """
        super().__init__(app)

        # 将配置参数设置为实例属性
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def dispatch(self, request, call_next):
        """
        处理请求的默认实现

        子类应该重写此方法
        """
        return await call_next(request)
