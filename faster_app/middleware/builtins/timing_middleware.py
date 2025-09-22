"""
请求计时中间件 - 符合 FastAPI 最佳实践
"""

import time
from starlette.requests import Request
from starlette.responses import Response
from faster_app.middleware.base import BaseMiddleware
from faster_app.settings import logger


class TimingMiddleware(BaseMiddleware):
    """
    请求计时中间件

    符合 FastAPI 最佳实践的请求计时中间件
    """

    priority = 50  # 中等优先级

    def __init__(
        self,
        app,
        log_requests: bool = True,
        add_header: bool = True,
        header_name: str = "X-Process-Time",
    ):
        """
        初始化计时中间件

        Args:
            app: ASGI 应用
            log_requests: 是否记录请求日志
            add_header: 是否添加处理时间头部
            header_name: 处理时间头部名称
        """
        super().__init__(app)

        self.log_requests = log_requests
        self.add_header = add_header
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next) -> Response:
        """记录请求处理时间"""

        start_time = time.time()

        # 处理请求
        response = await call_next(request)

        # 计算处理时间
        process_time = time.time() - start_time

        # 添加处理时间到响应头
        if self.add_header:
            response.headers[self.header_name] = f"{process_time:.4f}"

        # 记录日志
        if self.log_requests:
            logger.info(
                f"{request.method} {request.url.path} - "
                f"处理时间: {process_time:.4f}s - "
                f"状态码: {response.status_code}"
            )

        return response
