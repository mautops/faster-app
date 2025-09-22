"""
响应工具函数
"""

from typing import Any, Optional
from fastapi import status
from fastapi.responses import JSONResponse

from faster_app.routes.base import ApiResponse, ErrorResponse


def success_response(
    data: Any = None, message: str = "操作成功", code: int = status.HTTP_200_OK
) -> JSONResponse:
    """成功响应"""
    response = ApiResponse(success=True, code=code, message=message, data=data)
    return JSONResponse(status_code=code, content=response.model_dump())


def error_response(
    message: str = "操作失败",
    code: int = status.HTTP_400_BAD_REQUEST,
    detail: Optional[str] = None,
) -> JSONResponse:
    """错误响应"""
    response = ErrorResponse(success=False, code=code, message=message, detail=detail)
    return JSONResponse(status_code=code, content=response.model_dump())


def paginated_response(
    items: list, total: int, page: int = 1, size: int = 10, message: str = "查询成功"
) -> JSONResponse:
    """分页响应"""
    data = {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,  # 向上取整
        },
    }

    return success_response(data=data, message=message)


def created_response(data: Any = None, message: str = "创建成功") -> JSONResponse:
    """创建成功响应"""
    return success_response(data=data, message=message, code=status.HTTP_201_CREATED)


def no_content_response(message: str = "操作成功") -> JSONResponse:
    """无内容响应"""
    return success_response(message=message, code=status.HTTP_204_NO_CONTENT)
