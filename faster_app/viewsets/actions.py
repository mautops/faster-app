"""
Action 装饰器

提供 @action 装饰器用于定义自定义操作,类似 DRF 的 @action。
"""

from collections.abc import Callable
from functools import wraps
from typing import Any, Protocol

from fastapi import Request


class ActionFunction(Protocol):
    """带有 action 元数据的函数协议"""

    action: bool
    action_methods: list[str]
    action_detail: bool
    action_url_path: str
    action_url_name: str
    action_kwargs: dict[str, Any]

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


def action(
    methods: list[str] | None = None,
    detail: bool = False,
    url_path: str | None = None,
    url_name: str | None = None,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], ActionFunction]:
    """
    装饰器：定义自定义操作

    Args:
        methods: HTTP 方法列表,如 ["GET", "POST"],默认 ["GET"]
        detail: 是否是针对单个对象的操作(需要 pk 参数)
        url_path: 自定义 URL 路径,默认使用函数名
        url_name: URL 名称(用于反向解析)
        **kwargs: 其他 FastAPI 路由参数

    Returns:
        装饰器函数

    Example:
        class MyViewSet(ModelViewSet):
            @action(detail=True, methods=["POST"])
            async def activate(self, request: Request, pk: str):
                # 激活操作
                pass

            @action(detail=False, methods=["GET"])
            async def stats(self, request: Request):
                # 统计操作
                pass
    """
    if methods is None:
        methods = ["GET"]

    def decorator(func: Callable[..., Any]) -> ActionFunction:
        # 将 action 元数据附加到函数上
        wrapper_func: Any = func
        wrapper_func.action = True
        wrapper_func.action_methods = methods
        wrapper_func.action_detail = detail
        wrapper_func.action_url_path = url_path or func.__name__.replace("_", "-")
        wrapper_func.action_url_name = url_name or func.__name__
        wrapper_func.action_kwargs = kwargs

        @wraps(func)
        async def wrapper(self: Any, request: Request, *args: Any, **kwargs_inner: Any) -> Any:
            return await func(self, request, *args, **kwargs_inner)

        # 复制元数据到 wrapper
        wrapper.action = True  # type: ignore[attr-defined]
        wrapper.action_methods = methods  # type: ignore[attr-defined]
        wrapper.action_detail = detail  # type: ignore[attr-defined]
        wrapper.action_url_path = url_path or func.__name__.replace("_", "-")  # type: ignore[attr-defined]
        wrapper.action_url_name = url_name or func.__name__  # type: ignore[attr-defined]
        wrapper.action_kwargs = kwargs  # type: ignore[attr-defined]

        return wrapper  # type: ignore[return-value]

    return decorator
