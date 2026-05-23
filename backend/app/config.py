"""
Central configuration for api-pilot backend.

Settings are loaded from environment variables (and optionally a .env file).
All settings have sensible defaults so the app starts without a .env present.

Usage:
    from app.config import get_settings
    settings = get_settings()
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "api-pilot"
    app_env: str = "development"  # development | staging | production
    log_level: str = "INFO"
    api_prefix: str = "/api"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://api_pilot:api_pilot_dev@localhost:5432/api_pilot"
    db_echo: bool = False       # SQL echo logging — set True in dev to see queries
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_pre_ping: bool = True


def get_settings() -> Settings:
    return Settings()
