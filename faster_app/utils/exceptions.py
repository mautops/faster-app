"""
全局异常处理器
"""

import traceback
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from faster_app.routes.base import ErrorResponse
from faster_app.settings import logger


def setup_exception_handlers(app: FastAPI) -> None:
    """设置全局异常处理器"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """处理 FastAPI HTTPException"""
        logger.warning(
            f"HTTP异常: {exc.status_code} - {exc.detail} - URL: {request.url}"
        )

        error_response = ErrorResponse(
            code=exc.status_code, message="请求处理失败", detail=str(exc.detail)
        )

        return JSONResponse(
            status_code=exc.status_code, content=error_response.model_dump()
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """处理 Starlette HTTPException"""
        logger.warning(
            f"Starlette HTTP异常: {exc.status_code} - {exc.detail} - URL: {request.url}"
        )

        error_response = ErrorResponse(
            code=exc.status_code, message="请求处理失败", detail=str(exc.detail)
        )

        return JSONResponse(
            status_code=exc.status_code, content=error_response.model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """处理请求验证错误"""
        logger.warning(f"请求验证错误: {exc.errors()} - URL: {request.url}")

        # 格式化验证错误信息
        error_details = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            error_details.append(f"{field}: {error['msg']}")

        error_response = ErrorResponse(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="请求参数验证失败",
            detail="; ".join(error_details),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(),
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """处理 Pydantic 验证错误"""
        logger.warning(f"Pydantic验证错误: {exc.errors()} - URL: {request.url}")

        # 格式化验证错误信息
        error_details = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            error_details.append(f"{field}: {error['msg']}")

        error_response = ErrorResponse(
            code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="数据验证失败",
            detail="; ".join(error_details),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """处理值错误"""
        logger.warning(f"值错误: {str(exc)} - URL: {request.url}")

        error_response = ErrorResponse(
            code=status.HTTP_400_BAD_REQUEST, message="参数值错误", detail=str(exc)
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=error_response.model_dump()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """处理所有未捕获的异常"""
        logger.error(
            f"未处理异常: {type(exc).__name__}: {str(exc)} - URL: {request.url}"
        )
        logger.error(f"异常堆栈: {traceback.format_exc()}")

        # 在生产环境中不暴露详细错误信息
        from faster_app.settings import configs

        if configs.DEBUG:
            detail = f"{type(exc).__name__}: {str(exc)}"
        else:
            detail = "服务器内部错误，请稍后重试"

        error_response = ErrorResponse(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="服务器内部错误",
            detail=detail,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )


# 自定义异常类
class BusinessException(Exception):
    """业务异常基类"""

    def __init__(
        self, message: str, code: int = status.HTTP_400_BAD_REQUEST, detail: str = None
    ):
        self.message = message
        self.code = code
        self.detail = detail
        super().__init__(self.message)


class AuthenticationException(BusinessException):
    """认证异常"""

    def __init__(self, message: str = "认证失败", detail: str = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, detail)


class AuthorizationException(BusinessException):
    """授权异常"""

    def __init__(self, message: str = "权限不足", detail: str = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, detail)


class ResourceNotFoundException(BusinessException):
    """资源未找到异常"""

    def __init__(self, message: str = "资源未找到", detail: str = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, detail)


def setup_custom_exception_handlers(app: FastAPI) -> None:
    """设置自定义异常处理器"""

    @app.exception_handler(BusinessException)
    async def business_exception_handler(
        request: Request, exc: BusinessException
    ) -> JSONResponse:
        """处理业务异常"""
        logger.warning(f"业务异常: {exc.message} - URL: {request.url}")

        error_response = ErrorResponse(
            code=exc.code, message=exc.message, detail=exc.detail
        )

        return JSONResponse(status_code=exc.code, content=error_response.model_dump())
