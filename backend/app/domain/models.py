from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class HealthStatus(str, Enum):
    """Health check status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class HealthCheck:
    """Domain model for health check information.

    Attributes:
        status: Current health status
        timestamp: Time of health check
        version: Application version
        environment: Runtime environment
    """
    status: HealthStatus
    timestamp: datetime
    version: str
    environment: str

    def __post_init__(self):
        """Validate domain invariants."""
        if not self.version:
            raise ValueError("Version cannot be empty")
        if not self.environment:
            raise ValueError("Environment cannot be empty")


@dataclass(frozen=True)
class PingResponse:
    """Domain model for ping response.

    Attributes:
        message: Response message
        timestamp: Time of ping
    """
    message: str
    timestamp: datetime

    def __post_init__(self):
        """Validate domain invariants."""
        if not self.message:
            raise ValueError("Message cannot be empty")
