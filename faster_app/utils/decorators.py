"""Decorators for common functionality"""

import logging
from functools import wraps

logger = logging.getLogger(__name__)


def with_aerich_command(tortoise: bool = True):
    """Decorator to handle aerich command lifecycle management.

    Args:
        tortoise: Whether to initialize tortoise connection
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Lazy import to avoid circular dependency
            from faster_app.db import tortoise_init, tortoise_close

            logger.debug(f"Executing {func.__name__} with tortoise={tortoise}")

            # Initialize tortoise if needed
            if tortoise:
                await tortoise_init()

            try:
                # Initialize aerich command if needed (except for init method)
                if tortoise:
                    await self.command.init()

                # Execute the original method
                result = await func(self, *args, **kwargs)
                return result

            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise

            finally:
                # Always close aerich command
                try:
                    await self.command.close()
                except Exception as e:
                    logger.warning(f"Error closing aerich command: {e}")

                # Close tortoise connections if we initialized them
                if tortoise:
                    try:
                        await tortoise_close()
                    except Exception as e:
                        logger.warning(f"Error closing tortoise connections: {e}")

        return wrapper

    return decorator
