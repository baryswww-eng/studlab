"""STUD AI business logic: limits, lesson context, history and persistence."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.gemini import ChatTurn
from app.models import AIConversation, AIMessage, Course, CourseTranslation, Lesson, Module, User
from app.services.course_service import pick_translation

MAX_HISTORY_TURNS = 12
MAX_HISTORY_CHARS = 24_000


async def count_user_requests(session: AsyncSession, user_id: int, since: datetime) -> int:
    return int(
        await session.scalar(
            select(func.count(AIMessage.id))
            .join(AIConversation, AIConversation.id == AIMessage.conversation_id)
            .where(
                AIConversation.user_id == user_id,
                AIMessage.role == "user",
                AIMessage.created_at >= since,
            )
        )
        or 0
    )


async def user_usage(session: AsyncSession, user: User) -> tuple[int, int]:
    now = datetime.now(UTC)
    hour = await count_user_requests(session, user.id, now - timedelta(hours=1))
    day = await count_user_requests(session, user.id, now - timedelta(days=1))
    return hour, day


async def lesson_context(session: AsyncSession, lesson_id: int) -> str | None:
    """Short text describing the lesson the student is on (published courses only)."""
    row = (
        await session.execute(
            select(Lesson, Module, Course)
            .join(Module, Module.id == Lesson.module_id)
            .join(Course, Course.id == Module.course_id)
            .where(Lesson.id == lesson_id, Course.status == "published")
            .options(selectinload(Lesson.translations), selectinload(Course.translations))
        )
    ).first()
    if row is None:
        return None
    lesson, module, course = row
    lesson_tr = pick_translation(lesson.translations, "ru")
    course_tr: CourseTranslation | None = pick_translation(course.translations, "ru")
    parts = [
        f"Курс: {course_tr.title if course_tr else course.slug}",
        f"Модуль {module.position}: {module.title_ru or module.title_kk}",
        f"Урок: {lesson_tr.title if lesson_tr else lesson.position}",
    ]
    if course_tr and course_tr.short_description:
        parts.append(f"О курсе: {course_tr.short_description}")
    if lesson_tr and lesson_tr.content_md:
        parts.append(f"Материал урока:\n{lesson_tr.content_md[:4000]}")
    return "\n".join(parts)


def trim_history(turns: list[ChatTurn]) -> list[ChatTurn]:
    """Keep the most recent turns within count/size budgets; must start with a user turn."""
    kept: list[ChatTurn] = []
    total = 0
    for turn in reversed(turns[-MAX_HISTORY_TURNS:]):
        total += len(turn.text)
        if total > MAX_HISTORY_CHARS:
            break
        kept.append(turn)
    kept.reverse()
    while kept and kept[0].role != "user":
        kept.pop(0)
    return kept


async def load_conversation(
    session: AsyncSession, user: User, conversation_id: int
) -> AIConversation | None:
    return await session.scalar(
        select(AIConversation)
        .where(AIConversation.id == conversation_id, AIConversation.user_id == user.id)
        .options(selectinload(AIConversation.messages))
    )


def conversation_turns(conversation: AIConversation) -> list[ChatTurn]:
    return [
        ChatTurn(role="model" if m.role == "model" else "user", text=m.content)
        for m in conversation.messages
    ]
