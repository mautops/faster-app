"""Database configuration management utilities"""

from typing import Dict, Any
from faster_app.settings.builtins.settings import DefaultSettings
from faster_app.models.discover import ModelDiscover
from faster_app.settings import configs


# Constants
AERICH_APP_NAME = "aerich"
AERICH_MODELS = ["aerich.models"]
DEVELOPMENT_CONNECTION = "development"
PRODUCTION_CONNECTION = "production"


def get_tortoise_config(include_aerich: bool = True) -> Dict[str, Any]:
    """Generate Tortoise ORM configuration.

    Args:
        include_aerich: Whether to include aerich models in configuration

    Returns:
        Complete Tortoise ORM configuration dictionary
    """
    # Get base configuration from settings
    settings = DefaultSettings()
    tortoise_config = settings.TORTOISE_ORM.copy()

    # Discover application models
    apps_models = ModelDiscover().discover()

    # Clear existing apps configuration
    tortoise_config["apps"] = {}

    # Determine connection based on debug mode
    default_connection = (
        DEVELOPMENT_CONNECTION if configs.DEBUG else PRODUCTION_CONNECTION
    )

    # Configure each discovered app
    for app_name, models in apps_models.items():
        tortoise_config["apps"][app_name] = {
            "models": models,
            "default_connection": default_connection,
        }

    # Add aerich models if requested
    if include_aerich:
        tortoise_config["apps"][AERICH_APP_NAME] = {
            "models": AERICH_MODELS,
            "default_connection": default_connection,
        }

    return tortoise_config


def get_aerich_config() -> Dict[str, Any]:
    """Generate Aerich-specific Tortoise configuration.

    Returns:
        Tortoise configuration optimized for Aerich operations
    """
    return get_tortoise_config(include_aerich=True)


def get_app_config() -> Dict[str, Any]:
    """Generate application-only Tortoise configuration.

    Returns:
        Tortoise configuration without Aerich models
    """
    return get_tortoise_config(include_aerich=False)
