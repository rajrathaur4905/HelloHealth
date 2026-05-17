"""
Application Configuration.

Loads settings from environment variables and .env file using
pydantic-settings. All configuration is centralized here — no
hardcoded values anywhere else in the codebase.

Usage:
    from app.config import settings
    print(settings.DATABASE_URL)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # ── Application ──────────────────────────────────────────
    APP_NAME: str = "HelloHealth"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/hellohealth"

    # ── Redis ────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6380/0"

    # ── Authentication ───────────────────────────────────────
    JWT_SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── AI Model ─────────────────────────────────────────────
    MODEL_NAME: str = "facebook/bart-large-mnli"
    MODEL_ENABLED: bool = True

    # ── CORS ─────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # ── Rate Limiting ────────────────────────────────────────
    RATE_LIMIT_SYMPTOMS: str = "30/minute"
    RATE_LIMIT_AUTH: str = "5/minute"

    # ── Logging ──────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"


# Singleton instance — import this everywhere
settings = Settings()
