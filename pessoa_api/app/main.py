from fastapi import FastAPI

from app.api.error_handlers import register_exception_handlers
from app.api.health import router as health_router
from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=("API REST didática com FastAPI, Pydantic, SQLAlchemy, Alembic e PostgreSQL."),
    )
    register_exception_handlers(application)
    application.include_router(health_router)
    application.include_router(v1_router)
    return application


app = create_app()
