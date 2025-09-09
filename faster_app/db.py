from tortoise import Tortoise
from faster_app.models.discover import ModelDiscover


async def tortoise_init(tortoise_config: dict = None):
    """
    初始化Tortoise ORM

    Args:
        tortoise_config: Tortoise ORM 配置字典，如果不提供则使用默认配置
    """
    if not Tortoise._inited:
        if tortoise_config is None:
            # 提供一个默认的配置示例
            tortoise_config = {
                "connections": {"default": "sqlite://db.sqlite3"},
                "apps": {},
                "use_tz": False,
                "timezone": "UTC",
            }

        # 自动发现模型并添加到配置中
        apps_models = ModelDiscover().discover()

        # 为每个app创建配置
        for app_name, models in apps_models.items():
            tortoise_config["apps"][app_name] = {
                "models": models,
                "default_connection": "default",
            }

        await Tortoise.init(config=tortoise_config)
