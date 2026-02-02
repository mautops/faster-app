"""异常管理器"""

import logging
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from faster_app.exceptions.base import FasterAppError
from faster_app.exceptions.handlers import (
    faster_app_exception_handler,
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)

logger = logging.getLogger(__name__)

# 异常处理器类型：支持异步处理函数
# 注：FastAPI 异常处理器通常是异步函数，返回 Awaitable[JSONResponse]
ExceptionHandler = Callable[[Request, Exception], Awaitable[JSONResponse] | JSONResponse]


class ExceptionManager:
    """异常处理器管理器"""

    def __init__(self) -> None:
        self._handlers: dict[type[Exception], ExceptionHandler] = {}
        self._order: list[type[Exception]] = []
        self._registered_defaults = False

    def register(
        self,
        exception_class: type[Exception],
        handler: ExceptionHandler,
        *,
        priority: int = 0,
    ) -> None:
        """注册异常处理器"""
        if exception_class in self._handlers:
            raise ValueError(f"异常处理器 {exception_class.__name__} 已注册")

        self._handlers[exception_class] = handler
        self._order.append(exception_class)
        logger.debug(f"[异常管理器] 注册: {exception_class.__name__} 优先级: {priority}")

    def register_defaults(self) -> None:
        """注册默认异常处理器"""
        if self._registered_defaults:
            logger.debug("[异常管理器] 默认处理器已注册,跳过")
            return

        # 使用 type: ignore 来忽略类型检查，因为这些处理器的签名是正确的
        self.register(FasterAppError, faster_app_exception_handler, priority=10)  # type: ignore[arg-type]
        self.register(RequestValidationError, validation_exception_handler, priority=20)  # type: ignore[arg-type]
        self.register(StarletteHTTPException, http_exception_handler, priority=30)  # type: ignore[arg-type]
        self.register(Exception, general_exception_handler, priority=100)

        self._registered_defaults = True
        logger.debug("[异常管理器] 默认处理器注册完成")

    def unregister(self, exception_class: type[Exception]) -> None:
        """取消注册异常处理器"""
        if exception_class not in self._handlers:
            raise KeyError(f"异常处理器 {exception_class.__name__} 未注册")

        del self._handlers[exception_class]
        self._order.remove(exception_class)
        logger.debug(f"[异常管理器] 取消注册: {exception_class.__name__}")

    def get_handler(self, exception_class: type[Exception]) -> ExceptionHandler | None:
        """获取异常处理器"""
        return self._handlers.get(exception_class)

    def list_handlers(self) -> list[tuple[type[Exception], ExceptionHandler]]:
        """列出所有注册的异常处理器"""
        return [(exc_class, self._handlers[exc_class]) for exc_class in self._order]

    def apply(self, app: FastAPI) -> None:
        """将所有注册的异常处理器应用到 FastAPI 应用"""
        for exception_class, handler in self.list_handlers():
            app.add_exception_handler(exception_class, handler)
            logger.debug(f"[异常管理器] 应用处理器: {exception_class.__name__}")

        logger.info(f"[异常管理器] 已注册 {len(self._handlers)} 个异常处理器")

    def clear(self) -> None:
        """清空所有注册的异常处理器"""
        self._handlers.clear()
        self._order.clear()
        self._registered_defaults = False
        logger.debug("[异常管理器] 清空所有处理器")


_global_manager: ExceptionManager | None = None


def get_manager() -> ExceptionManager:
    """获取全局异常管理器"""
    global _global_manager
    if _global_manager is None:
        _global_manager = ExceptionManager()
        _global_manager.register_defaults()
    return _global_manager


def reset_manager() -> None:
    """重置全局异常管理器(用于测试)"""
    global _global_manager
    _global_manager = None
