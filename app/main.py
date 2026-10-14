from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.api import health
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.middleware.request_logging import RequestLoggingMiddleware

logger = get_logger("docuchat.app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Code that runs once when the app starts, and once when it stops."""
    settings = get_settings()
    logger.info("app_started", version=__version__, environment=settings.app_env)
    yield
    logger.info("app_stopped")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()  # stops here with a clear message if config is invalid
    configure_logging(settings)

    app = FastAPI(
        title="DocuChat API",
        version=__version__,
        description="Document question-and-answer backend with cited answers.",
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(health.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=settings.port,
        reload=not settings.is_production,
        log_config=None,  # keep our logging setup instead of Uvicorn's default
    )