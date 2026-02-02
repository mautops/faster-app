"""
Faster APP main startup module.

Entry point for running the FastAPI application with Uvicorn server.
Supports both development mode (with hot reload) and production mode.
"""

import uvicorn
from fastapi_pagination import add_pagination

from faster_app.app import get_app
from faster_app.settings import configs, logger
from faster_app.settings.logging import log_config


def main() -> None:
    """
    Main startup method for Faster APP.

    Initializes the FastAPI application, configures pagination, and
    starts the Uvicorn server. Behavior changes based on DEBUG setting:

    - DEBUG=True: Enables hot reload for development
    - DEBUG=False: Runs in production mode without reload

    Note:
        Server configuration (host, port) is read from configs.

    Example:
        Run from command line: python -m faster_app.main
        Or use CLI: faster server start
    """
    # 创建应用实例
    app = get_app()

    # 添加分页器
    add_pagination(app)

    # 生产环境中不使用 reload, 只在开发环境(DEBUG=True)中启用
    reload = configs.DEBUG

    logger.info(
        f"[服务器启动] 操作: 启动服务器 主机: {configs.SERVER.HOST} 端口: {configs.SERVER.PORT} "
        f"模式: {'开发' if reload else '生产'} 状态: 开始"
    )

    if reload:
        # 开发模式使用字符串导入以支持热重载
        uvicorn.run(
            "faster_app.app:get_app",
            factory=True,
            host=configs.SERVER.HOST,
            port=configs.SERVER.PORT,
            reload=reload,
            log_config=log_config,
        )
    else:
        # 生产模式直接使用应用实例
        uvicorn.run(
            app,
            host=configs.SERVER.HOST,
            port=configs.SERVER.PORT,
            reload=reload,
            log_config=log_config,
        )


if __name__ == "__main__":
    main()
