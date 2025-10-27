from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from faster_app.settings import configs

router = APIRouter()


@router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义 Swagger UI 文档页面"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{configs.PROJECT_NAME} - API 文档",
        swagger_js_url="/static/swagger-ui-bundle.min.js",
        swagger_css_url="/static/swagger-ui.min.css",
    )
