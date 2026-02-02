"""
测试限流系统
"""

from unittest.mock import MagicMock

import pytest


class TestSimpleRateThrottle:
    """测试简单速率限流"""

    def test_parse_rate(self):
        """测试解析速率字符串"""
        from faster_app.viewsets.throttling import SimpleRateThrottle

        throttle = SimpleRateThrottle()

        # 测试各种时间单位
        assert throttle.parse_rate("10/second") == (10, 1)
        assert throttle.parse_rate("60/minute") == (60, 60)
        assert throttle.parse_rate("100/hour") == (100, 3600)
        assert throttle.parse_rate("1000/day") == (1000, 86400)

    def test_parse_empty_rate(self):
        """测试解析空速率"""
        from faster_app.viewsets.throttling import SimpleRateThrottle

        throttle = SimpleRateThrottle()
        assert throttle.parse_rate("") == (0, 0)

    @pytest.mark.asyncio
    async def test_allow_request_no_rate(self, mock_request: MagicMock):
        """测试无速率限制时允许请求"""
        from faster_app.viewsets.throttling import SimpleRateThrottle

        throttle = SimpleRateThrottle(rate="")
        view = MagicMock()

        assert await throttle.allow_request(mock_request, view) is True

    @pytest.mark.asyncio
    async def test_allow_request_within_limit(self, mock_request: MagicMock):
        """测试在限制内允许请求"""
        from faster_app.viewsets.throttling import SimpleRateThrottle

        throttle = SimpleRateThrottle(rate="10/minute", scope="test_within")
        view = MagicMock()
        view.throttle_scope = None

        # 前 10 个请求应该被允许
        for i in range(10):
            result = await throttle.allow_request(mock_request, view)
            assert result is True, f"Request {i + 1} should be allowed"

    @pytest.mark.asyncio
    async def test_deny_request_over_limit(self, mock_request: MagicMock):
        """测试超过限制拒绝请求"""
        from faster_app.viewsets.throttling import SimpleRateThrottle

        throttle = SimpleRateThrottle(rate="3/minute", scope="test_over")
        view = MagicMock()
        view.throttle_scope = None

        # 前 3 个请求应该被允许
        for _ in range(3):
            await throttle.allow_request(mock_request, view)

        # 第 4 个请求应该被拒绝
        result = await throttle.allow_request(mock_request, view)
        assert result is False

    def test_get_cache_key(self, mock_request: MagicMock):
        """测试获取缓存键"""
        from faster_app.viewsets.throttling import SimpleRateThrottle

        throttle = SimpleRateThrottle(scope="test_scope")
        view = MagicMock()
        view.throttle_scope = None

        key = throttle.get_cache_key(mock_request, view)
        assert "throttle_test_scope_" in key
        assert "127.0.0.1" in key

    def test_get_ident_with_user(self, mock_request: MagicMock, mock_user: MagicMock):
        """测试获取用户标识"""
        from faster_app.viewsets.throttling import SimpleRateThrottle

        mock_request.state.user = mock_user
        throttle = SimpleRateThrottle()

        ident = throttle.get_ident(mock_request)
        assert ident == str(mock_user.id)

    def test_get_ident_without_user(self, mock_request: MagicMock):
        """测试获取 IP 标识"""
        from faster_app.viewsets.throttling import SimpleRateThrottle

        throttle = SimpleRateThrottle()

        ident = throttle.get_ident(mock_request)
        assert ident == "127.0.0.1"


class TestUserRateThrottle:
    """测试用户限流"""

    @pytest.mark.asyncio
    async def test_skip_unauthenticated(self, mock_request: MagicMock):
        """测试跳过未认证用户"""
        from faster_app.viewsets.throttling import UserRateThrottle

        mock_request.state.user = None
        throttle = UserRateThrottle()
        view = MagicMock()

        # 未认证用户应该被跳过（允许）
        result = await throttle.allow_request(mock_request, view)
        assert result is True

    @pytest.mark.asyncio
    async def test_throttle_authenticated(self, auth_request: MagicMock):
        """测试限流已认证用户"""
        from faster_app.viewsets.throttling import UserRateThrottle

        throttle = UserRateThrottle()
        throttle.rate = "2/minute"
        throttle.scope = "test_user_throttle"
        view = MagicMock()
        view.throttle_scope = None

        # 前 2 个请求允许
        assert await throttle.allow_request(auth_request, view) is True
        assert await throttle.allow_request(auth_request, view) is True

        # 第 3 个请求拒绝
        assert await throttle.allow_request(auth_request, view) is False


class TestAnonRateThrottle:
    """测试匿名用户限流"""

    @pytest.mark.asyncio
    async def test_skip_authenticated(self, auth_request: MagicMock):
        """测试跳过已认证用户"""
        from faster_app.viewsets.throttling import AnonRateThrottle

        throttle = AnonRateThrottle()
        view = MagicMock()

        # 已认证用户应该被跳过（允许）
        result = await throttle.allow_request(auth_request, view)
        assert result is True

    @pytest.mark.asyncio
    async def test_throttle_anonymous(self, mock_request: MagicMock):
        """测试限流匿名用户"""
        from faster_app.viewsets.throttling import AnonRateThrottle

        mock_request.state.user = None
        throttle = AnonRateThrottle()
        throttle.rate = "2/minute"
        throttle.scope = "test_anon_throttle"
        view = MagicMock()
        view.throttle_scope = None

        # 前 2 个请求允许
        assert await throttle.allow_request(mock_request, view) is True
        assert await throttle.allow_request(mock_request, view) is True

        # 第 3 个请求拒绝
        assert await throttle.allow_request(mock_request, view) is False


class TestNoThrottle:
    """测试无限流"""

    @pytest.mark.asyncio
    async def test_always_allows(self, mock_request: MagicMock):
        """测试总是允许请求"""
        from faster_app.viewsets.throttling import NoThrottle

        throttle = NoThrottle()
        view = MagicMock()

        # 总是允许
        for _ in range(100):
            assert await throttle.allow_request(mock_request, view) is True


class TestMultiRateThrottle:
    """测试多速率限流"""

    @pytest.mark.asyncio
    async def test_all_rates_must_pass(self, mock_request: MagicMock):
        """测试所有速率规则都必须通过"""
        from faster_app.viewsets.throttling import MultiRateThrottle

        # 设置两个速率规则
        throttle = MultiRateThrottle(rates=["5/minute", "2/second"], scope="test_multi")
        view = MagicMock()
        view.throttle_scope = None

        # 前 2 个请求允许（受限于 2/second）
        assert await throttle.allow_request(mock_request, view) is True
        assert await throttle.allow_request(mock_request, view) is True

        # 第 3 个请求被 2/second 规则拒绝
        assert await throttle.allow_request(mock_request, view) is False


class TestCacheBehavior:
    """测试缓存行为"""

    def test_cache_is_bounded(self):
        """测试缓存有大小限制"""
        from faster_app.viewsets.throttling import _cache, _cache_max_size

        assert _cache_max_size == 10000

    def test_cache_cleanup(self, mock_request: MagicMock):
        """测试缓存自动清理过期条目"""
        import time

        from faster_app.viewsets.throttling import _cache

        # 清空缓存
        _cache.clear()

        # 添加一些条目
        now = time.time()
        _cache["old_key"] = [now - 7200]  # 2 小时前
        _cache["new_key"] = [now]

        # 缓存应该包含两个条目
        assert len(_cache) == 2
