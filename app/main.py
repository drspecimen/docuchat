from fastapi import FastAPI

from app import __version__
from app.api import health


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title="DocuChat API",
        version=__version__,
        description="Document question-and-answer backend with cited answers.",
    )

    app.include_router(health.router)

    return app


app = create_app()