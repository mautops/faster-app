"""
JWT 配置组
"""

from pydantic import BaseModel, SecretStr, field_validator


class JWTSettings(BaseModel):
    """JWT 配置组"""

    secret_key: SecretStr = SecretStr("your-secret-key-here-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, v):
        """验证 JWT 算法"""
        allowed_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        if v not in allowed_algorithms:
            raise ValueError(
                f"jwt.algorithm 必须是 {allowed_algorithms} 之一，当前值: {v}"
            )
        return v

    @field_validator("access_token_expire_minutes")
    @classmethod
    def validate_token_expire(cls, v):
        """验证 token 过期时间"""
        if v < 1:
            raise ValueError(
                f"jwt.access_token_expire_minutes 必须大于 0，当前值: {v}"
            )
        if v > 43200:  # 30 天
            raise ValueError(
                f"jwt.access_token_expire_minutes 不应超过 43200 分钟（30天），当前值: {v}"
            )
        return v

