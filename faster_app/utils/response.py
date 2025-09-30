from http import HTTPStatus
from typing import Any, Optional
from fastapi.responses import JSONResponse
from datetime import datetime


class ApiResponse:
    """统一的API响应格式类"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        code: int = 200,
        status_code: int = HTTPStatus.OK,
    ) -> JSONResponse:
        """
        成功响应格式

        Args:
            data: 返回的数据，可以是任意类型
            message: 成功消息
            code: 业务状态码
            status_code: HTTP状态码
        """
        response_data = {
            "success": True,
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        return JSONResponse(content=response_data, status_code=status_code)

    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = 500,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        error_detail: Optional[str] = None,
        data: Any = None,
    ) -> JSONResponse:
        """
        错误响应格式

        Args:
            message: 错误消息
            code: 业务错误码
            status_code: HTTP状态码
            error_detail: 详细错误信息
            data: 额外的错误数据
        """
        response_data = {
            "success": False,
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }

        # 如果有详细错误信息，添加到响应中
        if error_detail:
            response_data["error_detail"] = error_detail

        return JSONResponse(content=response_data, status_code=status_code)

    @staticmethod
    def paginated(
        data: list,
        total: int,
        page: int = 1,
        page_size: int = 10,
        message: str = "查询成功",
    ) -> JSONResponse:
        """
        分页响应格式

        Args:
            data: 分页数据列表
            total: 总记录数
            page: 当前页码
            page_size: 每页大小
            message: 响应消息
        """
        pagination_info = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "has_next": page * page_size < total,
            "has_prev": page > 1,
        }

        response_data = {
            "success": True,
            "code": 200,
            "message": message,
            "data": data,
            "pagination": pagination_info,
            "timestamp": datetime.now().isoformat(),
        }

        return JSONResponse(content=response_data, status_code=HTTPStatus.OK)
