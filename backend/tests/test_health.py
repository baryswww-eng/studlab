from httpx import AsyncClient
from sqlalchemy.exc import OperationalError

from app.database.session import get_session
from tests.conftest import requires_db


async def test_health_ok(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "STUD LAB API"
    assert body["environment"] == "test"


async def test_db_health_returns_503_without_leaking_details(client: AsyncClient) -> None:
    class BrokenSession:
        async def execute(self, *_: object) -> None:
            raise OperationalError("SELECT 1", {}, Exception("password=secret host=db"))

    async def broken_session():  # type: ignore[no-untyped-def]
        yield BrokenSession()

    app = client._transport.app  # type: ignore[attr-defined]
    app.dependency_overrides[get_session] = broken_session

    response = await client.get("/api/v1/health/db")
    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "database": "postgresql",
        "latency_ms": None,
    }
    assert "secret" not in response.text


@requires_db
async def test_db_health_with_real_postgres(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/db")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["latency_ms"] >= 0


async def test_unknown_route_uses_error_envelope(client: AsyncClient) -> None:
    response = await client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


async def test_cors_allows_only_configured_origin(client: AsyncClient) -> None:
    allowed = await client.options(
        "/api/v1/health",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"

    denied = await client.options(
        "/api/v1/health",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"},
    )
    assert "access-control-allow-origin" not in denied.headers
