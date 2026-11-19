from collections.abc import AsyncIterator
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select

from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models import Course, CourseLevel, CourseStatus, CourseTranslation, Role, User
from app.scripts.seed_demo import seed
from tests.conftest import requires_db

pytestmark = requires_db


@pytest.fixture(scope="module", autouse=True)
async def catalog_db() -> AsyncIterator[None]:
    """Fresh schema in the TEST database, demo catalog + one draft course."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            insert(Role), [{"name": "student"}, {"name": "instructor"}, {"name": "admin"}]
        )
    await seed()
    async with SessionLocal() as s:
        instructor = await s.scalar(select(User).limit(1))
        assert instructor is not None
        s.add(
            Course(
                slug="secret-draft",
                instructor_id=instructor.id,
                level=CourseLevel.BEGINNER,
                status=CourseStatus.DRAFT,
                price=Decimal("0"),
                translations=[
                    CourseTranslation(locale="kk", title="Жоба", short_description="draft")
                ],
            )
        )
        await s.commit()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def test_list_returns_only_published(client: AsyncClient) -> None:
    body = (await client.get("/api/v1/courses", params={"page_size": 48})).json()
    slugs = {c["slug"] for c in body["items"]}
    assert body["total"] == 8
    assert "secret-draft" not in slugs
    assert all(c["is_demo"] for c in body["items"])


async def test_draft_course_detail_is_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/courses/secret-draft")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "course_not_found"


async def test_pagination(client: AsyncClient) -> None:
    body = (await client.get("/api/v1/courses", params={"page": 2, "page_size": 3})).json()
    assert (body["page"], body["pages"], len(body["items"])) == (2, 3, 3)


@pytest.mark.parametrize(
    ("params", "expected"),
    [
        ({"q": "postgres"}, {"sql-postgresql"}),
        ({"q": "100%"}, set()),  # LIKE wildcards are escaped
        ({"category": "python"}, {"python-basics", "python-oop"}),
        ({"level": "advanced"}, {"react-nextjs"}),
        ({"price": "paid"}, set()),  # every course is free
    ],
)
async def test_filters(client: AsyncClient, params: dict[str, str], expected: set[str]) -> None:
    body = (await client.get("/api/v1/courses", params={**params, "page_size": 48})).json()
    assert {c["slug"] for c in body["items"]} == expected


async def test_price_sort_and_free_flag(client: AsyncClient) -> None:
    items = (await client.get("/api/v1/courses", params={"sort": "price_desc"})).json()["items"]
    prices = [Decimal(c["price"]) for c in items]
    assert prices == sorted(prices, reverse=True)
    assert all(c["is_free"] == (Decimal(c["price"]) == 0) for c in items)


async def test_detail_is_localized(client: AsyncClient) -> None:
    kk = (await client.get("/api/v1/courses/python-basics", params={"locale": "kk"})).json()
    ru = (await client.get("/api/v1/courses/python-basics", params={"locale": "ru"})).json()
    assert kk["title"] == "Python негіздері"
    assert ru["title"] == "Основы Python"
    assert [m["title"] for m in ru["modules"]] == [
        "Теория",
        "Видеоуроки",
        "Тесты и практические задания",
    ]
    assert ru["modules"][0]["lessons"][0]["title"].startswith("Python: первая программа")
    assert ru["modules"][1]["lessons"][0]["title"] == "Что такое Python?"
    assert [lsn["type"] for lsn in ru["modules"][2]["lessons"]] == [
        "quiz",
        "assignment",
        "assignment",
    ]
    assert kk["lessons_count"] == 12  # 3 theory + 6 video + quiz + 2 tasks
    assert kk["duration_minutes"] == sum(
        lesson["duration_minutes"] for m in kk["modules"] for lesson in m["lessons"]
    )


async def test_lesson_is_public_with_youtube_video(client: AsyncClient) -> None:
    course = (await client.get("/api/v1/courses/python-basics")).json()
    first = course["modules"][1]["lessons"][0]  # first video lesson
    assert first["has_video"] is True
    assert course["modules"][0]["lessons"][0]["has_video"] is False  # theory article

    response = await client.get(f"/api/v1/lessons/{first['id']}")  # no session cookie
    assert response.status_code == 200
    lesson = response.json()
    assert lesson["title"] == "Что такое Python?"
    assert lesson["youtube_id"] == "34Rp6KVGIEM"
    assert lesson["video_author"]
    assert lesson["course"]["slug"] == "python-basics"
    assert lesson["prev_lesson_id"] == course["modules"][0]["lessons"][-1]["id"]
    assert lesson["next_lesson_id"] == course["modules"][1]["lessons"][1]["id"]


async def test_last_lesson_has_no_next(client: AsyncClient) -> None:
    course = (await client.get("/api/v1/courses/python-basics")).json()
    last = course["modules"][-1]["lessons"][-1]
    lesson = (await client.get(f"/api/v1/lessons/{last['id']}")).json()
    assert lesson["next_lesson_id"] is None
    assert lesson["youtube_id"] is None  # assignment lessons have no video


async def test_unknown_lesson_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/lessons/999999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "lesson_not_found"


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.youtube.com/watch?v=34Rp6KVGIEM", "34Rp6KVGIEM"),
        ("https://youtu.be/34Rp6KVGIEM", "34Rp6KVGIEM"),
        ("https://www.youtube.com/watch?v=34Rp6KVGIEM&t=10", "34Rp6KVGIEM"),
        ("https://evil.example/watch?v=34Rp6KVGIEM", None),
        ("javascript:alert(1)", None),
        ("https://www.youtube.com/watch?v=short", None),
        (None, None),
    ],
)
def test_youtube_id_parser(url: str | None, expected: str | None) -> None:
    from app.services.course_service import youtube_id

    assert youtube_id(url) == expected


async def test_invalid_query_rejected(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/courses", params={"level": "expert"})).status_code == 422
    assert (await client.get("/api/v1/courses", params={"locale": "en"})).status_code == 422
    assert (await client.get("/api/v1/courses", params={"page_size": 1000})).status_code == 422


async def test_categories_and_stats_are_real_counts(client: AsyncClient) -> None:
    cats = (await client.get("/api/v1/categories", params={"locale": "ru"})).json()
    assert sum(c["course_count"] for c in cats) == 8  # draft not counted
    stats = (await client.get("/api/v1/stats/public")).json()
    assert stats == {"published_courses": 8, "categories": 6, "lessons": 103}  # 48 + 55 videos
