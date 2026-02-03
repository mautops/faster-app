"""
限流系统

提供请求频率控制功能,防止 API 被滥用。
"""

import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import TYPE_CHECKING

from fastapi import Request

from faster_app.settings import configs

if TYPE_CHECKING:
    from faster_app.viewsets.base import ViewSet

# 全局限流缓存（有界 LRU）
_cache: OrderedDict[str, list[float]] = OrderedDict()
_cache_max_size = 10000


class BaseThrottle(ABC):
    """
    限流基类

    所有限流类都应继承此类,实现限流逻辑。
    """

    @abstractmethod
    async def allow_request(self, request: Request, view: "ViewSet") -> bool:
        """
        检查是否允许请求

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例

        Returns:
            True 表示允许请求,False 表示需要限流

        Note:
            如果返回 False,应该抛出 TooManyRequestsError
        """
        pass

    def get_ident(self, request: Request) -> str:
        """
        获取请求的唯一标识(用于限流)

        Args:
            request: FastAPI 请求对象

        Returns:
            唯一标识字符串(通常是 IP 地址或用户 ID)
        """
        # 优先使用用户 ID
        if hasattr(request.state, "user") and request.state.user:
            user_id = getattr(request.state.user, "id", None)
            if user_id:
                return str(user_id)

        # 否则使用 IP 地址
        if request.client:
            return request.client.host

        return "unknown"

    def wait(self) -> int | None:
        """
        返回需要等待的秒数(可选)

        Returns:
            需要等待的秒数,如果为 None 则不提供等待时间信息
        """
        return None


class SimpleRateThrottle(BaseThrottle):
    """
    简单速率限流

    基于时间窗口的限流,支持配置速率(如 "100/hour")。
    """

    scope: str = ""
    rate: str = ""  # 格式：'100/hour', '1000/day', '10/minute'

    def __init__(self, rate: str | None = None, scope: str | None = None):
        """
        初始化速率限流

        Args:
            rate: 速率字符串,格式：'数量/时间单位',如 '100/hour'
            scope: 作用域名称(用于从配置中获取速率)
        """
        if rate is not None:
            self.rate = rate
        if scope is not None:
            self.scope = scope

    def parse_rate(self, rate: str) -> tuple[int, int]:
        """
        解析速率字符串

        Args:
            rate: 速率字符串,如 '100/hour'

        Returns:
            (允许的请求数, 时间窗口秒数) 元组
        """
        if not rate:
            return (0, 0)

        num, period = rate.split("/")
        num_requests = int(num)

        # 时间单位映射
        period_map = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }

        period_seconds = period_map.get(period.lower(), 1)
        return (num_requests, period_seconds)

    def get_rate(self, view: "ViewSet") -> str:
        """
        获取速率配置(可被子类重写)

        Args:
            view: ViewSet 实例

        Returns:
            速率字符串
        """
        # 如果直接指定了 rate,优先使用
        if self.rate:
            return self.rate

        # 如果有 scope,从配置中获取速率
        if self.scope:
            throttle_rates = {
                "user": configs.THROTTLE_USER_RATE,
                "anon": configs.THROTTLE_ANON_RATE,
                "default": configs.THROTTLE_DEFAULT_RATE,
            }
            if self.scope in throttle_rates:
                return throttle_rates[self.scope]

        # 如果 ViewSet 有 throttle_scope,从配置中获取
        if hasattr(view, "throttle_scope") and view.throttle_scope:
            throttle_rates = {
                "user": configs.THROTTLE_USER_RATE,
                "anon": configs.THROTTLE_ANON_RATE,
                "default": configs.THROTTLE_DEFAULT_RATE,
            }
            if view.throttle_scope in throttle_rates:
                return throttle_rates[view.throttle_scope]

        # 使用默认速率
        return configs.THROTTLE_DEFAULT_RATE

    def get_cache_key(self, request: Request, view: "ViewSet") -> str:
        """
        获取缓存键(可被子类重写)

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例

        Returns:
            缓存键字符串
        """
        ident = self.get_ident(request)
        scope = self.scope or getattr(view, "throttle_scope", "default")
        return f"throttle_{scope}_{ident}"

    async def allow_request(self, request: Request, view: "ViewSet") -> bool:
        """
        检查是否允许请求

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例

        Returns:
            True 表示允许请求,False 表示需要限流
        """
        rate = self.get_rate(view)
        if not rate:
            return True

        num_requests, duration = self.parse_rate(rate)
        if num_requests is None:
            return True

        key = self.get_cache_key(request, view)
        now = time.time()
        cutoff = now - duration

        # 获取并清理过期记录
        history = [ts for ts in _cache.get(key, []) if ts > cutoff]

        # 检查是否超过限制
        if len(history) >= num_requests:
            _cache[key] = history
            return False

        # 记录本次请求，并限制缓存大小
        history.append(now)
        if key in _cache:
            _cache.move_to_end(key)
        elif len(_cache) >= _cache_max_size:
            _cache.popitem(last=False)
        _cache[key] = history

        return True

    def wait(self) -> int | None:
        """
        返回需要等待的秒数

        Returns:
            需要等待的秒数
        """
        # 简化实现,返回 None
        # 实际实现可以计算需要等待的时间
        return None


class UserRateThrottle(SimpleRateThrottle):
    """
    用户限流

    对已认证用户进行限流。
    """

    scope = "user"

    def get_cache_key(self, request: Request, view: "ViewSet") -> str:
        """
        获取缓存键(基于用户 ID)

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例

        Returns:
            缓存键字符串
        """
        if hasattr(request.state, "user") and request.state.user:
            user_id = getattr(request.state.user, "id", None)
            ident = str(user_id) if user_id else self.get_ident(request)
        else:
            ident = self.get_ident(request)

        scope = self.scope or getattr(view, "throttle_scope", "user")
        return f"throttle_{scope}_{ident}"

    async def allow_request(self, request: Request, view: "ViewSet") -> bool:
        """
        检查是否允许请求(仅对已认证用户限流)

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例

        Returns:
            True 表示允许请求,False 表示需要限流
        """
        # 如果未认证,不进行限流(由 AnonRateThrottle 处理)
        if not hasattr(request.state, "user") or not request.state.user:
            return True

        return await super().allow_request(request, view)


class AnonRateThrottle(SimpleRateThrottle):
    """
    匿名用户限流

    对未认证用户进行限流。
    """

    scope = "anon"

    async def allow_request(self, request: Request, view: "ViewSet") -> bool:
        """
        检查是否允许请求(仅对未认证用户限流)

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例

        Returns:
            True 表示允许请求,False 表示需要限流
        """
        # 如果已认证,不进行限流(由 UserRateThrottle 处理)
        if hasattr(request.state, "user") and request.state.user:
            return True

        return await super().allow_request(request, view)


class ScopedRateThrottle(SimpleRateThrottle):
    """
    作用域限流

    基于作用域的限流,每个 ViewSet 可以配置不同的限流速率。
    """

    def get_rate(self, view: "ViewSet") -> str:
        """
        从 ViewSet 的 throttle_scope 获取速率

        Args:
            view: ViewSet 实例

        Returns:
            速率字符串
        """
        if hasattr(view, "throttle_scope") and view.throttle_scope:
            throttle_rates = {
                "user": configs.THROTTLE_USER_RATE,
                "anon": configs.THROTTLE_ANON_RATE,
                "default": configs.THROTTLE_DEFAULT_RATE,
            }
            if view.throttle_scope in throttle_rates:
                return throttle_rates[view.throttle_scope]

        # 如果没有配置,使用默认速率
        return self.rate or ""


class MultiRateThrottle(BaseThrottle):
    """
    多速率限流

    支持同时配置多个速率规则,需要同时满足所有规则("与"的关系)。
    例如：同时限制 500/hour 和 30/minute,必须同时满足这两个条件。

    Args:
        rates: 速率列表,格式：['500/hour', '30/minute']
        scope: 作用域名称(可选)
    """

    def __init__(self, rates: list[str], scope: str | None = None):
        """
        初始化多速率限流

        Args:
            rates: 速率列表,格式：['500/hour', '30/minute']
            scope: 作用域名称(可选)
        """
        self.rates = rates
        self.scope = scope or "multi_rate"
        # 为每个速率创建一个 SimpleRateThrottle 实例
        self._throttles = [
            SimpleRateThrottle(rate=rate, scope=f"{self.scope}_{i}") for i, rate in enumerate(rates)
        ]

    def get_cache_key(self, request: Request, view: "ViewSet") -> str:
        """
        获取缓存键(基于第一个限流器的键)

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例

        Returns:
            缓存键字符串
        """
        if self._throttles:
            return self._throttles[0].get_cache_key(request, view)
        ident = self.get_ident(request)
        return f"throttle_{self.scope}_{ident}"

    async def allow_request(self, request: Request, view: "ViewSet") -> bool:
        """
        检查是否允许请求(需要同时满足所有速率规则)

        Args:
            request: FastAPI 请求对象
            view: ViewSet 实例

        Returns:
            True 表示允许请求,False 表示需要限流
        """
        # 检查所有速率规则,必须全部通过
        for throttle in self._throttles:
            if not await throttle.allow_request(request, view):
                return False
        return True

    def wait(self) -> int | None:
        """
        返回需要等待的秒数(返回最长的等待时间)

        Returns:
            需要等待的秒数
        """
        wait_times: list[int] = []
        for throttle in self._throttles:
            wait = throttle.wait()
            if wait is not None and wait > 0:
                wait_times.append(wait)
        return max(wait_times) if wait_times else 0


class NoThrottle(BaseThrottle):
    """
    不限流

    不进行任何限流检查。
    """

    async def allow_request(self, request: Request, view: "ViewSet") -> bool:
        return True
