from datetime import datetime, timedelta, UTC
from fastapi import status


def test_ping_endpoint_returns_200(client):
    """GET /ping should return 200 OK status."""
    response = client.get("/ping")

    assert response.status_code == status.HTTP_200_OK


def test_ping_endpoint_response_structure(client):
    """GET /ping should return expected JSON structure."""
    response = client.get("/ping")
    data = response.json()

    assert "message" in data
    assert "timestamp" in data
    assert len(data) == 2  # Exactly 2 fields


def test_ping_endpoint_returns_pong(client):
    """GET /ping should return 'pong' message."""
    response = client.get("/ping")
    data = response.json()

    assert data["message"] == "pong"


def test_ping_endpoint_timestamp_is_recent(client):
    """GET /ping should return a timestamp within last 5 seconds."""
    response = client.get("/ping")
    data = response.json()

    timestamp_str = data["timestamp"].replace("Z", "+00:00")
    timestamp = datetime.fromisoformat(timestamp_str)
    now = datetime.now(UTC)

    time_diff = abs((now - timestamp).total_seconds())
    assert time_diff < 5, f"Timestamp is {time_diff}s old"


def test_ping_endpoint_accepts_get_only(client):
    """POST /ping should return 405 Method Not Allowed."""
    response = client.post("/ping")

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_ping_endpoint_openapi_documented(client):
    """GET /ping should be documented in OpenAPI schema."""
    response = client.get("/openapi.json")
    openapi_schema = response.json()

    assert "/ping" in openapi_schema["paths"]
    assert "get" in openapi_schema["paths"]["/ping"]
    ping_endpoint = openapi_schema["paths"]["/ping"]["get"]
    assert ping_endpoint["summary"] == "Ping"
    assert "monitoring" in ping_endpoint["tags"]


def test_ping_endpoint_multiple_calls(client):
    """Multiple calls to /ping should return fresh timestamps."""
    responses = [client.get("/ping") for _ in range(5)]

    assert all(r.status_code == 200 for r in responses)

    timestamps = [
        datetime.fromisoformat(r.json()["timestamp"].replace("Z", "+00:00"))
        for r in responses
    ]

    # All timestamps should be recent
    for ts in timestamps:
        time_diff = abs((datetime.now(UTC) - ts).total_seconds())
        assert time_diff < 10
