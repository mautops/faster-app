"""
Faster APP 主启动模块
"""

import uvicorn
from faster_app.app import get_app
from faster_app.settings import configs
from faster_app.settings.logging import log_config
from fastapi_pagination import add_pagination


def main():
    """主启动方法"""
    # 创建应用实例
    app = get_app()

    # 添加分页器
    add_pagination(app)

    # 生产环境中不使用 reload，只在开发环境(DEBUG=True)中启用
    reload = configs.DEBUG

    if reload:
        # 开发模式使用字符串导入以支持热重载
        uvicorn.run(
            "faster_app.app:get_app",
            factory=True,
            host=configs.HOST,
            port=configs.PORT,
            reload=reload,
            log_config=log_config,
        )
    else:
        # 生产模式直接使用应用实例
        uvicorn.run(
            app,
            host=configs.HOST,
            port=configs.PORT,
            reload=reload,
            log_config=log_config,
        )


if __name__ == "__main__":
    main()
