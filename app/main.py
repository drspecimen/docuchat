from fastapi import FastAPI

from app import __version__
from app.api import health
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()  # stops here with a clear message if config is invalid

    app = FastAPI(
        title="DocuChat API",
        version=__version__,
        description="Document question-and-answer backend with cited answers.",
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
    )

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
    )