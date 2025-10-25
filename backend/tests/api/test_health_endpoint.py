from datetime import datetime, timedelta, UTC
from fastapi import status


def test_health_endpoint_returns_200(client):
    """GET /health should return 200 OK status."""
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK


def test_health_endpoint_response_structure(client):
    """GET /health should return expected JSON structure."""
    response = client.get("/health")
    data = response.json()

    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    assert "environment" in data
    assert len(data) == 4  # Exactly 4 fields


def test_health_endpoint_status_is_healthy(client):
    """GET /health should return 'healthy' status for simple boilerplate."""
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "healthy"


def test_health_endpoint_includes_version(client):
    """GET /health should include version from test settings."""
    response = client.get("/health")
    data = response.json()

    assert data["version"] == "0.0.1-test"


def test_health_endpoint_includes_environment(client):
    """GET /health should include environment from test settings."""
    response = client.get("/health")
    data = response.json()

    assert data["environment"] == "testing"


def test_health_endpoint_timestamp_is_recent(client):
    """GET /health should return a timestamp within last 5 seconds."""
    response = client.get("/health")
    data = response.json()

    # Parse timestamp (handles both with and without 'Z')
    timestamp_str = data["timestamp"].replace("Z", "+00:00")
    timestamp = datetime.fromisoformat(timestamp_str)
    now = datetime.now(UTC)

    time_diff = abs((now - timestamp).total_seconds())
    assert time_diff < 5, f"Timestamp is {time_diff}s old"


def test_health_endpoint_accepts_get_only(client):
    """POST /health should return 405 Method Not Allowed."""
    response = client.post("/health")

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_health_endpoint_openapi_documented(client):
    """GET /health should be documented in OpenAPI schema."""
    response = client.get("/openapi.json")
    openapi_schema = response.json()

    assert "/health" in openapi_schema["paths"]
    assert "get" in openapi_schema["paths"]["/health"]
    health_endpoint = openapi_schema["paths"]["/health"]["get"]
    assert health_endpoint["summary"] == "Health Check"
    assert "monitoring" in health_endpoint["tags"]
