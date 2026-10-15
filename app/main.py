from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import health
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.middleware.error_handler import register_error_handlers
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

logger = get_logger("docuchat.app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Code that runs once when the app starts, and once when it stops."""
    settings = get_settings()
    logger.info(
        "server_started",
        port=settings.port,
        environment=settings.app_env,
        version=__version__,
    )
    yield
    logger.info("server_stopped")


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

    # === MIDDLEWARE ===
    # Starlette runs the LAST one added FIRST, so they are added in reverse:
    # a request passes CORS -> security headers -> request logging -> route.
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # open for now, like cors() in the lesson; locked down in Step 3.6
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # === ROUTES ===
    app.include_router(health.router)

    # === ERROR HANDLER (catches anything the routes did not handle) ===
    register_error_handlers(app)

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