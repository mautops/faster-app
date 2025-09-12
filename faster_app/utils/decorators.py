"""Decorators for common functionality"""

import logging
from functools import wraps
from tortoise import Tortoise
from faster_app.settings import configs

logger = logging.getLogger(__name__)


def with_aerich_command():
    """decorator to handle aerich command lifecycle management."""

    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                await Tortoise.init(config=configs.TORTOISE_ORM)
                return await func(self, *args, **kwargs)
            finally:
                await Tortoise.close_connections()

        return wrapper

    return decorator
