from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger("docuchat.errors")


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last line of defence: any error nobody else handled becomes a clean 500.

    The full details go to the logs; the client only sees a generic message,
    never a stack trace. Step 1.12 adds custom error classes on top of this.
    """
    logger.error(
        "unhandled_exception",
        method=request.method,
        path=request.url.path,
        error_type=type(exc).__name__,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": "Something went wrong"},
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, unhandled_exception_handler)