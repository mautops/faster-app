"""
测试认证系统
"""

from unittest.mock import MagicMock

import pytest

# 检查 jwt 模块是否可用
try:
    import jwt

    HAS_JWT = True
except ImportError:
    HAS_JWT = False


class TestNoAuthentication:
    """测试无认证"""

    @pytest.mark.asyncio
    async def test_always_returns_none(self, mock_request: MagicMock):
        """测试总是返回 None"""
        from faster_app.viewsets.authentication import NoAuthentication

        auth = NoAuthentication()
        result = await auth.authenticate(mock_request)
        assert result is None


class TestJWTAuthentication:
    """测试 JWT 认证"""

    @pytest.mark.asyncio
    async def test_no_authorization_header(self, mock_request: MagicMock):
        """测试无 Authorization 头"""
        from faster_app.viewsets.authentication import JWTAuthentication

        auth = JWTAuthentication(secret_key="test-secret")
        result = await auth.authenticate(mock_request)
        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_authorization_format(self, mock_request: MagicMock):
        """测试无效的 Authorization 格式"""
        from faster_app.viewsets.authentication import JWTAuthentication

        mock_request.headers = {"Authorization": "InvalidFormat token"}
        auth = JWTAuthentication(secret_key="test-secret")
        result = await auth.authenticate(mock_request)
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.skipif(not HAS_JWT, reason="PyJWT not installed")
    async def test_valid_jwt_token(self, mock_request: MagicMock):
        """测试有效的 JWT token"""
        import jwt

        from faster_app.viewsets.authentication import JWTAuthentication

        secret = "test-secret"
        payload = {"user_id": 123, "username": "testuser", "is_admin": True}
        token = jwt.encode(payload, secret, algorithm="HS256")

        mock_request.headers = {"Authorization": f"Bearer {token}"}
        auth = JWTAuthentication(secret_key=secret)
        result = await auth.authenticate(mock_request)

        assert result is not None
        user, returned_token = result
        assert user.id == 123
        assert user.username == "testuser"
        assert user.is_admin is True
        assert returned_token == token

    @pytest.mark.asyncio
    @pytest.mark.skipif(not HAS_JWT, reason="PyJWT not installed")
    async def test_expired_token(self, mock_request: MagicMock):
        """测试过期的 token"""
        import time

        import jwt

        from faster_app.viewsets.authentication import JWTAuthentication

        secret = "test-secret"
        payload = {"user_id": 123, "exp": int(time.time()) - 3600}  # 1 小时前过期
        token = jwt.encode(payload, secret, algorithm="HS256")

        mock_request.headers = {"Authorization": f"Bearer {token}"}
        auth = JWTAuthentication(secret_key=secret)
        result = await auth.authenticate(mock_request)

        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_token(self, mock_request: MagicMock):
        """测试无效的 token"""
        from faster_app.viewsets.authentication import JWTAuthentication

        mock_request.headers = {"Authorization": "Bearer invalid.token.here"}
        auth = JWTAuthentication(secret_key="test-secret")
        result = await auth.authenticate(mock_request)

        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.skipif(not HAS_JWT, reason="PyJWT not installed")
    async def test_wrong_secret(self, mock_request: MagicMock):
        """测试错误的密钥"""
        import jwt

        from faster_app.viewsets.authentication import JWTAuthentication

        token = jwt.encode({"user_id": 123}, "correct-secret", algorithm="HS256")
        mock_request.headers = {"Authorization": f"Bearer {token}"}

        auth = JWTAuthentication(secret_key="wrong-secret")
        result = await auth.authenticate(mock_request)

        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.skipif(not HAS_JWT, reason="PyJWT not installed")
    async def test_token_without_user_id(self, mock_request: MagicMock):
        """测试没有 user_id 的 token"""
        import jwt

        from faster_app.viewsets.authentication import JWTAuthentication

        secret = "test-secret"
        token = jwt.encode({"some_field": "value"}, secret, algorithm="HS256")

        mock_request.headers = {"Authorization": f"Bearer {token}"}
        auth = JWTAuthentication(secret_key=secret)
        result = await auth.authenticate(mock_request)

        assert result is None


class TestJWTUser:
    """测试 JWT 用户数据类"""

    def test_jwt_user_creation(self):
        """测试创建 JWT 用户"""
        from faster_app.viewsets.authentication import JWTUser

        user = JWTUser(
            id=1,
            username="testuser",
            is_admin=True,
            is_superuser=False,
            role="editor",
        )

        assert user.id == 1
        assert user.username == "testuser"
        assert user.is_admin is True
        assert user.is_superuser is False
        assert user.role == "editor"

    def test_jwt_user_defaults(self):
        """测试 JWT 用户默认值"""
        from faster_app.viewsets.authentication import JWTUser

        user = JWTUser(id=1)

        assert user.id == 1
        assert user.username is None
        assert user.is_admin is False
        assert user.is_superuser is False
        assert user.role is None


class TestTokenAuthentication:
    """测试 Token 认证"""

    @pytest.mark.asyncio
    async def test_no_token(self, mock_request: MagicMock):
        """测试无 token"""
        from faster_app.viewsets.authentication import TokenAuthentication

        auth = TokenAuthentication()
        result = await auth.authenticate(mock_request)
        assert result is None

    @pytest.mark.asyncio
    async def test_token_in_header(self, mock_request: MagicMock):
        """测试 header 中的 token（占位实现返回 None）"""
        from faster_app.viewsets.authentication import TokenAuthentication

        mock_request.headers = {"Authorization": "Token abc123"}
        auth = TokenAuthentication()
        # 当前占位实现返回 None
        result = await auth.authenticate(mock_request)
        assert result is None


class TestSessionAuthentication:
    """测试 Session 认证"""

    @pytest.mark.asyncio
    async def test_no_session(self, mock_request: MagicMock):
        """测试无 session"""
        from faster_app.viewsets.authentication import SessionAuthentication

        auth = SessionAuthentication()
        result = await auth.authenticate(mock_request)
        assert result is None

    @pytest.mark.asyncio
    async def test_session_without_user(self, mock_request: MagicMock):
        """测试 session 中无用户"""
        from faster_app.viewsets.authentication import SessionAuthentication

        mock_request.session = {}
        auth = SessionAuthentication()
        result = await auth.authenticate(mock_request)
        assert result is None
