"""Email/password auth: Argon2 hashes, HttpOnly session cookie, brute-force limits."""

from collections.abc import AsyncIterator

import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select, update

from app.api.v1.endpoints import auth as auth_endpoint
from app.core.passwords import hash_password, verify_password
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models import Role, User
from tests.conftest import requires_db

pytestmark = requires_db

PASSWORD = "secret123"  # noqa: S105 — test fixture value


@pytest.fixture(scope="module", autouse=True)
async def auth_db() -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            insert(Role), [{"name": "student"}, {"name": "instructor"}, {"name": "admin"}]
        )
        role_id = (await conn.execute(select(Role.id).where(Role.name == "instructor"))).scalar()
        await conn.execute(
            insert(User).values(
                email="demo.teacher@studlab.local",
                full_name="Demo",
                role_id=role_id,
                is_demo=True,
                password_hash="!demo-account-no-login",  # noqa: S106 — unusable marker
            )
        )
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def reset_limiters() -> None:
    auth_endpoint.login_limiter.reset()
    auth_endpoint.register_limiter.reset()


async def register(client: AsyncClient, email: str, name: str = "Alice Smith"):  # type: ignore[no-untyped-def]
    return await client.post(
        "/api/v1/auth/register", json={"full_name": name, "email": email, "password": PASSWORD}
    )


def test_argon2_hashing() -> None:
    hashed = hash_password(PASSWORD)
    assert hashed.startswith("$argon2id$")
    assert PASSWORD not in hashed
    assert verify_password(PASSWORD, hashed)
    assert not verify_password("wrong-pass1", hashed)
    assert not verify_password(PASSWORD, "!demo-account-no-login")
    assert not verify_password(PASSWORD, None)


async def test_me_requires_session(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


async def test_register_creates_student_and_signs_in(client: AsyncClient) -> None:
    response = await register(client, "Alice@Example.com", name="  Alice   Smith ")
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["full_name"] == "Alice Smith"
    assert body["role"] == "student"
    cookie = response.headers["set-cookie"]
    assert "studlab_session=" in cookie and "HttpOnly" in cookie
    assert "samesite=lax" in cookie.lower()
    assert (await client.get("/api/v1/users/me")).json()["id"] == body["id"]

    async with SessionLocal() as s:
        stored = await s.scalar(select(User.password_hash).where(User.id == body["id"]))
    assert stored and stored.startswith("$argon2id$")


async def test_duplicate_email_rejected(client: AsyncClient) -> None:
    assert (await register(client, "dup@example.com")).status_code == 201
    response = await register(client, "DUP@example.com")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "email_taken"


@pytest.mark.parametrize(
    "payload",
    [
        {"full_name": "A", "email": "a@example.com", "password": PASSWORD},
        {"full_name": "Bob", "email": "not-an-email", "password": PASSWORD},
        {"full_name": "Bob", "email": "b@example.com", "password": "short1"},
        {"full_name": "Bob", "email": "b@example.com", "password": "onlyletters"},
        {"full_name": "Bob", "email": "b@example.com", "password": "12345678"},
        {"full_name": "Bob", "email": "b@example.com", "password": "a1" * 65},
    ],
)
async def test_register_validation(client: AsyncClient, payload: dict[str, str]) -> None:
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 422


async def test_login_success_and_logout(client: AsyncClient) -> None:
    await register(client, "bob@example.com", name="Bob")
    client.cookies.clear()
    response = await client.post(
        "/api/v1/auth/login", json={"email": "BOB@example.com", "password": PASSWORD}
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Bob"
    assert (await client.get("/api/v1/users/me")).status_code == 200

    assert (await client.post("/api/v1/auth/logout")).status_code == 204
    assert (await client.get("/api/v1/users/me")).status_code == 401


async def test_wrong_password_and_unknown_email_look_the_same(client: AsyncClient) -> None:
    await register(client, "carol@example.com")
    client.cookies.clear()
    wrong = await client.post(
        "/api/v1/auth/login", json={"email": "carol@example.com", "password": "wrong-pass1"}
    )
    unknown = await client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": PASSWORD}
    )
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()
    assert "set-cookie" not in wrong.headers


async def test_demo_account_cannot_log_in(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login", json={"email": "demo.teacher@studlab.local", "password": PASSWORD}
    )
    assert response.status_code == 401


async def test_disabled_user_cannot_log_in(client: AsyncClient) -> None:
    await register(client, "dave@example.com")
    async with SessionLocal() as s:
        await s.execute(
            update(User).where(User.email == "dave@example.com").values(is_active=False)
        )
        await s.commit()
    response = await client.post(
        "/api/v1/auth/login", json={"email": "dave@example.com", "password": PASSWORD}
    )
    assert response.status_code == 403
    # The session cookie from registration stops working too.
    assert (await client.get("/api/v1/users/me")).status_code == 401


async def test_login_brute_force_limited(client: AsyncClient) -> None:
    for _ in range(10):
        r = await client.post(
            "/api/v1/auth/login", json={"email": "victim@example.com", "password": "guess1234"}
        )
        assert r.status_code == 401
    blocked = await client.post(
        "/api/v1/auth/login", json={"email": "victim@example.com", "password": "guess1234"}
    )
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0


async def test_tampered_cookie_rejected(client: AsyncClient) -> None:
    client.cookies.set("studlab_session", "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.bad")
    assert (await client.get("/api/v1/users/me")).status_code == 401


async def test_update_profile(client: AsyncClient) -> None:
    await register(client, "erin@example.com")
    response = await client.patch("/api/v1/users/me", json={"full_name": "Erin Builder"})
    assert response.status_code == 200
    assert response.json()["full_name"] == "Erin Builder"
    assert (await client.patch("/api/v1/users/me", json={"full_name": "E"})).status_code == 422
