# FastAPI Backend Boilerplate - Implementation Plan

## Architecture Decision: Simplified Hexagonal Structure

**Recommendation**: Use a **lightweight hexagonal architecture** that:
- Establishes core patterns (domain, application, infrastructure layers)
- Avoids over-engineering for simple endpoints
- Provides clear expansion path for future features
- Demonstrates FastAPI best practices

**Rationale**:
- Pure hexagonal would be overkill for health/ping endpoints
- Complete flat structure would miss learning opportunities
- Hybrid approach teaches patterns while staying practical
- Easy to add repositories/use cases later when needed

---

## Recommended Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application factory
│   ├── config.py                  # Configuration management
│   │
│   ├── domain/                    # Domain layer (business logic)
│   │   ├── __init__.py
│   │   └── models.py              # Domain models (health status, etc.)
│   │
│   ├── application/               # Application layer (use cases - minimal for now)
│   │   ├── __init__.py
│   │   └── services.py            # Application services (health check logic)
│   │
│   └── infrastructure/            # Infrastructure layer (external concerns)
│       ├── __init__.py
│       ├── web/                   # Web layer (FastAPI specific)
│       │   ├── __init__.py
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   └── monitoring.py  # Health & ping endpoints
│       │   └── dto.py             # Pydantic DTOs for requests/responses
│       └── middleware/
│           ├── __init__.py
│           └── exception_handlers.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_health.py
│   └── test_ping.py
│
├── .env.example                   # Environment variables template
├── .gitignore
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
└── README.md
```

---

## File-by-File Implementation Guide

### 1. `backend/requirements.txt`

```txt
# Web Framework
fastapi==0.115.0
uvicorn[standard]==0.32.0

# Data Validation
pydantic==2.9.2
pydantic-settings==2.6.1

# Environment Management
python-dotenv==1.0.1
```

**Notes**:
- `fastapi==0.115.0`: Latest stable with all features
- `uvicorn[standard]`: Includes uvloop, httptools for performance
- `pydantic-settings`: Clean config management from env vars
- Pinned versions for reproducibility

### 2. `backend/requirements-dev.txt`

```txt
-r requirements.txt

# Testing
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
httpx==0.28.1  # Async client for testing FastAPI

# Code Quality
black==24.10.0
ruff==0.8.4
mypy==1.13.0

# Development
python-dotenv==1.0.1
```

**Notes**:
- `httpx`: Required for TestClient in async mode
- `pytest-asyncio`: Handle async test functions
- `ruff`: Fast linter replacing flake8/isort
- `mypy`: Type checking

### 3. `backend/app/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings.

    Loads from environment variables with APP_ prefix.
    Example: APP_ENVIRONMENT=production
    """

    # Application
    app_name: str = "FastAPI Backend Boilerplate"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance for dependency injection.

    Returns:
        Settings: Singleton settings instance
    """
    return Settings()
```

**Key Points**:
- **`pydantic_settings.BaseSettings`**: Type-safe config from env vars
- **`@lru_cache()`**: Singleton pattern for FastAPI dependency injection
- **Env prefix**: All vars use `APP_` prefix to avoid conflicts
- **CORS defaults**: Common development origins included
- **Type hints**: Full typing for IDE support

### 4. `backend/app/domain/models.py`

```python
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
```

**Key Points**:
- **`@dataclass(frozen=True)`**: Immutable domain objects
- **`__post_init__`**: Domain validation (hexagonal pattern)
- **`Enum` for status**: Type-safe status values
- **Framework-agnostic**: No FastAPI/Pydantic imports
- **Clear invariants**: Business rules enforced at creation

### 5. `backend/app/application/services.py`

```python
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
```

**Key Points**:
- **Constructor injection**: Dependencies passed in constructor
- **Single responsibility**: Each service has one purpose
- **Domain object creation**: Services create domain objects
- **Testable**: Easy to mock dependencies
- **Expansion path**: Comments indicate where to add checks later

### 6. `backend/app/infrastructure/web/dto.py`

```python
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
```

**Key Points**:
- **Pydantic models**: Web layer validation/serialization
- **`Field()` descriptions**: Auto-generated OpenAPI docs
- **Example schemas**: Better API documentation
- **Separation**: DTOs separate from domain models
- **Validation**: Automatic by Pydantic on responses

### 7. `backend/app/infrastructure/web/routes/monitoring.py`

```python
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
```

**Key Points**:
- **Thin controllers**: Router only handles HTTP concerns
- **Dependency injection**: Uses FastAPI's `Depends()`
- **Explicit response models**: Type-safe responses
- **OpenAPI metadata**: Rich documentation via decorators
- **Service delegation**: Business logic in services, not routers
- **Async handlers**: Following FastAPI best practices

### 8. `backend/app/infrastructure/middleware/exception_handlers.py`

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent format.

    Args:
        request: FastAPI request
        exc: HTTP exception

    Returns:
        JSONResponse: Formatted error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with detailed format.

    Args:
        request: FastAPI request
        exc: Validation error

    Returns:
        JSONResponse: Formatted validation error response
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Args:
        request: FastAPI request
        exc: Unexpected exception

    Returns:
        JSONResponse: Generic error response
    """
    # In production, log the full exception
    # In development, you may want to include more details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_error",
                "message": "An unexpected error occurred"
            }
        }
    )
```

**Key Points**:
- **Consistent error format**: All errors follow same structure
- **Separation of concerns**: Different handlers for different error types
- **Security**: Generic messages for internal errors
- **Validation details**: Helpful Pydantic validation errors
- **Production ready**: Safe for production use

### 9. `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.infrastructure.web.routes import monitoring
from app.infrastructure.middleware.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)


def create_application() -> FastAPI:
    """Application factory pattern.

    Creates and configures the FastAPI application instance.

    Returns:
        FastAPI: Configured application instance
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="FastAPI Backend Boilerplate with hexagonal architecture",
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Exception Handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Include Routers
    app.include_router(monitoring.router)

    return app


# Application instance
app = create_application()


@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    settings = get_settings()
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    print("Shutting down application...")
```

**Key Points**:
- **Factory pattern**: `create_application()` for testing flexibility
- **Configuration centralized**: All settings from Settings class
- **CORS configured**: Ready for frontend integration
- **Exception handlers registered**: Consistent error responses
- **Lifecycle events**: Startup/shutdown hooks for future needs
- **OpenAPI enabled**: Auto-generated documentation at `/docs`

### 10. `backend/.env.example`

```bash
# Application Configuration
APP_APP_NAME=FastAPI Backend Boilerplate
APP_APP_VERSION=0.1.0
APP_ENVIRONMENT=development
APP_DEBUG=true

# Server Configuration
APP_HOST=0.0.0.0
APP_PORT=8000

# CORS Configuration (comma-separated)
APP_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
APP_CORS_ALLOW_CREDENTIALS=true
```

**Notes**:
- Prefix all vars with `APP_` to match settings
- Document each section clearly
- Provide sensible defaults for development

### 11. `backend/.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# MyPy
.mypy_cache/
.dmypy.json
dmypy.json
```

### 12. `backend/tests/conftest.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import create_application
from app.config import Settings, get_settings


def get_test_settings() -> Settings:
    """Override settings for testing."""
    return Settings(
        app_name="Test App",
        app_version="0.0.1",
        environment="testing",
        debug=True
    )


@pytest.fixture(scope="function")
def test_app():
    """Create a test FastAPI application."""
    app = create_application()
    app.dependency_overrides[get_settings] = get_test_settings
    return app


@pytest.fixture(scope="function")
def client(test_app):
    """Create a test client."""
    return TestClient(test_app)
```

**Key Points**:
- **Dependency override**: Test settings separate from real settings
- **Fresh app per test**: `scope="function"` for isolation
- **TestClient**: Synchronous client for easy testing

### 13. `backend/tests/test_health.py`

```python
import pytest
from fastapi import status


def test_health_endpoint_returns_200(client):
    """Test health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK


def test_health_endpoint_returns_correct_structure(client):
    """Test health endpoint returns expected JSON structure."""
    response = client.get("/health")
    data = response.json()

    assert "status" in data
    assert "timestamp" in data
    assert "version" in data
    assert "environment" in data


def test_health_endpoint_status_is_healthy(client):
    """Test health endpoint returns healthy status."""
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "healthy"


def test_health_endpoint_contains_version(client):
    """Test health endpoint includes version information."""
    response = client.get("/health")
    data = response.json()

    assert data["version"] == "0.0.1"  # From test settings


def test_health_endpoint_contains_environment(client):
    """Test health endpoint includes environment information."""
    response = client.get("/health")
    data = response.json()

    assert data["environment"] == "testing"  # From test settings
```

### 14. `backend/tests/test_ping.py`

```python
import pytest
from fastapi import status


def test_ping_endpoint_returns_200(client):
    """Test ping endpoint returns 200 OK."""
    response = client.get("/ping")
    assert response.status_code == status.HTTP_200_OK


def test_ping_endpoint_returns_correct_structure(client):
    """Test ping endpoint returns expected JSON structure."""
    response = client.get("/ping")
    data = response.json()

    assert "message" in data
    assert "timestamp" in data


def test_ping_endpoint_returns_pong(client):
    """Test ping endpoint returns 'pong' message."""
    response = client.get("/ping")
    data = response.json()

    assert data["message"] == "pong"


def test_ping_endpoint_timestamp_is_recent(client):
    """Test ping endpoint returns a recent timestamp."""
    from datetime import datetime, timedelta

    response = client.get("/ping")
    data = response.json()

    timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    now = datetime.utcnow()

    # Timestamp should be within last 5 seconds
    assert (now - timestamp) < timedelta(seconds=5)
```

### 15. `backend/README.md`

```markdown
# FastAPI Backend Boilerplate

A production-ready FastAPI backend boilerplate following hexagonal architecture principles.

## Features

- FastAPI framework with async support
- Hexagonal architecture (ports and adapters)
- Type-safe configuration with Pydantic Settings
- Comprehensive test suite with pytest
- Auto-generated OpenAPI documentation
- CORS middleware configured
- Consistent error handling
- Health check and ping endpoints

## Project Structure

```
backend/
├── app/
│   ├── domain/              # Domain layer (business logic)
│   ├── application/         # Application layer (use cases)
│   └── infrastructure/      # Infrastructure layer (external concerns)
│       └── web/            # Web layer (FastAPI routers, DTOs)
└── tests/                  # Test suite
```

## Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Running the Application

Development server with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Endpoints

### Health Check
```
GET /health
```

Returns application health status, version, and environment.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "0.1.0",
  "environment": "development"
}
```

### Ping
```
GET /ping
```

Simple connectivity test endpoint.

**Response:**
```json
{
  "message": "pong",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Architecture

This boilerplate follows hexagonal architecture principles:

- **Domain Layer**: Business logic and domain models (framework-agnostic)
- **Application Layer**: Use cases and application services
- **Infrastructure Layer**: External concerns (database, web, etc.)
- **Web Layer**: FastAPI routers, DTOs, and HTTP concerns

### Adding New Features

1. Define domain models in `app/domain/models.py`
2. Create application services in `app/application/services.py`
3. Implement infrastructure adapters (repositories, external APIs)
4. Create DTOs in `app/infrastructure/web/dto.py`
5. Add routers in `app/infrastructure/web/routes/`
6. Write tests in `tests/`

## Development

### Code Quality

Format code:
```bash
black app/ tests/
```

Lint code:
```bash
ruff check app/ tests/
```

Type checking:
```bash
mypy app/
```

## Configuration

Configuration is managed through environment variables with `APP_` prefix:

- `APP_APP_NAME`: Application name
- `APP_APP_VERSION`: Application version
- `APP_ENVIRONMENT`: Runtime environment (development/production)
- `APP_DEBUG`: Enable debug mode (true/false)
- `APP_HOST`: Server host
- `APP_PORT`: Server port
- `APP_CORS_ORIGINS`: Allowed CORS origins (comma-separated)

See `.env.example` for complete configuration options.
```

---

## Implementation Checklist

### Phase 1: Project Setup
- [ ] Create `backend/` directory structure
- [ ] Create all `__init__.py` files for Python packages
- [ ] Create `requirements.txt` with dependencies
- [ ] Create `requirements-dev.txt` with dev dependencies
- [ ] Create `.env.example` with configuration template
- [ ] Create `.gitignore` for Python/IDE files

### Phase 2: Configuration Layer
- [ ] Implement `app/config.py` with Pydantic Settings
- [ ] Implement cached `get_settings()` function

### Phase 3: Domain Layer
- [ ] Implement `app/domain/models.py`:
  - [ ] `HealthStatus` enum
  - [ ] `HealthCheck` dataclass with validation
  - [ ] `PingResponse` dataclass with validation

### Phase 4: Application Layer
- [ ] Implement `app/application/services.py`:
  - [ ] `HealthService` class with `check_health()` method
  - [ ] `PingService` class with `ping()` method

### Phase 5: Infrastructure - DTOs
- [ ] Implement `app/infrastructure/web/dto.py`:
  - [ ] `HealthCheckResponse` Pydantic model
  - [ ] `PingResponseDTO` Pydantic model

### Phase 6: Infrastructure - Middleware
- [ ] Implement `app/infrastructure/middleware/exception_handlers.py`:
  - [ ] `http_exception_handler()`
  - [ ] `validation_exception_handler()`
  - [ ] `generic_exception_handler()`

### Phase 7: Infrastructure - Routes
- [ ] Implement `app/infrastructure/web/routes/monitoring.py`:
  - [ ] Create APIRouter
  - [ ] Implement dependency injection functions
  - [ ] Implement `/health` endpoint
  - [ ] Implement `/ping` endpoint

### Phase 8: Application Factory
- [ ] Implement `app/main.py`:
  - [ ] `create_application()` factory function
  - [ ] Configure CORS middleware
  - [ ] Register exception handlers
  - [ ] Include routers
  - [ ] Add startup/shutdown events

### Phase 9: Testing
- [ ] Implement `tests/conftest.py` with fixtures
- [ ] Implement `tests/test_health.py` with all health endpoint tests
- [ ] Implement `tests/test_ping.py` with all ping endpoint tests
- [ ] Run test suite and verify all pass

### Phase 10: Documentation
- [ ] Create comprehensive `README.md`
- [ ] Verify all inline code comments are clear
- [ ] Test OpenAPI documentation generation

---

## Critical Implementation Notes

### 1. Python Version Requirement
- **Minimum**: Python 3.11
- **Reason**: Uses modern type hints (`list[str]` instead of `List[str]`)
- **Check**: Run `python --version` before starting

### 2. Dependency Installation Order
```bash
# ALWAYS create virtual environment first
python -m venv venv
source venv/bin/activate

# Install production dependencies
pip install -r requirements.txt

# Install dev dependencies (includes production)
pip install -r requirements-dev.txt
```

### 3. Environment Configuration
- Copy `.env.example` to `.env` BEFORE running
- DO NOT commit `.env` file (in `.gitignore`)
- All environment variables use `APP_` prefix

### 4. Directory Creation
All `__init__.py` files are REQUIRED for Python to recognize directories as packages:
```bash
backend/app/__init__.py
backend/app/domain/__init__.py
backend/app/application/__init__.py
backend/app/infrastructure/__init__.py
backend/app/infrastructure/web/__init__.py
backend/app/infrastructure/web/routes/__init__.py
backend/app/infrastructure/middleware/__init__.py
backend/tests/__init__.py
```

### 5. Running the Application
**Development (with auto-reload):**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Testing Guidelines
- Run tests from `backend/` directory
- Use `pytest` not `python -m pytest` (simpler)
- All tests should pass before considering complete
- Coverage should be 100% for this simple boilerplate

### 7. Common Pitfalls to Avoid

**DO NOT:**
- ❌ Import Pydantic models in domain layer
- ❌ Import FastAPI in application layer
- ❌ Put business logic in routers
- ❌ Use mutable default arguments
- ❌ Forget `async` on endpoint handlers

**DO:**
- ✅ Keep domain layer framework-agnostic
- ✅ Use dependency injection for all services
- ✅ Validate in both domain and DTO layers
- ✅ Use `frozen=True` for domain dataclasses
- ✅ Add docstrings to all public methods

### 8. FastAPI-Specific Best Practices

**Dependency Injection:**
```python
# CORRECT: Using Depends()
@router.get("/health")
async def health_check(
    service: HealthService = Depends(get_health_service)
):
    ...

# WRONG: Creating service directly
@router.get("/health")
async def health_check():
    service = HealthService(get_settings())  # Don't do this
    ...
```

**Response Models:**
```python
# CORRECT: Explicit response_model
@router.get("/health", response_model=HealthCheckResponse)
async def health_check(...) -> HealthCheckResponse:
    ...

# ACCEPTABLE but less explicit
@router.get("/health")
async def health_check(...) -> HealthCheckResponse:
    ...
```

**Async Handlers:**
```python
# CORRECT: All handlers should be async
async def health_check(...):
    ...

# AVOID: Sync handlers (blocks event loop)
def health_check(...):
    ...
```

### 9. Type Checking
- Modern Python 3.11+ uses `list[str]` not `List[str]`
- No need to import `from typing import List, Dict, etc.`
- Use `from typing import` only for `Optional`, `Union`, `Callable`, etc.

### 10. CORS Configuration
- Development origins include both Vite (5173) and CRA (3000)
- Production should restrict `cors_origins` to actual frontend domain
- Update via environment variables, not code

---

## Expansion Patterns

When this boilerplate needs to grow, follow these patterns:

### Adding Database Support
1. Create repository port in `app/application/ports/repositories.py`
2. Implement MongoDB adapter in `app/infrastructure/persistence/mongodb/`
3. Update services to accept repository in constructor
4. Update dependency injection in routers

### Adding Authentication
1. Create domain models for User, Token in `app/domain/models.py`
2. Create auth service in `app/application/services.py`
3. Create JWT utilities in `app/infrastructure/security/`
4. Create auth router in `app/infrastructure/web/routes/auth.py`
5. Add dependencies for protected routes

### Adding Business Logic
1. Start with domain models (entities, value objects)
2. Define repository ports for data access
3. Implement use cases in application layer
4. Create infrastructure adapters
5. Add web layer (routers, DTOs, mappers)

---

## Testing Strategy

### Unit Tests
- Test domain models validate correctly
- Test services with mocked dependencies
- Test mappers convert correctly

### Integration Tests
- Test full endpoint flow with TestClient
- Test error handling scenarios
- Test CORS configuration
- Test OpenAPI schema generation

### Coverage Goals
- Aim for 100% coverage on this simple boilerplate
- Focus on behavior, not just coverage percentage
- Test both happy paths and error cases

---

## Production Considerations

### Before Deploying to Production:

1. **Environment Variables**
   - Set `APP_ENVIRONMENT=production`
   - Set `APP_DEBUG=false`
   - Configure real CORS origins
   - Use secrets manager for sensitive values

2. **Server Configuration**
   - Use multiple workers: `--workers 4`
   - Consider Gunicorn with Uvicorn workers
   - Set up reverse proxy (nginx)
   - Enable HTTPS/TLS

3. **Monitoring**
   - Add logging middleware
   - Set up error tracking (Sentry)
   - Monitor health endpoint
   - Set up uptime monitoring

4. **Security**
   - Review CORS configuration
   - Add rate limiting middleware
   - Enable security headers
   - Regular dependency updates

---

## Summary

This implementation plan provides:

✅ **Simplified hexagonal architecture** - Teaches patterns without over-engineering
✅ **Production-ready structure** - CORS, error handling, configuration
✅ **Type safety** - Full type hints, Pydantic validation
✅ **Testability** - Dependency injection, clear separation
✅ **Documentation** - OpenAPI auto-generation, comprehensive README
✅ **Scalability** - Clear patterns for adding features

The structure is intentionally simple for health/ping endpoints but establishes the foundation for complex features later.
