from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from faster_app.settings import configs

router = APIRouter()


@router.get("/")
async def default():
    return {
        "message": f"Make {configs.PROJECT_NAME}",
        "version": configs.VERSION,
    }


@router.get("/health")
async def health_check(request: Request):
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": configs.VERSION,
    }


@router.get("/ready")
async def readiness_check(request: Request):
    """就绪检查端点 - 检查所有应用是否已就绪"""
    if not hasattr(request.app.state, "app_registry"):
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "message": "应用注册表未初始化",
            },
        )

    registry = request.app.state.app_registry
    apps_status = []

    for app_info in registry.list_apps():
        app_name = app_info["name"]
        app_state = registry.get_state(app_name)
        app = registry.get_app(app_name)

        status = {
            "name": app_name,
            "state": app_state.value if app_state else "unknown",
        }

        # 如果应用实现了健康检查, 调用它
        if app and hasattr(app, "health_check"):
            try:
                health = await app.health_check()
                status["health"] = health
            except Exception as e:
                status["health"] = {"status": "unhealthy", "error": str(e)}

        apps_status.append(status)

    # 检查是否所有应用都已就绪
    all_ready = all(app["state"] == "ready" for app in apps_status)

    if all_ready:
        return {
            "status": "ready",
            "apps": apps_status,
        }
    else:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "apps": apps_status,
            },
        )
