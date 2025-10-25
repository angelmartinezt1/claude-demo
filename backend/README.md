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
│   │   └── models.py        # Domain models (HealthCheck, PingResponse)
│   ├── application/         # Application layer (use cases)
│   │   └── services.py      # Application services
│   ├── infrastructure/      # Infrastructure layer (external concerns)
│   │   ├── web/            # Web layer (FastAPI routers, DTOs)
│   │   │   ├── dto.py      # Pydantic response DTOs
│   │   │   └── routes/
│   │   │       └── monitoring.py  # Health & ping endpoints
│   │   └── middleware/
│   │       └── exception_handlers.py  # Consistent error handling
│   ├── config.py           # Settings with pydantic-settings
│   └── main.py             # FastAPI application factory
└── tests/                  # Test suite
    ├── conftest.py         # Shared pytest fixtures
    └── api/
        ├── test_health_endpoint.py
        └── test_ping_endpoint.py
```

## Architecture

This boilerplate follows **hexagonal architecture** principles:

- **Domain Layer**: Business logic and domain models (framework-agnostic)
- **Application Layer**: Use cases and application services
- **Infrastructure Layer**: External concerns (database, web, etc.)
- **Web Layer**: FastAPI routers, DTOs, and HTTP concerns

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
cd backend
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Development server with auto-reload:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production server:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The application will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

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

## Testing

### Run all tests:
```bash
cd backend
pytest
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Run specific test file:
```bash
pytest tests/api/test_health_endpoint.py
```

View coverage report:
```bash
open htmlcov/index.html
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

## Adding New Features

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

## Production Considerations

### Before Deploying:

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

## License

MIT
