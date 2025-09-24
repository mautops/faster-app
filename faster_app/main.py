"""
Faster APP 主启动模块
"""

import os
import sys
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
    # 将当前工作目录添加到 Python 路径，确保可以导入项目模块
    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # 设置 PYTHONPATH 环境变量，确保子进程也能找到项目模块
    pythonpath = os.environ.get("PYTHONPATH", "")
    if current_dir not in pythonpath:
        os.environ["PYTHONPATH"] = (
            current_dir + ":" + pythonpath if pythonpath else current_dir
        )

    # 启动主程序
    main()
