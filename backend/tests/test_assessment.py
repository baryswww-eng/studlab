"""Quizzes, practical assignments (AI review mocked) and the streaming AI chat."""

import json
from collections.abc import AsyncIterator

import httpx
import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select

from app.ai.gemini import GeminiClient
from app.api.v1.endpoints import ai as ai_endpoint
from app.api.v1.endpoints import assessment as assessment_endpoint
from app.core.config import get_settings
from app.core.security import create_session_token
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models import Answer, Question, Role, User
from app.scripts.seed_demo import seed
from tests.conftest import requires_db

pytestmark = requires_db


@pytest.fixture(scope="module", autouse=True)
async def db() -> AsyncIterator[dict[str, int]]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(insert(Role), [{"name": n} for n in ("student", "instructor", "admin")])
    await seed()
    async with SessionLocal() as s:
        role_id = await s.scalar(select(Role.id).where(Role.name == "student"))
        users = [
            User(email=f"a{i}@example.com", full_name=f"A{i}", role_id=role_id) for i in (1, 2)
        ]
        s.add_all(users)
        await s.commit()
        ids = {"u1": users[0].id, "u2": users[1].id}
    yield ids
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def sign_in(client: AsyncClient, user_id: int) -> None:
    client.cookies.set("studlab_session", create_session_token(user_id, get_settings()))


async def practice_lessons(client: AsyncClient, slug: str = "python-basics") -> list[dict]:
    course = (await client.get(f"/api/v1/courses/{slug}")).json()
    return course["modules"][2]["lessons"]  # quiz, task 1, task 2


async def correct_answers(quiz_id: int) -> dict[str, object]:
    async with SessionLocal() as s:
        questions = (await s.scalars(select(Question).where(Question.quiz_id == quiz_id))).all()
        out: dict[str, object] = {}
        for q in questions:
            answers = (await s.scalars(select(Answer).where(Answer.question_id == q.id))).all()
            good = [a for a in answers if a.is_correct]
            out[str(q.id)] = good[0].text if q.type == "text" else [a.id for a in good]
        return out


# ------------------------------------------------------------------ quizzes


async def test_quiz_hides_correct_answers(client: AsyncClient) -> None:
    quiz_lesson = (await practice_lessons(client))[0]
    body = (await client.get(f"/api/v1/quizzes/by-lesson/{quiz_lesson['id']}")).json()
    assert len(body["questions"]) == 6
    raw = json.dumps(body, ensure_ascii=False)
    assert "is_correct" not in raw and "explanation" not in raw
    text_q = [q for q in body["questions"] if q["type"] == "text"]
    assert text_q and all(q["options"] == [] for q in text_q)  # accepted answers never sent


async def test_submit_requires_login(client: AsyncClient) -> None:
    quiz_lesson = (await practice_lessons(client))[0]
    quiz = (await client.get(f"/api/v1/quizzes/by-lesson/{quiz_lesson['id']}")).json()
    r = await client.post(f"/api/v1/quizzes/{quiz['id']}/submit", json={"answers": {}})
    assert r.status_code == 401


async def test_quiz_pass_marks_lesson_completed(client: AsyncClient, db: dict[str, int]) -> None:
    sign_in(client, db["u1"])
    quiz_lesson = (await practice_lessons(client))[0]
    quiz = (await client.get(f"/api/v1/quizzes/by-lesson/{quiz_lesson['id']}")).json()
    answers = await correct_answers(quiz["id"])
    # Text answers are normalized: case, spaces, backticks.
    for q in quiz["questions"]:
        if q["type"] == "text":
            answers[str(q["id"])] = f"  `{str(answers[str(q['id'])]).upper()}` "

    result = (
        await client.post(f"/api/v1/quizzes/{quiz['id']}/submit", json={"answers": answers})
    ).json()
    assert (result["score"], result["max_score"], result["percent"], result["passed"]) == (
        6,
        6,
        100,
        True,
    )
    assert all(r["correct"] and r["explanation"] for r in result["results"])

    progress = (await client.get("/api/v1/progress/courses/python-basics")).json()
    assert quiz_lesson["id"] in progress["completed_lesson_ids"]

    again = (await client.get(f"/api/v1/quizzes/by-lesson/{quiz_lesson['id']}")).json()
    assert again["attempts_count"] == 1
    assert again["last_attempt"]["percent"] == 100


async def test_quiz_wrong_answers_fail(client: AsyncClient, db: dict[str, int]) -> None:
    sign_in(client, db["u2"])
    quiz_lesson = (await practice_lessons(client))[0]
    quiz = (await client.get(f"/api/v1/quizzes/by-lesson/{quiz_lesson['id']}")).json()
    single = next(q for q in quiz["questions"] if q["type"] == "single")
    all_options = [o["id"] for o in single["options"]]  # choosing every option is not "single"
    result = (
        await client.post(
            f"/api/v1/quizzes/{quiz['id']}/submit",
            json={"answers": {str(single["id"]): all_options, "999999": "junk"}},
        )
    ).json()
    assert result["passed"] is False
    assert result["score"] == 0
    first = next(r for r in result["results"] if r["question_id"] == single["id"])
    assert first["correct"] is False and len(first["correct_option_ids"]) == 1
    progress = (await client.get("/api/v1/progress/courses/python-basics")).json()
    assert quiz_lesson["id"] not in progress["completed_lesson_ids"]


# ------------------------------------------------------------------ assignments


class Recorder:
    def __init__(self, response: httpx.Response):
        self.response = response
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.response


def gemini_json(payload: dict[str, object]) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "candidates": [
                {"content": {"parts": [{"text": json.dumps(payload, ensure_ascii=False)}]}}
            ]
        },
    )


def use_reviewer(client: AsyncClient, recorder: Recorder | None) -> None:
    app = client._transport.app  # type: ignore[attr-defined]
    app.dependency_overrides[assessment_endpoint.get_optional_ai_client] = (
        (lambda: None)
        if recorder is None
        else (lambda: GeminiClient("test-key", transport=httpx.MockTransport(recorder)))
    )


async def test_assignment_hides_criteria(client: AsyncClient) -> None:
    task = (await practice_lessons(client))[1]
    body = (await client.get(f"/api/v1/assignments/by-lesson/{task['id']}")).json()
    assert "чётное" in body["description_md"]
    assert "criteria" not in body
    assert body["submissions"] == []


async def test_accepted_submission(client: AsyncClient, db: dict[str, int]) -> None:
    sign_in(client, db["u1"])
    rec = Recorder(gemini_json({"score": 90, "accepted": True, "feedback": "Отлично!"}))
    use_reviewer(client, rec)
    task = (await practice_lessons(client))[1]
    assignment = (await client.get(f"/api/v1/assignments/by-lesson/{task['id']}")).json()
    code = "n = int(input())\nprint('чётное' if n % 2 == 0 else 'нечётное')"
    r = await client.post(
        f"/api/v1/assignments/{assignment['id']}/submissions", json={"content": code}
    )
    assert r.status_code == 201
    sub = r.json()
    assert (sub["status"], sub["score"], sub["feedback_md"]) == ("accepted", 90, "Отлично!")
    assert sub["reviewed_by"].startswith("STUD AI")

    sent = json.loads(rec.requests[0].content)
    assert sent["generationConfig"]["responseMimeType"] == "application/json"
    prompt = sent["contents"][0]["parts"][0]["text"]
    assert "<<<РЕШЕНИЕ>>>" in prompt and code in prompt and "% 2" in prompt  # criteria included

    progress = (await client.get("/api/v1/progress/courses/python-basics")).json()
    assert task["id"] in progress["completed_lesson_ids"]
    listed = (await client.get(f"/api/v1/assignments/by-lesson/{task['id']}")).json()
    assert listed["submissions"][0]["id"] == sub["id"]


async def test_needs_work_and_score_cannot_be_forced(
    client: AsyncClient, db: dict[str, int]
) -> None:
    sign_in(client, db["u2"])
    # Model claims accepted but with a low score → treated as needs_work.
    use_reviewer(
        client, Recorder(gemini_json({"score": 40, "accepted": True, "feedback": "Нет проверки"}))
    )
    task = (await practice_lessons(client))[2]
    assignment = (await client.get(f"/api/v1/assignments/by-lesson/{task['id']}")).json()
    r = await client.post(
        f"/api/v1/assignments/{assignment['id']}/submissions", json={"content": "x"}
    )
    assert r.json()["status"] == "needs_work"


async def test_submission_waits_when_ai_unavailable(
    client: AsyncClient, db: dict[str, int]
) -> None:
    sign_in(client, db["u2"])
    use_reviewer(client, None)
    task = (await practice_lessons(client, "sql-postgresql"))[1]
    assignment = (await client.get(f"/api/v1/assignments/by-lesson/{task['id']}")).json()
    r = await client.post(
        f"/api/v1/assignments/{assignment['id']}/submissions", json={"content": "CREATE TABLE x();"}
    )
    body = r.json()
    assert (body["status"], body["score"], body["feedback_md"]) == ("submitted", None, None)


async def test_submission_validation(client: AsyncClient, db: dict[str, int]) -> None:
    task = (await practice_lessons(client))[1]
    assignment = (await client.get(f"/api/v1/assignments/by-lesson/{task['id']}")).json()
    client.cookies.clear()
    url = f"/api/v1/assignments/{assignment['id']}/submissions"
    assert (await client.post(url, json={"content": "x"})).status_code == 401
    sign_in(client, db["u1"])
    assert (await client.post(url, json={"content": ""})).status_code == 422
    assert (await client.post(url, json={"content": "x" * 20_001})).status_code == 422


# ------------------------------------------------------------------ streaming chat


async def test_chat_stream(client: AsyncClient, db: dict[str, int]) -> None:
    ai_endpoint.anon_limiter.reset()
    sse = (
        'data: {"candidates":[{"content":{"parts":[{"text":"Сәлем! "}]}}]}\n\n'
        'data: {"candidates":[{"content":{"parts":[{"text":"Python — язык."}]}}],'
        '"usageMetadata":{"promptTokenCount":5,"candidatesTokenCount":7}}\n\n'
    )
    rec = Recorder(httpx.Response(200, text=sse, headers={"content-type": "text/event-stream"}))
    app = client._transport.app  # type: ignore[attr-defined]
    app.dependency_overrides[ai_endpoint.get_ai_client] = lambda: GeminiClient(
        "test-key", transport=httpx.MockTransport(rec)
    )
    sign_in(client, db["u1"])
    r = await client.post("/api/v1/ai/chat/stream", json={"message": "Python деген не?"})
    assert r.status_code == 200
    events = [json.loads(line[5:]) for line in r.text.splitlines() if line.startswith("data:")]
    assert [e["type"] for e in events] == ["delta", "delta", "done"]
    assert "".join(e["text"] for e in events if e["type"] == "delta") == "Сәлем! Python — язык."
    assert events[-1]["conversation_id"] is not None  # saved for signed-in users
    assert "streamGenerateContent" in str(rec.requests[0].url)
    system = json.loads(rec.requests[0].content)["systemInstruction"]["parts"][0]["text"]
    assert "Свободный чат" in system  # default mode answers any question


async def test_chat_stream_error_event(client: AsyncClient) -> None:
    ai_endpoint.anon_limiter.reset()
    client.cookies.clear()
    app = client._transport.app  # type: ignore[attr-defined]
    app.dependency_overrides[ai_endpoint.get_ai_client] = lambda: GeminiClient(
        "test-key", transport=httpx.MockTransport(Recorder(httpx.Response(503)))
    )
    r = await client.post("/api/v1/ai/chat/stream", json={"message": "привет"})
    events = [json.loads(line[5:]) for line in r.text.splitlines() if line.startswith("data:")]
    assert events == [{"type": "error", "message": events[0]["message"]}]
    assert "недоступен" in events[0]["message"]
