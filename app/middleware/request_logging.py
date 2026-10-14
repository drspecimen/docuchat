import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("docuchat.http")

# Paths hit constantly by monitoring; logged at debug level to avoid noise
QUIET_PATHS = {"/health"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log one line per request: method, path, status and how long it took."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        fields = {
            "method": request.method,
            "path": request.url.path,  # path only: query strings can carry tokens
            "client_ip": request.client.host if request.client else None,
        }

        try:
            response = await call_next(request)
        except Exception:
            fields["duration_ms"] = round((time.perf_counter() - start) * 1000, 2)
            logger.exception("request_failed", **fields)
            raise

        fields["status_code"] = response.status_code
        fields["duration_ms"] = round((time.perf_counter() - start) * 1000, 2)

        if request.url.path in QUIET_PATHS:
            logger.debug("request_completed", **fields)
        elif response.status_code >= 500:
            logger.error("request_completed", **fields)
        elif response.status_code >= 400:
            logger.warning("request_completed", **fields)
        else:
            logger.info("request_completed", **fields)

        return response