"""
测试配置系统
"""

import os

import pytest


class TestDefaultSettings:
    """测试默认配置"""

    def test_default_values(self):
        """测试默认配置值"""
        from faster_app.settings.builtins.settings import DefaultSettings

        # 临时设置环境变量
        os.environ["DEBUG"] = "true"
        settings = DefaultSettings()

        assert settings.PROJECT_NAME == "Faster APP"
        assert settings.DEBUG is True
        assert settings.VERSION == "0.0.1"

    def test_flattened_config(self):
        """测试扁平化配置"""
        from faster_app.settings.builtins.settings import DefaultSettings

        os.environ["DEBUG"] = "true"
        settings = DefaultSettings()

        # 服务器配置
        assert settings.SERVER_HOST == "0.0.0.0"
        assert settings.SERVER_PORT == 8000

        # JWT 配置
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_EXPIRE_MINUTES == 30

        # 日志配置
        assert settings.LOG_LEVEL == "INFO"

    def test_middleware_config(self):
        """测试中间件配置"""
        from faster_app.settings.builtins.settings import DefaultSettings

        os.environ["DEBUG"] = "true"
        settings = DefaultSettings()

        # CORS 配置
        assert "*" in settings.CORS_ORIGINS
        assert settings.CORS_CREDENTIALS is False

        # GZip 配置
        assert settings.GZIP_ENABLED is True
        assert settings.GZIP_MINIMUM_SIZE == 1000

    def test_lifespan_config(self):
        """测试生命周期配置"""
        from faster_app.settings.builtins.settings import DefaultSettings

        os.environ["DEBUG"] = "true"
        settings = DefaultSettings()

        assert settings.LIFESPAN_DATABASE is False
        assert settings.LIFESPAN_APPS is False
        assert settings.LIFESPAN_USER is False

    def test_throttle_config(self):
        """测试限流配置"""
        from faster_app.settings.builtins.settings import DefaultSettings

        os.environ["DEBUG"] = "true"
        settings = DefaultSettings()

        assert settings.THROTTLE_USER_RATE == "100/hour"
        assert settings.THROTTLE_ANON_RATE == "20/hour"
        assert settings.THROTTLE_DEFAULT_RATE == "100/hour"


class TestProductionValidation:
    """测试生产环境配置验证"""

    def test_cors_config_validation(self):
        """测试 CORS 配置验证"""
        from pydantic import ValidationError

        from faster_app.settings.builtins.settings import DefaultSettings

        # 正常配置
        settings = DefaultSettings(
            DEBUG=False,
            JWT_SECRET_KEY="production-secret-key",
            CORS_CREDENTIALS=False,
            CORS_ORIGINS=["*"]
        )
        assert settings.CORS_ORIGINS == ["*"]

        # 不安全配置应该抛出错误
        with pytest.raises(ValidationError, match="CORS 配置不安全"):
            DefaultSettings(
                DEBUG=False,
                JWT_SECRET_KEY="production-secret-key",
                CORS_CREDENTIALS=True,
                CORS_ORIGINS=["*"]
            )

    def test_jwt_secret_validation(self):
        """测试 JWT 密钥验证"""
        from pydantic import ValidationError

        from faster_app.settings.builtins.settings import DefaultSettings

        # 生产环境必须修改默认密钥
        with pytest.raises(ValidationError, match="生产环境必须修改 JWT_SECRET_KEY"):
            DefaultSettings(
                DEBUG=False,
                JWT_SECRET_KEY="your-secret-key-here-change-in-production"
            )


class TestConfigsInstance:
    """测试全局配置实例"""

    def test_configs_is_singleton(self):
        """测试配置是单例"""
        from faster_app.settings import configs
        from faster_app.settings.config import configs as configs2

        assert configs is configs2

    def test_configs_attributes(self):
        """测试配置属性可访问"""
        from faster_app.settings import configs

        # 基础配置
        assert hasattr(configs, "PROJECT_NAME")
        assert hasattr(configs, "DEBUG")
        assert hasattr(configs, "VERSION")

        # 服务器配置
        assert hasattr(configs, "SERVER_HOST")
        assert hasattr(configs, "SERVER_PORT")

        # JWT 配置
        assert hasattr(configs, "JWT_SECRET_KEY")
        assert hasattr(configs, "JWT_ALGORITHM")
        assert hasattr(configs, "JWT_EXPIRE_MINUTES")

        # 数据库配置
        assert hasattr(configs, "DB_URL")

        # 日志配置
        assert hasattr(configs, "LOG_LEVEL")
        assert hasattr(configs, "LOG_FORMAT")

        # 生命周期配置
        assert hasattr(configs, "LIFESPAN_DATABASE")
        assert hasattr(configs, "LIFESPAN_APPS")
        assert hasattr(configs, "LIFESPAN_USER")

        # 限流配置
        assert hasattr(configs, "THROTTLE_USER_RATE")
        assert hasattr(configs, "THROTTLE_ANON_RATE")

        # CORS 配置
        assert hasattr(configs, "CORS_ORIGINS")
        assert hasattr(configs, "CORS_CREDENTIALS")

        # GZip 配置
        assert hasattr(configs, "GZIP_ENABLED")
        assert hasattr(configs, "GZIP_MINIMUM_SIZE")
