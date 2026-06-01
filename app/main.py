import logging
import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.enrichment import router as enrichment_router
from app.api.news import router as news_router
from app.configuration.config import settings
from app.configuration.logger import setup_logging
from app.core.exceptions import NotFoundError

setup_logging()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="API для обогащения новостей",
        description=(
            "API для сбора, обогащения и предоставления новостей. "
            "Поддерживает полнотекстовый поиск, фильтрацию по категории/тегу/домену/автору, "
            "и ручное или запланированное обогащение."
        ),
        version="1.0.0",
        openapi_url="/openapi.json",
    )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    # Routers
    app.include_router(news_router, prefix="/api/v1")
    app.include_router(enrichment_router, prefix="/api/v1")

    return app


app = create_app()