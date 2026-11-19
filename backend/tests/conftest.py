import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from dotenv import dotenv_values
from httpx import ASGITransport, AsyncClient

# TEST_DATABASE_URL may come from the shell or from the root .env file.
_ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"
if "TEST_DATABASE_URL" not in os.environ and _ROOT_ENV.exists():
    if value := dotenv_values(_ROOT_ENV).get("TEST_DATABASE_URL"):
        os.environ["TEST_DATABASE_URL"] = value

# Tests must never touch a developer's real database by accident:
# with TEST_DATABASE_URL they use it, otherwise an unreachable placeholder.
os.environ["ENVIRONMENT"] = "test"
# Never call the real Gemini API from tests (it is mocked where needed).
os.environ["GEMINI_API_KEY"] = ""
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+asyncpg://test:test@127.0.0.1:1/unused"
)

from app.main import create_app  # noqa: E402


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


requires_db = pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL not set (PostgreSQL required)",
)
