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
