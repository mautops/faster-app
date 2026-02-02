"""全局异常处理器"""

import logging
import traceback
from datetime import datetime
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from faster_app.exceptions.base import FasterAppError
from faster_app.settings import configs

logger = logging.getLogger(__name__)


def _create_error_response(
    *,
    code: int,
    message: str,
    status_code: int,
    data: Any = None,
    error_detail: str | None = None,
    extra: dict[str, Any] | None = None,
    include_detail: bool = True,
) -> JSONResponse:
    """创建标准错误响应

    Args:
        code: 业务错误码
        message: 错误消息
        status_code: HTTP 状态码
        data: 附加数据
        error_detail: 详细错误信息
        extra: 额外字段
        include_detail: 是否包含详细信息

    Returns:
        JSONResponse 对象
    """
    response_data: dict[str, Any] = {
        "success": False,
        "code": code,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }

    if include_detail and error_detail:
        response_data["error_detail"] = error_detail

    if extra:
        response_data.update(extra)

    return JSONResponse(content=response_data, status_code=status_code)


async def faster_app_exception_handler(request: Request, exc: FasterAppError) -> JSONResponse:
    """处理 FasterAppError 异常

    Args:
        request: FastAPI 请求对象
        exc: FasterAppError 异常实例

    Returns:
        标准化的错误响应
    """
    # 在生产环境中隐藏详细错误信息
    include_detail = configs.DEBUG

    logger.warning(
        f"[异常处理] {exc.__class__.__name__} 消息: {exc.message} "
        f"错误码: {exc.code} 状态码: {exc.status_code}"
    )

    return _create_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        data=exc.data,
        error_detail=exc.error_detail,
        include_detail=include_detail,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """处理请求验证错误

    Args:
        request: FastAPI 请求对象
        exc: RequestValidationError 异常实例

    Returns:
        标准化的错误响应
    """
    errors = exc.errors()

    # 格式化错误消息
    error_messages = [
        f"{' -> '.join(str(loc) for loc in error.get('loc', []))}: {error.get('msg', '验证失败')}"
        for error in errors
    ]
    error_detail = "; ".join(error_messages)

    logger.warning(f"[请求验证] 验证失败 详情: {error_detail}")

    # 在开发环境中显示详细错误信息
    extra = {"errors": errors} if configs.DEBUG else None

    return _create_error_response(
        code=422,
        message="请求参数验证失败",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_detail=error_detail,
        extra=extra,
        include_detail=configs.DEBUG,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """处理 HTTP 异常

    Args:
        request: FastAPI 请求对象
        exc: StarletteHTTPException 异常实例

    Returns:
        标准化的错误响应
    """
    message = exc.detail if hasattr(exc, "detail") else "HTTP 错误"

    logger.warning(f"[HTTP异常] 状态码: {exc.status_code} 详情: {message}")

    return _create_error_response(
        code=exc.status_code,
        message=message,
        status_code=exc.status_code,
        include_detail=False,
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理所有未捕获的异常

    Args:
        request: FastAPI 请求对象
        exc: 异常实例

    Returns:
        标准化的错误响应
    """
    # 记录完整错误信息到日志
    request_path = request.url.path if hasattr(request, "url") else "unknown"
    logger.error(
        f"[未处理异常] 异常类型: {type(exc).__name__} 消息: {str(exc)} 路径: {request_path}",
        exc_info=True,
    )

    # 在开发环境中显示详细错误信息
    extra = None
    error_detail = None
    if configs.DEBUG:
        error_detail = str(exc)
        extra = {"traceback": traceback.format_exc()}

    return _create_error_response(
        code=500,
        message="服务器内部错误",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_detail=error_detail,
        extra=extra,
        include_detail=configs.DEBUG,
    )
