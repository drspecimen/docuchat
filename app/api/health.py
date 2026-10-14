from fastapi import APIRouter

from app.schemas.health import HealthResponse
from app.services import health_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Liveness check used by monitoring and load balancers."""
    return health_service.get_health()