from fastapi import APIRouter, Depends
from app.infrastructure.web.dto import HealthCheckResponse, PingResponseDTO
from app.application.services import HealthService, PingService
from app.config import Settings, get_settings


router = APIRouter(
    prefix="",
    tags=["monitoring"],
)


def get_health_service(settings: Settings = Depends(get_settings)) -> HealthService:
    """Dependency injection for health service.

    Args:
        settings: Application settings (injected)

    Returns:
        HealthService: Configured health service instance
    """
    return HealthService(settings)


def get_ping_service() -> PingService:
    """Dependency injection for ping service.

    Returns:
        PingService: Ping service instance
    """
    return PingService()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=200,
    summary="Health Check",
    description="Returns the current health status of the application",
)
async def health_check(
    service: HealthService = Depends(get_health_service)
) -> HealthCheckResponse:
    """Health check endpoint.

    Returns application health status, version, and environment information.

    Args:
        service: Health service (injected)

    Returns:
        HealthCheckResponse: Current health status
    """
    health = service.check_health()

    return HealthCheckResponse(
        status=health.status,
        timestamp=health.timestamp,
        version=health.version,
        environment=health.environment
    )


@router.get(
    "/ping",
    response_model=PingResponseDTO,
    status_code=200,
    summary="Ping",
    description="Simple ping endpoint to test connectivity",
)
async def ping(
    service: PingService = Depends(get_ping_service)
) -> PingResponseDTO:
    """Ping endpoint.

    Returns a simple pong response with timestamp.

    Args:
        service: Ping service (injected)

    Returns:
        PingResponseDTO: Pong response with timestamp
    """
    response = service.ping()

    return PingResponseDTO(
        message=response.message,
        timestamp=response.timestamp
    )
