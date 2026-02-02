"""Lifespan 管理器"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from faster_app.lifespan.combine import LifespanFunc, combine_lifespans
from faster_app.settings import logger


class LifespanManager:
    """Lifespan 管理器"""

    def __init__(self) -> None:
        self._lifespans: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        lifespan: LifespanFunc,
        *,
        enabled: bool = True,
        priority: int = 0,
    ) -> None:
        """注册 lifespan 函数"""
        if name in self._lifespans:
            raise ValueError(f"Lifespan '{name}' 已注册")
        self._lifespans[name] = {"func": lifespan, "enabled": enabled, "priority": priority}
        logger.debug(f"[Lifespan] 注册: {name} 启用: {enabled} 优先级: {priority}")

    def enable(self, name: str) -> None:
        """启用指定的 lifespan"""
        if name not in self._lifespans:
            raise KeyError(f"Lifespan '{name}' 不存在")

        self._lifespans[name]["enabled"] = True
        logger.debug(f"[Lifespan] 启用: {name}")

    def disable(self, name: str) -> None:
        """禁用指定的 lifespan"""
        if name not in self._lifespans:
            raise KeyError(f"Lifespan '{name}' 不存在")

        self._lifespans[name]["enabled"] = False
        logger.debug(f"[Lifespan] 禁用: {name}")

    def is_enabled(self, name: str) -> bool:
        """检查 lifespan 是否启用"""
        return bool(self._lifespans.get(name, {}).get("enabled", False))

    def list_enabled(self) -> list[str]:
        """列出所有启用的 lifespan(按优先级排序)"""
        enabled = [
            (name, info["priority"]) for name, info in self._lifespans.items() if info["enabled"]
        ]
        enabled.sort(key=lambda x: x[1])
        return [name for name, _ in enabled]

    def build(self) -> LifespanFunc:
        """构建组合后的 lifespan 函数"""
        enabled_names = self.list_enabled()

        if not enabled_names:
            logger.debug("[Lifespan] 未发现启用的 lifespan")

            @asynccontextmanager
            async def empty_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
                yield

            return empty_lifespan

        logger.debug(f"[Lifespan] 启用的 lifespan: {', '.join(enabled_names)}")

        enabled_lifespans = [self._lifespans[name]["func"] for name in enabled_names]

        return combine_lifespans(*enabled_lifespans)

    def clear(self) -> None:
        """清空所有注册的 lifespan"""
        self._lifespans.clear()
        logger.debug("[Lifespan] 清空所有注册")


_global_manager: LifespanManager | None = None


def get_manager() -> LifespanManager:
    """获取全局 lifespan 管理器"""
    global _global_manager
    if _global_manager is None:
        _global_manager = LifespanManager()
    return _global_manager


def reset_manager() -> None:
    """重置全局 lifespan 管理器(用于测试)"""
    global _global_manager
    _global_manager = None
