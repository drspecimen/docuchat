import time
from datetime import datetime, timezone

from app import __version__
from app.schemas.health import HealthResponse

# Recorded once, when the app first imports this module
_STARTED_AT = time.monotonic()


def get_health() -> HealthResponse:
    """Report that the service is running, with version and uptime."""
    return HealthResponse(
        status="ok",
        service="docuchat",
        version=__version__,
        uptime_seconds=round(time.monotonic() - _STARTED_AT, 2),
        timestamp=datetime.now(timezone.utc),
    )