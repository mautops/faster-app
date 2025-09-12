"""Database initialization and management utilities"""

import logging
from typing import Optional, Dict, Any
from tortoise import Tortoise
from faster_app.utils.config import get_app_config

logger = logging.getLogger(__name__)


async def tortoise_init(config: Optional[Dict[str, Any]] = None) -> None:
    """Initialize Tortoise ORM with application configuration.

    Args:
        config: Optional Tortoise configuration. If None, uses project default.

    Raises:
        RuntimeError: If initialization fails
    """
    if Tortoise._inited:
        logger.debug("Tortoise ORM already initialized, skipping")
        return

    try:
        if config is None:
            config = get_app_config()

        logger.debug(
            "Initializing Tortoise ORM with config: %s", config.get("connections", {})
        )
        await Tortoise.init(config=config)
        logger.info("Tortoise ORM initialized successfully")

    except Exception as e:
        logger.error("Failed to initialize Tortoise ORM: %s", e)
        raise RuntimeError(f"Tortoise initialization failed: {e}") from e


async def tortoise_close() -> None:
    """Close Tortoise ORM connections safely."""
    try:
        if Tortoise._inited:
            await Tortoise.close_connections()
            logger.info("Tortoise ORM connections closed")
        else:
            logger.debug("Tortoise ORM not initialized, nothing to close")
    except Exception as e:
        logger.error("Error closing Tortoise connections: %s", e)
        raise
