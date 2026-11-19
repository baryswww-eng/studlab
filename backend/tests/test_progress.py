"""Lesson progress, auto-enrollment, dashboard and password change."""

from collections.abc import AsyncIterator
from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select

from app.core.config import get_settings
from app.core.passwords import hash_password
from app.core.security import create_session_token
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models import Course, Role, User
from app.scripts.seed_demo import seed
from app.services.progress_service import _streak
from tests.conftest import requires_db

pytestmark = requires_db
PASSWORD = "secret123"  # noqa: S105 — test fixture value


@pytest.fixture(scope="module", autouse=True)
async def progress_db() -> AsyncIterator[dict[str, int]]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(insert(Role), [{"name": n} for n in ("student", "instructor", "admin")])
    await seed()
    async with SessionLocal() as s:
        role_id = await s.scalar(select(Role.id).where(Role.name == "student"))
        users = [
            User(
                email=f"p{i}@example.com",
                full_name=f"P{i}",
                role_id=role_id,
                password_hash=hash_password(PASSWORD),
            )
            for i in (1, 2, 3)
        ]
        s.add_all(users)
        await s.commit()
        ids = {f"u{i}": u.id for i, u in enumerate(users, 1)}
    yield ids
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def sign_in(client: AsyncClient, user_id: int) -> None:
    client.cookies.set("studlab_session", create_session_token(user_id, get_settings()))


async def lesson_ids(client: AsyncClient, slug: str) -> list[int]:
    course = (await client.get(f"/api/v1/courses/{slug}")).json()
    return [lesson["id"] for m in course["modules"] for lesson in m["lessons"]]


async def test_progress_requires_login(client: AsyncClient) -> None:
    ids = await lesson_ids(client, "python-basics")
    assert (await client.put(f"/api/v1/progress/lessons/{ids[0]}")).status_code == 401
    assert (await client.get("/api/v1/users/me/dashboard")).status_code == 401


async def test_complete_lesson_and_auto_enroll(
    client: AsyncClient, progress_db: dict[str, int]
) -> None:
    sign_in(client, progress_db["u1"])
    ids = await lesson_ids(client, "python-basics")

    empty = (await client.get("/api/v1/users/me/dashboard")).json()
    assert empty["courses"] == []
    assert empty["stats"]["lessons_completed"] == 0

    course_json = (await client.get("/api/v1/courses/python-basics")).json()
    first_minutes = course_json["modules"][0]["lessons"][0]["duration_minutes"]
    first = (await client.put(f"/api/v1/progress/lessons/{ids[0]}")).json()
    again = (await client.put(f"/api/v1/progress/lessons/{ids[0]}")).json()  # idempotent
    assert first == again
    assert first["completed_lesson_ids"] == [ids[0]]
    assert (first["completed"], first["total"], first["percent"]) == (1, 12, 8)

    progress = (await client.get("/api/v1/progress/courses/python-basics")).json()
    assert progress["completed_lesson_ids"] == [ids[0]]

    dash = (await client.get("/api/v1/users/me/dashboard")).json()
    assert [c["slug"] for c in dash["courses"]] == ["python-basics"]
    course = dash["courses"][0]
    assert course["next_lesson_id"] == ids[1]
    assert course["next_lesson_title"] == "Условия: if, elif, else"
    assert dash["stats"]["lessons_completed"] == 1
    assert dash["stats"]["minutes_learned"] == first_minutes  # lesson duration
    assert dash["stats"]["streak_days"] == 1
    assert dash["stats"]["courses_started"] == 1


async def test_uncomplete_lesson(client: AsyncClient, progress_db: dict[str, int]) -> None:
    sign_in(client, progress_db["u2"])
    ids = await lesson_ids(client, "sql-postgresql")
    await client.put(f"/api/v1/progress/lessons/{ids[0]}")
    await client.put(f"/api/v1/progress/lessons/{ids[1]}")
    result = (await client.delete(f"/api/v1/progress/lessons/{ids[0]}")).json()
    assert result["completed_lesson_ids"] == [ids[1]]


async def test_course_completed_counter(client: AsyncClient, progress_db: dict[str, int]) -> None:
    sign_in(client, progress_db["u3"])
    for lesson_id in await lesson_ids(client, "it-fundamentals"):
        await client.put(f"/api/v1/progress/lessons/{lesson_id}")
    dash = (await client.get("/api/v1/users/me/dashboard")).json()
    assert dash["stats"]["courses_completed"] == 1
    assert dash["courses"][0]["percent"] == 100
    assert dash["courses"][0]["next_lesson_id"] is None


async def test_progress_is_private(client: AsyncClient, progress_db: dict[str, int]) -> None:
    sign_in(client, progress_db["u2"])
    dash = (await client.get("/api/v1/users/me/dashboard")).json()
    assert "python-basics" not in [c["slug"] for c in dash["courses"]]  # u1's course


async def test_unknown_or_draft_lesson_404(
    client: AsyncClient, progress_db: dict[str, int]
) -> None:
    sign_in(client, progress_db["u1"])
    assert (await client.put("/api/v1/progress/lessons/999999")).status_code == 404
    async with SessionLocal() as s:
        course = await s.scalar(select(Course).where(Course.slug == "react-nextjs"))
        assert course is not None
        course.status = "draft"  # type: ignore[assignment]
        await s.commit()
    ids_resp = await client.get("/api/v1/progress/courses/react-nextjs")
    assert ids_resp.status_code == 404


async def test_change_password(client: AsyncClient, progress_db: dict[str, int]) -> None:
    sign_in(client, progress_db["u3"])
    wrong = await client.post(
        "/api/v1/users/me/password",
        json={"current_password": "nope12345", "new_password": "newpass123"},
    )
    assert wrong.status_code == 400
    weak = await client.post(
        "/api/v1/users/me/password",
        json={"current_password": PASSWORD, "new_password": "short"},
    )
    assert weak.status_code == 422
    ok = await client.post(
        "/api/v1/users/me/password",
        json={"current_password": PASSWORD, "new_password": "newpass123"},
    )
    assert ok.status_code == 204
    login_old = await client.post(
        "/api/v1/auth/login", json={"email": "p3@example.com", "password": PASSWORD}
    )
    login_new = await client.post(
        "/api/v1/auth/login", json={"email": "p3@example.com", "password": "newpass123"}
    )
    assert (login_old.status_code, login_new.status_code) == (401, 200)


def test_streak() -> None:
    today = date(2026, 11, 19)
    d = lambda n: date(2026, 11, 19 - n)  # noqa: E731
    assert _streak(set(), today) == 0
    assert _streak({d(0)}, today) == 1
    assert _streak({d(0), d(1), d(2)}, today) == 3
    assert _streak({d(1), d(2)}, today) == 2  # not studied yet today: streak still alive
    assert _streak({d(0), d(2)}, today) == 1
    assert _streak({d(2), d(3)}, today) == 0
