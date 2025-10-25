from datetime import datetime
from app.domain.models import HealthCheck, HealthStatus, PingResponse
from app.config import Settings


class HealthService:
    """Application service for health check operations."""

    def __init__(self, settings: Settings):
        """Initialize health service.

        Args:
            settings: Application settings
        """
        self._settings = settings

    def check_health(self) -> HealthCheck:
        """Execute health check logic.

        Returns:
            HealthCheck: Current health status
        """
        # For simple boilerplate, always return healthy
        # Future: Add database connectivity, external service checks, etc.
        return HealthCheck(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow(),
            version=self._settings.app_version,
            environment=self._settings.environment
        )


class PingService:
    """Application service for ping operations."""

    def ping(self) -> PingResponse:
        """Execute ping operation.

        Returns:
            PingResponse: Ping response with timestamp
        """
        return PingResponse(
            message="pong",
            timestamp=datetime.utcnow()
        )
