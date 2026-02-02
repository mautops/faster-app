"""
自定义中间件示例

⚠️ 注意:这些中间件默认不会被加载,以避免性能开销。
如需使用,请在 faster_app/middleware/builtins/middlewares.py 的 MIDDLEWARES 列表中添加。

提供的中间件:
1. RequestTimingMiddleware - 性能监控中间件,记录请求处理时间
2. RequestLoggingMiddleware - 请求日志中间件,记录请求详情(会增加 I/O 开销)
3. SecurityHeadersMiddleware - 安全响应头中间件,自动添加安全 HTTP 头
"""

from collections.abc import Callable
from time import time
from typing import cast

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from faster_app.settings import configs
from faster_app.utils.logger import logger


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    请求性能监控中间件

    功能:
    1. 记录每个请求的处理时间
    2. 对慢请求进行警告
    3. 在响应头中添加处理时间信息
    """

    def __init__(self, app, slow_threshold: float = 1.0):
        """
        初始化中间件

        Args:
            app: ASGI 应用
            slow_threshold: 慢请求阈值(秒),默认 1.0 秒
        """
        super().__init__(app)
        self.slow_threshold = slow_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        start_time = time()

        # 调用下一个中间件/路由处理器
        response = await call_next(request)

        # 计算处理时间
        process_time = time() - start_time

        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        # 记录慢请求
        if process_time > self.slow_threshold:
            logger.warning(
                f"[慢请求] 方法: {request.method} "
                f"路径: {request.url.path} "
                f"耗时: {process_time:.4f}秒 "
                f"阈值: {self.slow_threshold}秒"
            )

        return cast(Response, response)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件

    功能:
    1. 记录所有 HTTP 请求的详细信息
    2. 记录请求方法,路径,客户端 IP,状态码
    3. 可选记录请求体和响应体(需注意性能和隐私)
    """

    def __init__(
        self,
        app,
        log_request_body: bool = False,
        log_response_body: bool = False,
    ):
        """
        初始化中间件

        Args:
            app: ASGI 应用
            log_request_body: 是否记录请求体(可能包含敏感信息)
            log_response_body: 是否记录响应体
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"

        # 记录请求信息
        log_msg = f"[请求] 方法: {request.method} 路径: {request.url.path} 客户端: {client_ip}"

        # 可选:记录查询参数
        if request.url.query:
            log_msg += f" 参数: {request.url.query}"

        logger.info(log_msg)

        # 可选:记录请求体(注意:这会消耗请求体,需要重新构造)
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                logger.debug(f"[请求体] {body.decode('utf-8')[:500]}")  # 限制长度
            except Exception as e:
                logger.debug(f"[请求体] 无法读取: {e}")

        # 调用下一个中间件/路由处理器
        response = await call_next(request)

        # 记录响应信息
        logger.info(f"[响应] 路径: {request.url.path} 状态码: {response.status_code}")

        return cast(Response, response)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全响应头中间件

    功能:
    1. 自动添加安全相关的 HTTP 响应头
    2. 提升应用的安全性
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        response = await call_next(request)

        # 添加安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 如果是生产环境,添加 HSTS(强制 HTTPS)
        if not configs.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return cast(Response, response)
