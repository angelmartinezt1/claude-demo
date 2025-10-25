from pydantic import BaseModel, Field
from datetime import datetime
from app.domain.models import HealthStatus


class HealthCheckResponse(BaseModel):
    """HTTP response DTO for health check endpoint.

    Maps from domain HealthCheck model to API response.
    """
    status: HealthStatus
    timestamp: datetime = Field(..., description="ISO 8601 timestamp of health check")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Runtime environment (development/production)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "0.1.0",
                "environment": "development"
            }
        }
    }


class PingResponseDTO(BaseModel):
    """HTTP response DTO for ping endpoint.

    Maps from domain PingResponse model to API response.
    """
    message: str = Field(..., description="Ping response message")
    timestamp: datetime = Field(..., description="ISO 8601 timestamp of ping")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "pong",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    }
