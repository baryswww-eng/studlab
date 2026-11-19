"""STUD AI: Gemini client parsing/fallback, limits, lesson context and persistence.
The Gemini HTTP API is replaced by httpx.MockTransport — no real calls."""

import asyncio
import json
from collections.abc import AsyncIterator, Callable

import httpx
import pytest
from httpx import AsyncClient
from sqlalchemy import func, insert, select

from app.ai.gemini import ChatTurn, GeminiClient
from app.api.v1.endpoints import ai as ai_endpoint
from app.core.config import get_settings
from app.core.security import create_session_token
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models import AIMessage, Lesson, Role, User
from app.scripts.seed_demo import seed
from tests.conftest import requires_db

Handler = Callable[[httpx.Request], httpx.Response]


def gemini_ok(text: str = "Ответ STUD AI") -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": "STOP"}],
            "usageMetadata": {"promptTokenCount": 12, "candidatesTokenCount": 34},
        },
    )


class Recorder:
    def __init__(self, *responses: httpx.Response):
        self.responses = list(responses)
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]

    def body(self, i: int = -1) -> dict:
        return json.loads(self.requests[i].content)


@pytest.fixture(autouse=True)
def reset_limiter() -> None:
    ai_endpoint.anon_limiter.reset()


def use_gemini(client: AsyncClient, recorder: Recorder) -> None:
    app = client._transport.app  # type: ignore[attr-defined]
    app.dependency_overrides[ai_endpoint.get_ai_client] = lambda: GeminiClient(
        "test-key", transport=httpx.MockTransport(recorder)
    )


async def test_status_reports_disabled_without_key(client: AsyncClient) -> None:
    body = (await client.get("/api/v1/ai/status")).json()
    assert body["enabled"] is False
    assert body["model"] is None


async def test_chat_503_when_not_configured(client: AsyncClient) -> None:
    response = await client.post("/api/v1/ai/chat", json={"message": "Привет"})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ai_not_configured"


async def test_anonymous_chat_and_request_shape(client: AsyncClient) -> None:
    rec = Recorder(gemini_ok("Переменная — это имя для значения."))
    use_gemini(client, rec)
    response = await client.post(
        "/api/v1/ai/chat",
        json={
            "message": "Что такое переменная?",
            "mode": "tutor",
            "history": [
                {"role": "model", "content": "orphan model turn is dropped"},
                {"role": "user", "content": "Привет"},
                {"role": "model", "content": "Здравствуйте!"},
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "Переменная — это имя для значения."
    assert body["conversation_id"] is None  # anonymous: not stored

    sent = rec.requests[0]
    assert sent.headers["x-goog-api-key"] == "test-key"
    assert "test-key" not in str(sent.url)  # key never in the URL
    assert str(sent.url).endswith(f"/models/{get_settings().gemini_model}:generateContent")
    payload = rec.body()
    system = payload["systemInstruction"]["parts"][0]["text"]
    assert "STUD AI" in system and "ЛЮБЫЕ" in system and "Объяснить тему" in system
    roles = [c["role"] for c in payload["contents"]]
    assert roles == ["user", "model", "user"]  # history must start with a user turn
    assert payload["contents"][-1]["parts"][0]["text"] == "Что такое переменная?"


@pytest.mark.parametrize(
    ("mode", "marker"),
    [("code", "Разбор кода"), ("quiz", "Тест по теме"), ("practice", "Практика")],
)
async def test_modes_change_system_prompt(client: AsyncClient, mode: str, marker: str) -> None:
    rec = Recorder(gemini_ok())
    use_gemini(client, rec)
    await client.post("/api/v1/ai/chat", json={"message": "print(1", "mode": mode})
    assert marker in rec.body()["systemInstruction"]["parts"][0]["text"]


async def test_fallback_model_on_quota(client: AsyncClient) -> None:
    rec = Recorder(httpx.Response(429, json={"error": {}}), gemini_ok("из запасной модели"))
    use_gemini(client, rec)
    body = (await client.post("/api/v1/ai/chat", json={"message": "Привет"})).json()
    assert body["reply"] == "из запасной модели"
    assert body["model"] == get_settings().gemini_fallback_models[0]
    assert len(rec.requests) == 2


async def test_all_models_failing_gives_503(client: AsyncClient) -> None:
    use_gemini(client, Recorder(httpx.Response(503)))
    response = await client.post("/api/v1/ai/chat", json={"message": "Привет"})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ai_unavailable"


async def test_bad_request_is_not_retried(client: AsyncClient) -> None:
    rec = Recorder(httpx.Response(400))
    use_gemini(client, rec)
    assert (await client.post("/api/v1/ai/chat", json={"message": "x"})).status_code == 503
    assert len(rec.requests) == 1


async def test_blocked_answer_gives_422(client: AsyncClient) -> None:
    use_gemini(
        client, Recorder(httpx.Response(200, json={"promptFeedback": {"blockReason": "SAFETY"}}))
    )
    response = await client.post("/api/v1/ai/chat", json={"message": "..."})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ai_blocked"


async def test_thought_parts_are_not_shown(client: AsyncClient) -> None:
    resp = httpx.Response(
        200,
        json={
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "скрытые рассуждения", "thought": True},
                            {"text": "Итог"},
                        ]
                    }
                }
            ]
        },
    )
    use_gemini(client, Recorder(resp))
    assert (await client.post("/api/v1/ai/chat", json={"message": "x"})).json()["reply"] == "Итог"


async def test_anonymous_rate_limit(client: AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ai_endpoint.anon_limiter, "limit", 2)
    use_gemini(client, Recorder(gemini_ok()))
    for _ in range(2):
        assert (await client.post("/api/v1/ai/chat", json={"message": "x"})).status_code == 200
    blocked = await client.post("/api/v1/ai/chat", json={"message": "x"})
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0


async def test_input_validation(client: AsyncClient) -> None:
    use_gemini(client, Recorder(gemini_ok()))
    assert (await client.post("/api/v1/ai/chat", json={"message": ""})).status_code == 422
    assert (await client.post("/api/v1/ai/chat", json={"message": "x" * 4001})).status_code == 422
    assert (
        await client.post("/api/v1/ai/chat", json={"message": "x", "mode": "hack"})
    ).status_code == 422
    too_long_history = [{"role": "user", "content": "a"}] * 13
    assert (
        await client.post("/api/v1/ai/chat", json={"message": "x", "history": too_long_history})
    ).status_code == 422


# ---------- with PostgreSQL: lesson context, signed-in users ----------


@pytest.fixture(scope="module")
async def ai_db() -> AsyncIterator[dict[str, int]]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(insert(Role), [{"name": n} for n in ("student", "instructor", "admin")])
    await seed()
    async with SessionLocal() as s:
        role_id = await s.scalar(select(Role.id).where(Role.name == "student"))
        users = [
            User(email=f"u{i}@studlab.test", full_name=f"U{i}", role_id=role_id) for i in (1, 2)
        ]
        s.add_all(users)
        await s.commit()
        lesson_id = await s.scalar(select(Lesson.id).order_by(Lesson.id).limit(1))
        ids = {"u1": users[0].id, "u2": users[1].id, "lesson": int(lesson_id or 0)}
    yield ids
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def sign_in(client: AsyncClient, user_id: int) -> None:
    client.cookies.set("studlab_session", create_session_token(user_id, get_settings()))


@requires_db
async def test_lesson_context_in_prompt(client: AsyncClient, ai_db: dict[str, int]) -> None:
    rec = Recorder(gemini_ok())
    use_gemini(client, rec)
    await client.post(
        "/api/v1/ai/chat", json={"message": "Объясни урок", "lesson_id": ai_db["lesson"]}
    )
    system = rec.body()["systemInstruction"]["parts"][0]["text"]
    assert "Курс: Основы Python" in system
    assert "Урок: Python: первая программа" in system


@requires_db
async def test_signed_in_conversation_is_saved_and_continued(
    client: AsyncClient, ai_db: dict[str, int]
) -> None:
    rec = Recorder(gemini_ok("Первый ответ"), gemini_ok("Второй ответ"))
    use_gemini(client, rec)
    sign_in(client, ai_db["u1"])

    first = (await client.post("/api/v1/ai/chat", json={"message": "Вопрос 1"})).json()
    conv = first["conversation_id"]
    assert conv is not None
    assert first["remaining_today"] == get_settings().ai_user_daily_limit - 1

    second = (
        await client.post(
            "/api/v1/ai/chat",
            json={
                "message": "Вопрос 2",
                "conversation_id": conv,
                "history": [{"role": "user", "content": "client history is ignored"}],
            },
        )
    ).json()
    assert second["conversation_id"] == conv
    texts = [c["parts"][0]["text"] for c in rec.body()["contents"]]
    assert texts == ["Вопрос 1", "Первый ответ", "Вопрос 2"]

    async with SessionLocal() as s:
        count = await s.scalar(
            select(func.count(AIMessage.id)).where(AIMessage.conversation_id == conv)
        )
    assert count == 4


@requires_db
async def test_cannot_use_someone_elses_conversation(
    client: AsyncClient, ai_db: dict[str, int]
) -> None:
    use_gemini(client, Recorder(gemini_ok()))
    sign_in(client, ai_db["u1"])
    conv = (await client.post("/api/v1/ai/chat", json={"message": "мой диалог"})).json()[
        "conversation_id"
    ]
    sign_in(client, ai_db["u2"])
    response = await client.post("/api/v1/ai/chat", json={"message": "x", "conversation_id": conv})
    assert response.status_code == 404


@requires_db
async def test_signed_in_hourly_limit(
    client: AsyncClient, ai_db: dict[str, int], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "ai_user_hourly_limit", 1)
    use_gemini(client, Recorder(gemini_ok()))
    sign_in(client, ai_db["u1"])  # u1 already sent requests in the tests above
    response = await client.post("/api/v1/ai/chat", json={"message": "x"})
    assert response.status_code == 429


# ---------- hedged requests: a silent model is raced by the next one ----------


def slow_first_transport(slow_model: str, body_for: Callable[[str], httpx.Response]):  # type: ignore[no-untyped-def]
    async def handler(request: httpx.Request) -> httpx.Response:
        model = request.url.path.split("/models/")[1].split(":")[0]
        if model == slow_model:
            await asyncio.sleep(5)  # "hangs"
        return body_for(model)

    return httpx.MockTransport(handler)


async def test_generate_hedges_slow_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(GeminiClient, "HEDGE_DELAY", 0.05)
    client = GeminiClient(
        "k", transport=slow_first_transport("slow", lambda m: gemini_ok(f"от {m}"))
    )
    started = asyncio.get_running_loop().time()
    reply = await client.generate(["slow", "fast"], "sys", [ChatTurn("user", "hi")])
    assert reply.model == "fast" and reply.text == "от fast"
    assert asyncio.get_running_loop().time() - started < 2  # did not wait for the slow model


async def test_stream_hedges_slow_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(GeminiClient, "HEDGE_DELAY", 0.05)
    sse = 'data: {"candidates":[{"content":{"parts":[{"text":"быстро"}]}}]}\n\n'
    client = GeminiClient(
        "k",
        transport=slow_first_transport(
            "slow",
            lambda m: httpx.Response(200, text=sse, headers={"content-type": "text/event-stream"}),
        ),
    )
    chunks = [c async for c in client.stream(["slow", "fast"], "sys", [ChatTurn("user", "hi")])]
    assert [c.text for c in chunks if not c.done] == ["быстро"]
    assert chunks[-1].done and chunks[-1].model == "fast"
