import pytest
from pydantic import ValidationError

from app.core.config import Settings


def make(**kwargs: object) -> Settings:
    # _env_file=None: ignore any local .env so tests are deterministic.
    return Settings(_env_file=None, **kwargs)  # type: ignore[call-arg]


def test_cors_origins_from_comma_separated_string() -> None:
    s = make(cors_origins="http://localhost:3000, https://studlab.kz")
    assert s.cors_origins == ["http://localhost:3000", "https://studlab.kz"]


@pytest.mark.parametrize("url", ["postgres://u:p@h/db", "postgresql://u:p@h/db"])
def test_database_url_is_normalized_to_async_driver(url: str) -> None:
    assert make(database_url=url).database_url == "postgresql+asyncpg://u:p@h/db"


def test_production_rejects_default_secret() -> None:
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        make(environment="production")


def test_production_rejects_wildcard_cors() -> None:
    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        make(environment="production", secret_key="x" * 40, cors_origins="*")


def test_ai_unavailable_without_key() -> None:
    assert make(ai_enabled=True, gemini_api_key=None).ai_available is False
    assert make(ai_enabled=True, gemini_api_key="test-key").ai_available is True
    assert make(ai_enabled=False, gemini_api_key="test-key").ai_available is False
