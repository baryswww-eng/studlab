"""Application settings, loaded from environment variables / .env."""

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

INSECURE_DEFAULT_SECRET = "change-me-in-production"  # noqa: S105 — placeholder, rejected in prod


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "STUD LAB API"
    app_version: str = "0.1.0"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # --- Security ---
    secret_key: SecretStr = SecretStr(INSECURE_DEFAULT_SECRET)
    session_cookie_name: str = "studlab_session"
    session_expire_days: int = 7
    # Must be true in production (HTTPS). Forced on there by the validator below.
    cookie_secure: bool = False

    # Comma-separated list in env: CORS_ORIGINS=http://localhost:3000,https://studlab.kz
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    # --- Database ---
    database_url: str = "postgresql+asyncpg://studlab:studlab@localhost:5432/studlab"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False

    # --- Redis (optional) ---
    redis_url: str | None = None

    # --- AI tutor: Google Gemini (server-side only, the key never reaches the browser) ---
    ai_enabled: bool = True
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.1-flash-lite"
    # Tried in order when the main model is over quota / unavailable.
    gemini_fallback_models: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["gemini-flash-lite-latest", "gemini-3.5-flash-lite"]
    )
    ai_timeout_seconds: float = 45
    # Request limits (per rolling hour / per day).
    ai_user_hourly_limit: int = 30
    ai_user_daily_limit: int = 100
    ai_anon_hourly_limit: int = 10

    @field_validator("cors_origins", "gemini_fallback_models", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [o.strip() for o in value.split(",") if o.strip()]
        return value

    @field_validator("database_url")
    @classmethod
    def _force_async_driver(cls, value: str) -> str:
        # Accept plain postgres:// URLs (e.g. from hosting providers).
        for prefix in ("postgres://", "postgresql://"):
            if value.startswith(prefix):
                return "postgresql+asyncpg://" + value[len(prefix) :]
        return value

    @model_validator(mode="after")
    def _check_production(self) -> "Settings":
        if self.environment == "production":
            secret = self.secret_key.get_secret_value()
            if secret == INSECURE_DEFAULT_SECRET or len(secret) < 32:
                raise ValueError(
                    "SECRET_KEY must be set to a random value of 32+ chars in production"
                )
            if "*" in self.cors_origins:
                raise ValueError("CORS_ORIGINS must list explicit domains in production")
            self.cookie_secure = True
        return self

    @property
    def ai_available(self) -> bool:
        """AI features are usable only when enabled AND a key is configured."""
        return self.ai_enabled and bool(
            self.gemini_api_key and self.gemini_api_key.get_secret_value()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
