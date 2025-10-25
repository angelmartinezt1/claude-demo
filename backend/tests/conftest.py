import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import create_application
from app.config import Settings, get_settings
from app.domain.models import HealthStatus


# ============================================
# Configuration Fixtures
# ============================================

def get_test_settings() -> Settings:
    """Override settings for testing environment.

    Returns test-specific configuration to ensure:
    - Isolated test environment
    - Predictable configuration values
    - No external dependencies
    """
    return Settings(
        app_name="Test FastAPI App",
        app_version="0.0.1-test",
        environment="testing",
        debug=True,
        host="0.0.0.0",
        port=8000,
        cors_origins=["http://localhost:3000"],
        cors_allow_credentials=True,
        cors_allow_methods=["*"],
        cors_allow_headers=["*"]
    )


@pytest.fixture(scope="function")
def test_settings():
    """Provide test settings instance.

    Scope: function - fresh settings per test for isolation
    """
    return get_test_settings()


# ============================================
# Application Fixtures
# ============================================

@pytest.fixture(scope="function")
def test_app():
    """Create a test FastAPI application with overridden dependencies.

    Scope: function - fresh app per test to avoid state leakage

    Usage:
        def test_something(test_app):
            # test_app has test settings injected
    """
    app = create_application()
    app.dependency_overrides[get_settings] = get_test_settings
    yield app
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_app):
    """Create a TestClient for API testing.

    TestClient is synchronous wrapper around httpx.AsyncClient

    Usage:
        def test_endpoint(client):
            response = client.get("/health")
            assert response.status_code == 200
    """
    return TestClient(test_app)


# ============================================
# Time Fixtures (for deterministic testing)
# ============================================

@pytest.fixture
def fixed_datetime():
    """Provide a fixed datetime for testing.

    Returns a fixed UTC timestamp to avoid time-based test flakiness

    Usage:
        def test_timestamp(fixed_datetime, monkeypatch):
            monkeypatch.setattr('app.application.services.datetime',
                              Mock(utcnow=lambda: fixed_datetime))
    """
    return datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)


# ============================================
# Domain Model Fixtures
# ============================================

@pytest.fixture
def valid_health_check_data(fixed_datetime):
    """Valid data for creating HealthCheck domain model."""
    return {
        "status": HealthStatus.HEALTHY,
        "timestamp": fixed_datetime,
        "version": "0.1.0",
        "environment": "testing"
    }


@pytest.fixture
def valid_ping_response_data(fixed_datetime):
    """Valid data for creating PingResponse domain model."""
    return {
        "message": "pong",
        "timestamp": fixed_datetime
    }
