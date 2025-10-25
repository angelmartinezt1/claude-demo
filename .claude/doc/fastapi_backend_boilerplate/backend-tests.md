# FastAPI Backend Boilerplate - Comprehensive Test Plan

## Executive Summary

This document provides a complete testing strategy for the FastAPI backend boilerplate implementation. The plan covers unit tests, integration tests, and API tests across all architectural layers (domain, application, infrastructure) following hexagonal architecture principles and pytest best practices.

**Testing Approach:**
- Test Pyramid: Many unit tests, fewer integration tests
- Layer-based organization: Tests mirror the application structure
- Comprehensive coverage: Both happy paths and error scenarios
- Mock isolation: Unit tests use mocks, integration tests use real components
- Fixture reuse: Shared test data and setup via pytest fixtures

**Coverage Target:** 95-100% (achievable for this simple boilerplate)

---

## 1. Testing Strategy Overview

### 1.1 Test Categories

| Category | Scope | Tools | Coverage |
|----------|-------|-------|----------|
| **Unit Tests** | Domain models, services (isolated) | pytest, unittest.mock | 60% of tests |
| **Integration Tests** | Service + dependencies, exception handlers | pytest, TestClient | 30% of tests |
| **API Tests** | Full endpoint flows, HTTP layer | pytest, TestClient, httpx | 10% of tests |

### 1.2 Test Organization

```
backend/tests/
├── __init__.py
├── conftest.py                     # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_domain_models.py       # Domain layer unit tests
│   ├── test_services.py            # Application layer unit tests
│   └── test_config.py              # Configuration unit tests
├── integration/
│   ├── __init__.py
│   ├── test_exception_handlers.py  # Middleware integration tests
│   └── test_dto_mapping.py         # DTO validation tests
└── api/
    ├── __init__.py
    ├── test_health_endpoint.py     # Health endpoint API tests
    └── test_ping_endpoint.py       # Ping endpoint API tests
```

### 1.3 Testing Principles

**DO:**
- Test behavior, not implementation
- Use descriptive test names (test_should_xxx_when_yyy)
- Follow AAA pattern (Arrange, Act, Assert)
- Isolate tests with fresh fixtures
- Mock external dependencies in unit tests
- Test edge cases and error conditions
- Use parametrized tests for similar scenarios

**DON'T:**
- Test framework code (FastAPI, Pydantic internals)
- Share state between tests
- Use hard-coded timestamps or random values
- Test multiple behaviors in one test
- Skip error scenario testing
- Use sleep() or time-based assertions

---

## 2. Test Infrastructure Setup

### 2.1 conftest.py - Shared Fixtures

**File:** `backend/tests/conftest.py`

```python
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock
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


# ============================================
# Mock Service Fixtures
# ============================================

@pytest.fixture
def mock_health_service():
    """Mock HealthService for testing routers in isolation.

    Usage:
        def test_router(mock_health_service):
            mock_health_service.check_health.return_value = HealthCheck(...)
    """
    return Mock()


@pytest.fixture
def mock_ping_service():
    """Mock PingService for testing routers in isolation."""
    return Mock()
```

**Key Design Decisions:**

1. **Function Scope for App Fixtures**: Ensures test isolation, prevents state leakage
2. **Fixed Datetime**: Eliminates time-based test flakiness
3. **Test Settings Override**: Uses dependency injection to inject test config
4. **Mock Fixtures**: Enables unit testing of routers without services
5. **Data Fixtures**: Reusable valid data structures for domain objects

---

## 3. Unit Tests - Domain Layer

### 3.1 test_domain_models.py

**File:** `backend/tests/unit/test_domain_models.py`

**Purpose:** Validate domain models enforce business rules and invariants

#### Test Cases for HealthStatus Enum

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_health_status_has_healthy_value` | Check HEALTHY enum value | Value is "healthy" |
| `test_health_status_has_unhealthy_value` | Check UNHEALTHY enum value | Value is "unhealthy" |
| `test_health_status_has_degraded_value` | Check DEGRADED enum value | Value is "degraded" |
| `test_health_status_is_string_enum` | Check enum inherits from str | Instance of str |
| `test_health_status_can_be_compared_as_string` | Compare enum to string | Equality works |

**Example Test:**
```python
def test_health_status_has_healthy_value():
    """HealthStatus.HEALTHY should have value 'healthy'."""
    assert HealthStatus.HEALTHY == "healthy"
    assert HealthStatus.HEALTHY.value == "healthy"
```

#### Test Cases for HealthCheck Dataclass

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_health_check_creation_with_valid_data` | Create with all valid fields | Instance created successfully |
| `test_health_check_is_frozen` | Try to modify frozen dataclass | AttributeError raised |
| `test_health_check_requires_status` | Create without status | TypeError raised |
| `test_health_check_requires_timestamp` | Create without timestamp | TypeError raised |
| `test_health_check_requires_version` | Create without version | TypeError raised |
| `test_health_check_requires_environment` | Create without environment | TypeError raised |
| `test_health_check_rejects_empty_version` | Create with empty string version | ValueError raised |
| `test_health_check_rejects_empty_environment` | Create with empty string environment | ValueError raised |
| `test_health_check_accepts_all_status_values` | Create with each status (parametrized) | All status values work |
| `test_health_check_timestamp_is_datetime` | Check timestamp type | Is datetime instance |
| `test_health_check_has_all_attributes` | Check all attributes exist | All 4 attributes accessible |

**Example Tests:**
```python
def test_health_check_creation_with_valid_data(valid_health_check_data):
    """HealthCheck should be created with all valid data."""
    health = HealthCheck(**valid_health_check_data)

    assert health.status == valid_health_check_data["status"]
    assert health.timestamp == valid_health_check_data["timestamp"]
    assert health.version == valid_health_check_data["version"]
    assert health.environment == valid_health_check_data["environment"]


def test_health_check_is_frozen(valid_health_check_data):
    """HealthCheck should be immutable (frozen dataclass)."""
    health = HealthCheck(**valid_health_check_data)

    with pytest.raises(AttributeError):
        health.status = HealthStatus.UNHEALTHY


def test_health_check_rejects_empty_version(valid_health_check_data):
    """HealthCheck should raise ValueError for empty version."""
    invalid_data = {**valid_health_check_data, "version": ""}

    with pytest.raises(ValueError, match="Version cannot be empty"):
        HealthCheck(**invalid_data)


@pytest.mark.parametrize("status", [
    HealthStatus.HEALTHY,
    HealthStatus.UNHEALTHY,
    HealthStatus.DEGRADED
])
def test_health_check_accepts_all_status_values(valid_health_check_data, status):
    """HealthCheck should accept all valid HealthStatus values."""
    data = {**valid_health_check_data, "status": status}
    health = HealthCheck(**data)

    assert health.status == status
```

#### Test Cases for PingResponse Dataclass

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_ping_response_creation_with_valid_data` | Create with valid message and timestamp | Instance created successfully |
| `test_ping_response_is_frozen` | Try to modify frozen dataclass | AttributeError raised |
| `test_ping_response_requires_message` | Create without message | TypeError raised |
| `test_ping_response_requires_timestamp` | Create without timestamp | TypeError raised |
| `test_ping_response_rejects_empty_message` | Create with empty string message | ValueError raised |
| `test_ping_response_timestamp_is_datetime` | Check timestamp type | Is datetime instance |
| `test_ping_response_has_both_attributes` | Check both attributes exist | message and timestamp accessible |

**Example Tests:**
```python
def test_ping_response_creation_with_valid_data(valid_ping_response_data):
    """PingResponse should be created with valid data."""
    ping = PingResponse(**valid_ping_response_data)

    assert ping.message == valid_ping_response_data["message"]
    assert ping.timestamp == valid_ping_response_data["timestamp"]


def test_ping_response_rejects_empty_message(valid_ping_response_data):
    """PingResponse should raise ValueError for empty message."""
    invalid_data = {**valid_ping_response_data, "message": ""}

    with pytest.raises(ValueError, match="Message cannot be empty"):
        PingResponse(**invalid_data)
```

**Test Statistics:**
- HealthStatus: 5 tests
- HealthCheck: 11 tests
- PingResponse: 7 tests
- **Total Domain Tests: 23 tests**

---

## 4. Unit Tests - Application Layer

### 4.1 test_services.py

**File:** `backend/tests/unit/test_services.py`

**Purpose:** Test service business logic in isolation using mocked dependencies

#### Test Cases for HealthService

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_health_service_initialization` | Initialize with settings | Service created successfully |
| `test_health_service_stores_settings` | Check settings are stored | Settings accessible via private attribute |
| `test_check_health_returns_health_check` | Call check_health() | Returns HealthCheck instance |
| `test_check_health_returns_healthy_status` | Call check_health() | Status is HEALTHY |
| `test_check_health_includes_version_from_settings` | Call check_health() | Version matches settings.app_version |
| `test_check_health_includes_environment_from_settings` | Call check_health() | Environment matches settings.environment |
| `test_check_health_includes_timestamp` | Call check_health() | Timestamp is recent (within 1 second) |
| `test_check_health_timestamp_is_utc` | Call check_health() with mocked time | Timestamp uses datetime.utcnow() |
| `test_check_health_with_different_settings` | Create service with custom settings | Returns custom version/environment |

**Example Tests:**
```python
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.application.services import HealthService
from app.domain.models import HealthCheck, HealthStatus
from app.config import Settings


def test_health_service_initialization(test_settings):
    """HealthService should initialize with settings."""
    service = HealthService(test_settings)

    assert service._settings == test_settings


def test_check_health_returns_healthy_status(test_settings):
    """check_health() should return HEALTHY status for simple boilerplate."""
    service = HealthService(test_settings)

    result = service.check_health()

    assert result.status == HealthStatus.HEALTHY


def test_check_health_includes_version_from_settings(test_settings):
    """check_health() should include app version from settings."""
    service = HealthService(test_settings)

    result = service.check_health()

    assert result.version == test_settings.app_version


def test_check_health_timestamp_is_utc(test_settings, fixed_datetime):
    """check_health() should use datetime.utcnow() for timestamp."""
    service = HealthService(test_settings)

    with patch('app.application.services.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = fixed_datetime
        result = service.check_health()

    assert result.timestamp == fixed_datetime


def test_check_health_with_different_settings():
    """check_health() should use settings values in response."""
    custom_settings = Settings(
        app_name="Custom App",
        app_version="1.2.3",
        environment="production"
    )
    service = HealthService(custom_settings)

    result = service.check_health()

    assert result.version == "1.2.3"
    assert result.environment == "production"
```

#### Test Cases for PingService

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_ping_service_initialization` | Initialize service | Service created successfully |
| `test_ping_returns_ping_response` | Call ping() | Returns PingResponse instance |
| `test_ping_returns_pong_message` | Call ping() | Message is "pong" |
| `test_ping_includes_timestamp` | Call ping() | Timestamp is recent (within 1 second) |
| `test_ping_timestamp_is_utc` | Call ping() with mocked time | Timestamp uses datetime.utcnow() |
| `test_ping_service_has_no_dependencies` | Check constructor | No parameters required |

**Example Tests:**
```python
from app.application.services import PingService
from app.domain.models import PingResponse


def test_ping_service_initialization():
    """PingService should initialize without dependencies."""
    service = PingService()

    assert service is not None


def test_ping_returns_pong_message():
    """ping() should return 'pong' message."""
    service = PingService()

    result = service.ping()

    assert result.message == "pong"


def test_ping_timestamp_is_utc(fixed_datetime):
    """ping() should use datetime.utcnow() for timestamp."""
    service = PingService()

    with patch('app.application.services.datetime') as mock_datetime:
        mock_datetime.utcnow.return_value = fixed_datetime
        result = service.ping()

    assert result.timestamp == fixed_datetime
```

**Test Statistics:**
- HealthService: 9 tests
- PingService: 6 tests
- **Total Service Tests: 15 tests**

---

## 5. Unit Tests - Configuration

### 5.1 test_config.py

**File:** `backend/tests/unit/test_config.py`

**Purpose:** Validate configuration management and dependency injection

#### Test Cases for Settings

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_settings_default_values` | Create Settings without env vars | All defaults loaded |
| `test_settings_app_name_default` | Check default app_name | Correct default value |
| `test_settings_app_version_default` | Check default app_version | Correct default value |
| `test_settings_environment_default` | Check default environment | "development" |
| `test_settings_debug_default` | Check default debug | False |
| `test_settings_host_default` | Check default host | "0.0.0.0" |
| `test_settings_port_default` | Check default port | 8000 |
| `test_settings_cors_origins_default` | Check default CORS origins | localhost:3000 and :5173 |
| `test_settings_loads_from_env_prefix` | Set APP_ENVIRONMENT env var | Loads with APP_ prefix |
| `test_settings_case_insensitive` | Set APP_ENVIRONMENT in different case | Loads case-insensitively |
| `test_settings_ignores_extra_fields` | Set unknown env var | Extra fields ignored |
| `test_settings_validates_types` | Set invalid type for port | Pydantic validation error |
| `test_settings_cors_origins_is_list` | Check cors_origins type | Is list of strings |

**Example Tests:**
```python
import os
import pytest
from app.config import Settings, get_settings


def test_settings_default_values():
    """Settings should have correct default values."""
    settings = Settings()

    assert settings.app_name == "FastAPI Backend Boilerplate"
    assert settings.app_version == "0.1.0"
    assert settings.environment == "development"
    assert settings.debug is False
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000


def test_settings_loads_from_env_prefix(monkeypatch):
    """Settings should load from environment with APP_ prefix."""
    monkeypatch.setenv("APP_ENVIRONMENT", "staging")
    monkeypatch.setenv("APP_DEBUG", "true")

    # Clear cache to force reload
    get_settings.cache_clear()
    settings = Settings()

    assert settings.environment == "staging"
    assert settings.debug is True


def test_settings_cors_origins_is_list():
    """Settings.cors_origins should be a list of strings."""
    settings = Settings()

    assert isinstance(settings.cors_origins, list)
    assert all(isinstance(origin, str) for origin in settings.cors_origins)
    assert "http://localhost:3000" in settings.cors_origins
```

#### Test Cases for get_settings()

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_get_settings_returns_settings_instance` | Call get_settings() | Returns Settings instance |
| `test_get_settings_is_cached` | Call twice | Returns same instance (lru_cache) |
| `test_get_settings_cache_clear_works` | Clear cache and call again | Returns new instance |
| `test_get_settings_can_be_used_as_dependency` | Use with FastAPI Depends | Works as dependency |

**Example Tests:**
```python
def test_get_settings_returns_settings_instance():
    """get_settings() should return Settings instance."""
    get_settings.cache_clear()
    settings = get_settings()

    assert isinstance(settings, Settings)


def test_get_settings_is_cached():
    """get_settings() should return cached instance (singleton pattern)."""
    get_settings.cache_clear()

    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2  # Same object reference
```

**Test Statistics:**
- Settings: 13 tests
- get_settings: 4 tests
- **Total Config Tests: 17 tests**

---

## 6. Integration Tests - Infrastructure Layer

### 6.1 test_exception_handlers.py

**File:** `backend/tests/integration/test_exception_handlers.py`

**Purpose:** Test exception handlers with real FastAPI request/response cycle

#### Test Cases for http_exception_handler

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_http_exception_handler_404` | Raise HTTPException with 404 | Returns 404 with error format |
| `test_http_exception_handler_500` | Raise HTTPException with 500 | Returns 500 with error format |
| `test_http_exception_handler_custom_message` | Raise with custom message | Message included in response |
| `test_http_exception_handler_error_structure` | Check response structure | Has error.type, error.message, error.status_code |
| `test_http_exception_handler_error_type` | Check error type | Type is "http_error" |

**Example Tests:**
```python
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from app.infrastructure.middleware.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError


def test_http_exception_handler_404(client):
    """HTTP 404 exceptions should return formatted error response."""
    # Create a route that raises 404
    @client.app.get("/test-404")
    async def test_404():
        raise HTTPException(status_code=404, detail="Resource not found")

    response = client.get("/test-404")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "type": "http_error",
            "message": "Resource not found",
            "status_code": 404
        }
    }


def test_http_exception_handler_error_structure(client):
    """HTTP exceptions should have consistent error structure."""
    @client.app.get("/test-error-structure")
    async def test_error():
        raise HTTPException(status_code=400, detail="Bad request")

    response = client.get("/test-error-structure")
    data = response.json()

    assert "error" in data
    assert "type" in data["error"]
    assert "message" in data["error"]
    assert "status_code" in data["error"]
```

#### Test Cases for validation_exception_handler

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_validation_exception_handler_missing_field` | Request missing required field | Returns 422 with validation error |
| `test_validation_exception_handler_wrong_type` | Request with wrong field type | Returns 422 with type error |
| `test_validation_exception_handler_error_structure` | Check response structure | Has error.type, error.message, error.details |
| `test_validation_exception_handler_error_type` | Check error type | Type is "validation_error" |
| `test_validation_exception_handler_includes_details` | Check error details | Includes Pydantic error details |

**Example Tests:**
```python
from pydantic import BaseModel


def test_validation_exception_handler_missing_field(client):
    """Missing required fields should return 422 validation error."""

    class TestRequest(BaseModel):
        required_field: str

    @client.app.post("/test-validation")
    async def test_validation(data: TestRequest):
        return {"ok": True}

    response = client.post("/test-validation", json={})

    assert response.status_code == 422
    data = response.json()
    assert data["error"]["type"] == "validation_error"
    assert data["error"]["message"] == "Request validation failed"
    assert "details" in data["error"]
```

#### Test Cases for generic_exception_handler

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_generic_exception_handler_catches_unexpected` | Raise unexpected exception | Returns 500 with generic message |
| `test_generic_exception_handler_error_structure` | Check response structure | Has error.type, error.message |
| `test_generic_exception_handler_error_type` | Check error type | Type is "internal_error" |
| `test_generic_exception_handler_hides_details` | Raise exception with sensitive info | Details not exposed to client |

**Example Tests:**
```python
def test_generic_exception_handler_catches_unexpected(client):
    """Unexpected exceptions should return 500 with generic message."""

    @client.app.get("/test-unexpected")
    async def test_unexpected():
        raise RuntimeError("Something went wrong internally")

    response = client.get("/test-unexpected")

    assert response.status_code == 500
    data = response.json()
    assert data["error"]["type"] == "internal_error"
    assert data["error"]["message"] == "An unexpected error occurred"
    # Should NOT expose internal error details
    assert "RuntimeError" not in str(data)
```

**Test Statistics:**
- http_exception_handler: 5 tests
- validation_exception_handler: 5 tests
- generic_exception_handler: 4 tests
- **Total Exception Handler Tests: 14 tests**

---

### 6.2 test_dto_mapping.py

**File:** `backend/tests/integration/test_dto_mapping.py`

**Purpose:** Test Pydantic DTO validation and serialization

#### Test Cases for HealthCheckResponse DTO

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_health_check_response_validation` | Create with valid data | DTO created successfully |
| `test_health_check_response_requires_all_fields` | Create with missing field | Pydantic ValidationError |
| `test_health_check_response_serialization` | Call model_dump() | Correct dict output |
| `test_health_check_response_json_serialization` | Call model_dump_json() | Valid JSON string |
| `test_health_check_response_timestamp_format` | Check timestamp serialization | ISO 8601 format |
| `test_health_check_response_accepts_health_status` | Pass HealthStatus enum | Accepts all status values |
| `test_health_check_response_schema` | Check JSON schema | Schema includes examples |

**Example Tests:**
```python
from datetime import datetime
from app.infrastructure.web.dto import HealthCheckResponse, PingResponseDTO
from app.domain.models import HealthStatus
import json


def test_health_check_response_validation():
    """HealthCheckResponse should validate and create with valid data."""
    dto = HealthCheckResponse(
        status=HealthStatus.HEALTHY,
        timestamp=datetime.utcnow(),
        version="0.1.0",
        environment="testing"
    )

    assert dto.status == HealthStatus.HEALTHY
    assert dto.version == "0.1.0"
    assert dto.environment == "testing"


def test_health_check_response_serialization():
    """HealthCheckResponse should serialize to dict correctly."""
    timestamp = datetime(2024, 1, 15, 10, 30, 0)
    dto = HealthCheckResponse(
        status=HealthStatus.HEALTHY,
        timestamp=timestamp,
        version="0.1.0",
        environment="testing"
    )

    data = dto.model_dump()

    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert data["environment"] == "testing"
    assert isinstance(data["timestamp"], datetime)
```

#### Test Cases for PingResponseDTO

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_ping_response_dto_validation` | Create with valid data | DTO created successfully |
| `test_ping_response_dto_requires_all_fields` | Create with missing field | Pydantic ValidationError |
| `test_ping_response_dto_serialization` | Call model_dump() | Correct dict output |
| `test_ping_response_dto_json_serialization` | Call model_dump_json() | Valid JSON string |
| `test_ping_response_dto_timestamp_format` | Check timestamp serialization | ISO 8601 format |
| `test_ping_response_dto_schema` | Check JSON schema | Schema includes examples |

**Example Tests:**
```python
def test_ping_response_dto_validation():
    """PingResponseDTO should validate and create with valid data."""
    dto = PingResponseDTO(
        message="pong",
        timestamp=datetime.utcnow()
    )

    assert dto.message == "pong"
    assert isinstance(dto.timestamp, datetime)


def test_ping_response_dto_json_serialization():
    """PingResponseDTO should serialize to JSON correctly."""
    timestamp = datetime(2024, 1, 15, 10, 30, 0)
    dto = PingResponseDTO(
        message="pong",
        timestamp=timestamp
    )

    json_str = dto.model_dump_json()
    data = json.loads(json_str)

    assert data["message"] == "pong"
    assert "timestamp" in data
```

**Test Statistics:**
- HealthCheckResponse: 7 tests
- PingResponseDTO: 6 tests
- **Total DTO Tests: 13 tests**

---

## 7. API Tests - Endpoint Layer

### 7.1 test_health_endpoint.py

**File:** `backend/tests/api/test_health_endpoint.py`

**Purpose:** Test /health endpoint end-to-end with full application context

#### Test Cases for /health Endpoint

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_health_endpoint_returns_200` | GET /health | Returns 200 OK |
| `test_health_endpoint_returns_json` | GET /health | Returns application/json |
| `test_health_endpoint_response_structure` | Check response shape | Has status, timestamp, version, environment |
| `test_health_endpoint_status_is_healthy` | Check status field | Status is "healthy" |
| `test_health_endpoint_includes_version` | Check version field | Version matches test settings |
| `test_health_endpoint_includes_environment` | Check environment field | Environment is "testing" |
| `test_health_endpoint_timestamp_is_recent` | Check timestamp | Within last 5 seconds |
| `test_health_endpoint_timestamp_format` | Check timestamp format | Valid ISO 8601 format |
| `test_health_endpoint_accepts_get_only` | Try POST /health | Returns 405 Method Not Allowed |
| `test_health_endpoint_cors_headers` | Check CORS headers | Has Access-Control-* headers |
| `test_health_endpoint_no_auth_required` | Call without credentials | Returns 200 (public endpoint) |
| `test_health_endpoint_openapi_documented` | Check OpenAPI schema | Documented in /openapi.json |

**Example Tests:**
```python
from datetime import datetime, timedelta
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


def test_health_endpoint_timestamp_is_recent(client):
    """GET /health should return a timestamp within last 5 seconds."""
    response = client.get("/health")
    data = response.json()

    # Parse timestamp (handles both with and without 'Z')
    timestamp_str = data["timestamp"].replace("Z", "+00:00")
    timestamp = datetime.fromisoformat(timestamp_str)
    now = datetime.utcnow()

    time_diff = abs((now - timestamp.replace(tzinfo=None)).total_seconds())
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
```

**Test Statistics:**
- /health endpoint: 12 tests

---

### 7.2 test_ping_endpoint.py

**File:** `backend/tests/api/test_ping_endpoint.py`

**Purpose:** Test /ping endpoint end-to-end with full application context

#### Test Cases for /ping Endpoint

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_ping_endpoint_returns_200` | GET /ping | Returns 200 OK |
| `test_ping_endpoint_returns_json` | GET /ping | Returns application/json |
| `test_ping_endpoint_response_structure` | Check response shape | Has message and timestamp |
| `test_ping_endpoint_returns_pong` | Check message field | Message is "pong" |
| `test_ping_endpoint_timestamp_is_recent` | Check timestamp | Within last 5 seconds |
| `test_ping_endpoint_timestamp_format` | Check timestamp format | Valid ISO 8601 format |
| `test_ping_endpoint_accepts_get_only` | Try POST /ping | Returns 405 Method Not Allowed |
| `test_ping_endpoint_cors_headers` | Check CORS headers | Has Access-Control-* headers |
| `test_ping_endpoint_no_auth_required` | Call without credentials | Returns 200 (public endpoint) |
| `test_ping_endpoint_openapi_documented` | Check OpenAPI schema | Documented in /openapi.json |
| `test_ping_endpoint_multiple_calls` | Call 5 times | All return fresh timestamps |

**Example Tests:**
```python
from datetime import datetime, timedelta
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
    now = datetime.utcnow()

    time_diff = abs((now - timestamp.replace(tzinfo=None)).total_seconds())
    assert time_diff < 5, f"Timestamp is {time_diff}s old"


def test_ping_endpoint_multiple_calls(client):
    """Multiple calls to /ping should return fresh timestamps."""
    responses = [client.get("/ping") for _ in range(5)]

    assert all(r.status_code == 200 for r in responses)

    timestamps = [
        datetime.fromisoformat(r.json()["timestamp"].replace("Z", "+00:00"))
        for r in responses
    ]

    # All timestamps should be unique (or very close)
    # All should be recent
    for ts in timestamps:
        time_diff = abs((datetime.utcnow() - ts.replace(tzinfo=None)).total_seconds())
        assert time_diff < 10


def test_ping_endpoint_openapi_documented(client):
    """GET /ping should be documented in OpenAPI schema."""
    response = client.get("/openapi.json")
    openapi_schema = response.json()

    assert "/ping" in openapi_schema["paths"]
    assert "get" in openapi_schema["paths"]["/ping"]
    ping_endpoint = openapi_schema["paths"]["/ping"]["get"]
    assert ping_endpoint["summary"] == "Ping"
    assert "monitoring" in ping_endpoint["tags"]
```

**Test Statistics:**
- /ping endpoint: 11 tests

---

## 8. Additional Test Scenarios

### 8.1 CORS Testing (Optional Enhancement)

**File:** `backend/tests/integration/test_cors.py`

#### Test Cases for CORS

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_cors_allows_configured_origins` | Request from allowed origin | CORS headers present |
| `test_cors_preflight_request` | OPTIONS request | Returns 200 with CORS headers |
| `test_cors_credentials_allowed` | Check credentials header | Access-Control-Allow-Credentials: true |
| `test_cors_methods_allowed` | Check allowed methods | Includes GET, POST, etc. |

**Example Test:**
```python
def test_cors_preflight_request(client):
    """OPTIONS request should return CORS headers."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
```

### 8.2 Application Lifecycle Testing

**File:** `backend/tests/integration/test_app_lifecycle.py`

#### Test Cases for App Lifecycle

| Test Name | Scenario | Expected Outcome |
|-----------|----------|------------------|
| `test_startup_event_executes` | Start app | Startup message printed |
| `test_shutdown_event_executes` | Stop app | Shutdown message printed |
| `test_app_configuration` | Check app metadata | Title, version, description correct |
| `test_openapi_endpoints_available` | Check docs | /docs, /redoc, /openapi.json exist |

**Example Test:**
```python
def test_app_configuration(test_app):
    """Application should have correct metadata configuration."""
    assert test_app.title == "Test FastAPI App"
    assert test_app.version == "0.0.1-test"
    assert "hexagonal architecture" in test_app.description


def test_openapi_endpoints_available(client):
    """OpenAPI documentation endpoints should be available."""
    docs = client.get("/docs")
    assert docs.status_code == 200

    redoc = client.get("/redoc")
    assert redoc.status_code == 200

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
```

---

## 9. Testing Best Practices and Patterns

### 9.1 Fixture Design Patterns

**Pattern 1: Fixture Composition**
```python
@pytest.fixture
def health_check_service_with_custom_settings():
    """Compose multiple fixtures for complex scenarios."""
    custom_settings = Settings(app_version="2.0.0", environment="staging")
    return HealthService(custom_settings)
```

**Pattern 2: Parametrized Fixtures**
```python
@pytest.fixture(params=[
    HealthStatus.HEALTHY,
    HealthStatus.UNHEALTHY,
    HealthStatus.DEGRADED
])
def health_status(request):
    """Parametrized fixture for testing all status values."""
    return request.param
```

**Pattern 3: Autouse Fixtures**
```python
@pytest.fixture(autouse=True)
def reset_settings_cache():
    """Automatically clear settings cache before each test."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
```

### 9.2 Mock Patterns

**Pattern 1: Mock DateTime for Deterministic Tests**
```python
from unittest.mock import patch

def test_with_fixed_time(fixed_datetime):
    """Use fixed time for deterministic testing."""
    with patch('app.application.services.datetime') as mock_dt:
        mock_dt.utcnow.return_value = fixed_datetime
        # Test code here
```

**Pattern 2: Mock Dependencies in Routers**
```python
def test_router_with_mock_service(client, mock_health_service):
    """Test router independently of service implementation."""
    from app.infrastructure.web.routes.monitoring import get_health_service

    mock_health_service.check_health.return_value = HealthCheck(...)

    client.app.dependency_overrides[get_health_service] = lambda: mock_health_service

    response = client.get("/health")

    assert response.status_code == 200
    mock_health_service.check_health.assert_called_once()
```

### 9.3 Assertion Patterns

**Pattern 1: Comprehensive Assertions**
```python
def test_comprehensive_response(client):
    """Test multiple aspects of response."""
    response = client.get("/health")

    # Status code
    assert response.status_code == 200

    # Content type
    assert response.headers["content-type"] == "application/json"

    # Response structure
    data = response.json()
    assert set(data.keys()) == {"status", "timestamp", "version", "environment"}

    # Value assertions
    assert data["status"] == "healthy"
    assert data["version"] != ""
```

**Pattern 2: Exception Assertions**
```python
def test_exception_with_message(client):
    """Test exception is raised with expected message."""
    with pytest.raises(ValueError, match="Version cannot be empty"):
        HealthCheck(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow(),
            version="",
            environment="test"
        )
```

### 9.4 Parametrized Testing

**Pattern 1: Multiple Input Scenarios**
```python
@pytest.mark.parametrize("status,expected", [
    (HealthStatus.HEALTHY, "healthy"),
    (HealthStatus.UNHEALTHY, "unhealthy"),
    (HealthStatus.DEGRADED, "degraded")
])
def test_status_values(status, expected):
    """Test all HealthStatus enum values."""
    assert status.value == expected
```

**Pattern 2: Edge Cases**
```python
@pytest.mark.parametrize("invalid_version", ["", " ", None])
def test_invalid_versions(invalid_version):
    """Test various invalid version inputs."""
    with pytest.raises((ValueError, TypeError)):
        HealthCheck(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow(),
            version=invalid_version,
            environment="test"
        )
```

### 9.5 Test Organization

**Naming Convention:**
- `test_<component>_<scenario>_<expected_outcome>`
- Examples:
  - `test_health_endpoint_returns_200_when_service_healthy`
  - `test_ping_service_raises_error_when_invalid_message`

**Test Structure (AAA Pattern):**
```python
def test_example():
    # Arrange - Set up test data and dependencies
    service = HealthService(test_settings)

    # Act - Execute the behavior being tested
    result = service.check_health()

    # Assert - Verify the outcome
    assert result.status == HealthStatus.HEALTHY
```

---

## 10. Coverage Goals and Metrics

### 10.1 Coverage Targets

| Layer | Coverage Target | Rationale |
|-------|----------------|-----------|
| **Domain Layer** | 100% | Pure business logic, critical to test |
| **Application Layer** | 100% | Use cases, core functionality |
| **Infrastructure - DTOs** | 95% | Pydantic validation, schema |
| **Infrastructure - Middleware** | 90% | Exception handlers, middleware |
| **Infrastructure - Routes** | 95% | API endpoints, request/response |
| **Configuration** | 90% | Settings, dependency injection |
| **Overall** | 95%+ | Achievable for this simple boilerplate |

### 10.2 Running Coverage

**Generate Coverage Report:**
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

**View HTML Report:**
```bash
open htmlcov/index.html
```

**Coverage Configuration (pytest.ini):**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=app
    --cov-branch
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=95
```

### 10.3 Uncovered Areas (Acceptable)

**Areas that may not need 100% coverage:**
- FastAPI framework internals (e.g., Depends() resolution)
- Pydantic internal validation logic
- Startup/shutdown event logging (integration test coverage sufficient)
- Type hints and docstrings

---

## 11. Test Execution Strategy

### 11.1 Running Tests

**Run All Tests:**
```bash
cd backend
pytest
```

**Run Specific Test File:**
```bash
pytest tests/unit/test_domain_models.py
```

**Run Specific Test:**
```bash
pytest tests/unit/test_domain_models.py::test_health_check_creation_with_valid_data
```

**Run by Category:**
```bash
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/api/           # API tests only
```

**Run with Verbose Output:**
```bash
pytest -v
```

**Run with Output Capture Disabled:**
```bash
pytest -s  # See print statements
```

### 11.2 Test Markers (Optional Enhancement)

**pytest.ini:**
```ini
[tool:pytest]
markers =
    unit: Unit tests (isolated, fast)
    integration: Integration tests (dependencies, slower)
    api: API endpoint tests (full stack)
    slow: Tests that take significant time
```

**Usage:**
```python
@pytest.mark.unit
def test_domain_model():
    pass

@pytest.mark.integration
def test_exception_handler():
    pass
```

**Run by Marker:**
```bash
pytest -m unit           # Run only unit tests
pytest -m "not slow"     # Skip slow tests
```

### 11.3 Continuous Integration

**GitHub Actions Example (.github/workflows/test.yml):**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
```

---

## 12. Testing Anti-Patterns to Avoid

### 12.1 Common Mistakes

**DON'T: Test Implementation Details**
```python
# BAD - Testing internal implementation
def test_health_service_internal_variable():
    service = HealthService(settings)
    assert hasattr(service, '_settings')  # Don't test privates
```

**DO: Test Behavior**
```python
# GOOD - Testing observable behavior
def test_health_service_returns_version_from_settings():
    service = HealthService(settings)
    result = service.check_health()
    assert result.version == settings.app_version
```

**DON'T: Share State Between Tests**
```python
# BAD - Shared state causes flaky tests
shared_service = HealthService(Settings())

def test_one():
    shared_service.check_health()  # Modifies shared state

def test_two():
    shared_service.check_health()  # Depends on test_one
```

**DO: Use Fresh Fixtures**
```python
# GOOD - Each test gets fresh instance
@pytest.fixture
def health_service():
    return HealthService(Settings())

def test_one(health_service):
    health_service.check_health()

def test_two(health_service):
    health_service.check_health()
```

**DON'T: Use Sleep for Timing**
```python
# BAD - Flaky and slow
def test_timestamp():
    import time
    before = datetime.utcnow()
    time.sleep(1)
    service = HealthService(settings)
    result = service.check_health()
    assert result.timestamp > before
```

**DO: Mock Time**
```python
# GOOD - Deterministic and fast
def test_timestamp(fixed_datetime):
    with patch('app.application.services.datetime') as mock_dt:
        mock_dt.utcnow.return_value = fixed_datetime
        service = HealthService(settings)
        result = service.check_health()
        assert result.timestamp == fixed_datetime
```

### 12.2 Over-Testing

**DON'T: Test Framework Behavior**
```python
# BAD - Testing FastAPI/Pydantic, not our code
def test_pydantic_validates_types():
    # Don't test Pydantic's validation - it's already tested
    pass
```

**DO: Test Your Business Logic**
```python
# GOOD - Testing our domain invariants
def test_health_check_enforces_non_empty_version():
    with pytest.raises(ValueError):
        HealthCheck(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow(),
            version="",
            environment="test"
        )
```

---

## 13. Test Summary and Statistics

### 13.1 Test Count by Category

| Category | Files | Test Cases | Lines of Code (est.) |
|----------|-------|------------|----------------------|
| **Unit Tests** | | | |
| - Domain Models | 1 | 23 | ~250 |
| - Services | 1 | 15 | ~180 |
| - Config | 1 | 17 | ~170 |
| **Integration Tests** | | | |
| - Exception Handlers | 1 | 14 | ~200 |
| - DTOs | 1 | 13 | ~150 |
| **API Tests** | | | |
| - Health Endpoint | 1 | 12 | ~180 |
| - Ping Endpoint | 1 | 11 | ~170 |
| **Infrastructure** | | | |
| - conftest.py | 1 | 0 (fixtures) | ~150 |
| **TOTAL** | 8 | **105 tests** | ~1,450 LOC |

### 13.2 Estimated Test Implementation Time

| Task | Estimated Time |
|------|---------------|
| Set up conftest.py with fixtures | 1 hour |
| Unit tests - Domain models | 2 hours |
| Unit tests - Services | 1.5 hours |
| Unit tests - Config | 1 hour |
| Integration tests - Exception handlers | 2 hours |
| Integration tests - DTOs | 1.5 hours |
| API tests - Health endpoint | 1.5 hours |
| API tests - Ping endpoint | 1.5 hours |
| **Total Implementation Time** | **12 hours** |

### 13.3 Test Execution Performance

**Expected Performance (estimated):**
- Unit tests: < 1 second (fast, no I/O)
- Integration tests: < 2 seconds (TestClient overhead)
- API tests: < 3 seconds (full stack)
- **Total suite: < 5 seconds**

---

## 14. Critical Testing Notes

### 14.1 Important Considerations

1. **Timezone Consistency**
   - All timestamps use `datetime.utcnow()` (UTC)
   - Tests should use `fixed_datetime` fixture or mock time
   - Avoid timezone-dependent assertions

2. **Settings Cache Management**
   - `get_settings()` is cached with `@lru_cache()`
   - Clear cache in tests: `get_settings.cache_clear()`
   - Use dependency override for test settings

3. **TestClient Behavior**
   - TestClient runs FastAPI synchronously
   - Automatically follows redirects
   - Supports session cookies
   - Does NOT start actual server

4. **Pydantic Validation**
   - DTOs validate on creation
   - Use `model_dump()` for dict output
   - Use `model_dump_json()` for JSON string
   - Validation errors are RequestValidationError

5. **FastAPI Dependency Injection**
   - Override dependencies with `app.dependency_overrides`
   - Clear overrides after test
   - Use `Depends()` in routes, not direct calls

### 14.2 Testing Checklist

Before considering tests complete, verify:

- [ ] All domain models have validation tests
- [ ] All services have unit tests with mocked dependencies
- [ ] All exception handlers have integration tests
- [ ] All endpoints have API tests (happy path + errors)
- [ ] Configuration loading is tested
- [ ] Edge cases are covered (empty strings, None, etc.)
- [ ] Error scenarios are tested
- [ ] Coverage is 95%+
- [ ] All tests are isolated (can run in any order)
- [ ] No hardcoded timestamps or sleeps
- [ ] Test names are descriptive
- [ ] Fixtures are reusable and well-documented

---

## 15. Future Test Enhancements

### 15.1 When Adding Database Layer

**Add:**
- Repository integration tests with test database
- Transaction rollback fixtures
- Database migration tests
- Connection pool tests

**Example:**
```python
@pytest.fixture(scope="function")
async def db_session():
    """Provide test database session with rollback."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
```

### 15.2 When Adding Authentication

**Add:**
- JWT token generation/validation tests
- Authorization tests for protected endpoints
- Session management tests
- Password hashing tests

**Example:**
```python
@pytest.fixture
def auth_headers(test_user):
    """Provide authentication headers."""
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}
```

### 15.3 When Adding External Services

**Add:**
- Mock external API responses
- Timeout and retry tests
- Circuit breaker tests
- Integration tests with test doubles

**Example:**
```python
@pytest.fixture
def mock_external_api(httpx_mock):
    """Mock external API responses."""
    httpx_mock.add_response(
        url="https://api.example.com/data",
        json={"status": "ok"}
    )
```

### 15.4 Performance Testing

**Add:**
- Load tests with locust or pytest-benchmark
- Response time assertions
- Concurrency tests
- Memory usage tests

**Example:**
```python
def test_health_endpoint_performance(benchmark, client):
    """Health endpoint should respond within 50ms."""
    result = benchmark(client.get, "/health")
    assert result.status_code == 200
```

---

## 16. Testing Resources and References

### 16.1 Documentation

- **pytest**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Pydantic Testing**: https://docs.pydantic.dev/latest/
- **httpx**: https://www.python-httpx.org/
- **unittest.mock**: https://docs.python.org/3/library/unittest.mock.html

### 16.2 Best Practices

- **Test Pyramid**: Focus on many unit tests, fewer integration/E2E
- **AAA Pattern**: Arrange, Act, Assert structure
- **FIRST Principles**: Fast, Isolated, Repeatable, Self-validating, Timely
- **DRY in Tests**: Use fixtures and parametrization, avoid duplication
- **Test Behavior**: Test what code does, not how it does it

### 16.3 Recommended Tools

- **pytest-cov**: Coverage reporting
- **pytest-asyncio**: Async test support
- **pytest-mock**: Easier mocking
- **pytest-xdist**: Parallel test execution
- **httpx**: Async HTTP client for testing

---

## 17. Conclusion

This test plan provides comprehensive coverage for the FastAPI backend boilerplate. The strategy follows industry best practices:

1. **Layered Testing**: Unit, integration, and API tests for each layer
2. **Isolation**: Tests don't share state or depend on each other
3. **Coverage**: 95%+ achievable for this simple boilerplate
4. **Maintainability**: Clear naming, DRY fixtures, well-organized
5. **Speed**: Entire suite runs in < 5 seconds
6. **Reliability**: No flaky tests, deterministic time handling

**Key Strengths:**
- Comprehensive test cases for all components
- Clear examples and patterns
- Reusable fixtures for efficiency
- Both happy paths and error scenarios
- Scalable approach for future features

**Implementation Recommendation:**
- Implement tests in order: conftest.py → unit → integration → API
- Run coverage after each category to ensure targets
- Use provided examples as templates
- Adapt patterns as needed for specific scenarios

The test suite will provide confidence in:
- Domain model invariants
- Service business logic
- API contract compliance
- Error handling consistency
- Configuration management

With 105 tests covering all layers, this test plan establishes a solid foundation for the boilerplate and demonstrates testing best practices for hexagonal architecture.

---

**Next Steps:**
1. Review this test plan for completeness
2. Implement conftest.py with shared fixtures
3. Implement unit tests (domain, services, config)
4. Implement integration tests (handlers, DTOs)
5. Implement API tests (endpoints)
6. Run coverage and verify 95%+ target
7. Document any edge cases discovered during implementation

