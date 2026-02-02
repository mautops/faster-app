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

    def test_nested_config(self):
        """测试嵌套配置"""
        from faster_app.settings.builtins.settings import DefaultSettings

        os.environ["DEBUG"] = "true"
        settings = DefaultSettings()

        # 服务器配置
        assert settings.SERVER.HOST == "0.0.0.0"
        assert settings.SERVER.PORT == 8000

        # JWT 配置
        assert settings.JWT.ALGORITHM == "HS256"
        assert settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES == 30

        # 日志配置
        assert settings.LOG.LEVEL == "INFO"

    def test_middleware_config(self):
        """测试中间件配置"""
        from faster_app.settings.builtins.settings import DefaultSettings

        os.environ["DEBUG"] = "true"
        settings = DefaultSettings()

        # CORS 配置
        assert "*" in settings.MIDDLEWARE.CORS.ALLOW_ORIGINS
        assert settings.MIDDLEWARE.CORS.ALLOW_CREDENTIALS is False

        # GZip 配置
        assert settings.MIDDLEWARE.GZIP.ENABLED is True
        assert settings.MIDDLEWARE.GZIP.MINIMUM_SIZE == 1000

    def test_lifespan_config(self):
        """测试生命周期配置"""
        from faster_app.settings.builtins.settings import DefaultSettings

        os.environ["DEBUG"] = "true"
        settings = DefaultSettings()

        assert settings.LIFESPAN.ENABLE_DATABASE is False
        assert settings.LIFESPAN.ENABLE_APPS is False
        assert settings.LIFESPAN.ENABLE_USER is False

    def test_throttle_config(self):
        """测试限流配置"""
        from faster_app.settings.builtins.settings import DefaultSettings

        os.environ["DEBUG"] = "true"
        settings = DefaultSettings()

        assert "user" in settings.THROTTLE.RATES
        assert "anon" in settings.THROTTLE.RATES
        assert "default" in settings.THROTTLE.RATES


class TestConfigModels:
    """测试配置模型"""

    def test_server_config(self):
        """测试服务器配置模型"""
        from faster_app.settings.builtins.settings import ServerConfig

        config = ServerConfig()
        assert config.HOST == "0.0.0.0"
        assert config.PORT == 8000

    def test_jwt_config(self):
        """测试 JWT 配置模型"""
        from faster_app.settings.builtins.settings import JWTConfig

        config = JWTConfig()
        assert config.ALGORITHM == "HS256"
        assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_cors_config_validation(self):
        """测试 CORS 配置验证"""
        from pydantic import ValidationError

        from faster_app.settings.builtins.settings import CORSConfig

        # 正常配置 (使用 validation_alias 名称进行初始化)
        config = CORSConfig.model_validate({
            "CORS_ALLOW_CREDENTIALS": False,
            "CORS_ALLOW_ORIGINS": ["*"]
        })
        assert config.ALLOW_ORIGINS == ["*"]

        # 不安全配置应该抛出错误 (Pydantic v2 将 ValueError 包装为 ValidationError)
        with pytest.raises(ValidationError):
            CORSConfig.model_validate({
                "CORS_ALLOW_CREDENTIALS": True,
                "CORS_ALLOW_ORIGINS": ["*"]
            })

    def test_log_config(self):
        """测试日志配置模型"""
        from faster_app.settings.builtins.settings import LogConfig

        config = LogConfig()
        assert config.LEVEL == "INFO"
        assert config.FORMAT == "STRING"
        assert config.TO_FILE is False


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

        assert hasattr(configs, "PROJECT_NAME")
        assert hasattr(configs, "DEBUG")
        assert hasattr(configs, "SERVER")
        assert hasattr(configs, "JWT")
        assert hasattr(configs, "DATABASE")
        assert hasattr(configs, "LOG")
        assert hasattr(configs, "MIDDLEWARE")
