"""Lesson completion, auto-enrollment and the student dashboard."""

from datetime import UTC, date, datetime, timedelta, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models import (
    AIConversation,
    AIMessage,
    Course,
    CourseStatus,
    Enrollment,
    Lesson,
    LessonProgress,
    Module,
    User,
)
from app.schemas.progress import CourseProgress, Dashboard, DashboardCourse, DashboardStats
from app.services.course_service import pick_translation

# Kazakhstan uses a single time zone, UTC+5 (since 2024). Days for streaks are local days.
LOCAL_TZ = timezone(timedelta(hours=5))


async def published_course_of_lesson(session: AsyncSession, lesson_id: int) -> int | None:
    return await session.scalar(
        select(Course.id)
        .join(Module, Module.course_id == Course.id)
        .join(Lesson, Lesson.module_id == Module.id)
        .where(Lesson.id == lesson_id, Course.status == CourseStatus.PUBLISHED)
    )


async def _lesson_ids(session: AsyncSession, course_id: int) -> list[int]:
    rows = await session.scalars(
        select(Lesson.id)
        .join(Module, Module.id == Lesson.module_id)
        .where(Module.course_id == course_id)
        .order_by(Module.position, Lesson.position)
    )
    return list(rows)


async def course_progress(session: AsyncSession, user: User, course_id: int) -> CourseProgress:
    ids = await _lesson_ids(session, course_id)
    done = set(
        await session.scalars(
            select(LessonProgress.lesson_id).where(
                LessonProgress.user_id == user.id, LessonProgress.lesson_id.in_(ids)
            )
        )
    )
    completed = [i for i in ids if i in done]
    total = len(ids)
    return CourseProgress(
        course_id=course_id,
        completed_lesson_ids=completed,
        completed=len(completed),
        total=total,
        percent=round(len(completed) * 100 / total) if total else 0,
    )


async def set_lesson_completed(
    session: AsyncSession, user: User, lesson_id: int, course_id: int, completed: bool
) -> CourseProgress:
    now = datetime.now(UTC)
    if completed:
        await session.execute(
            pg_insert(LessonProgress)
            .values(user_id=user.id, lesson_id=lesson_id)
            .on_conflict_do_nothing(index_elements=["user_id", "lesson_id"])
        )
        await session.execute(
            pg_insert(Enrollment)
            .values(user_id=user.id, course_id=course_id, last_lesson_id=lesson_id)
            .on_conflict_do_update(
                index_elements=["user_id", "course_id"],
                set_={"last_lesson_id": lesson_id, "last_activity_at": now},
            )
        )
    else:
        await session.execute(
            delete(LessonProgress).where(
                LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson_id
            )
        )
    await session.commit()
    return await course_progress(session, user, course_id)


def _streak(days: set[date], today: date) -> int:
    """Consecutive active days ending today (or yesterday, so the streak survives until tonight)."""
    start = today if today in days else today - timedelta(days=1)
    streak = 0
    while start - timedelta(days=streak) in days:
        streak += 1
    return streak


async def dashboard(session: AsyncSession, user: User, locale: str) -> Dashboard:
    enrollments = list(
        await session.scalars(
            select(Enrollment)
            .where(Enrollment.user_id == user.id)
            .order_by(Enrollment.last_activity_at.desc())
        )
    )
    progress_rows = (
        await session.execute(
            select(LessonProgress.lesson_id, LessonProgress.completed_at, Lesson.duration_minutes)
            .join(Lesson, Lesson.id == LessonProgress.lesson_id)
            .where(LessonProgress.user_id == user.id)
        )
    ).all()
    done = {row.lesson_id for row in progress_rows}

    courses: list[DashboardCourse] = []
    if enrollments:
        loaded = {
            c.id: c
            for c in await session.scalars(
                select(Course)
                .where(
                    Course.id.in_([e.course_id for e in enrollments]),
                    Course.status == CourseStatus.PUBLISHED,
                )
                .options(
                    selectinload(Course.translations),
                    joinedload(Course.category),
                    selectinload(Course.modules)
                    .selectinload(Module.lessons)
                    .selectinload(Lesson.translations),
                )
            )
        }
        for enrollment in enrollments:
            course = loaded.get(enrollment.course_id)
            if course is None:
                continue
            lessons = [lesson for m in course.modules for lesson in m.lessons]
            completed = sum(1 for lesson in lessons if lesson.id in done)
            nxt = next((lesson for lesson in lessons if lesson.id not in done), None)
            tr = pick_translation(course.translations, locale)
            nxt_tr = pick_translation(nxt.translations, locale) if nxt else None
            courses.append(
                DashboardCourse(
                    id=course.id,
                    slug=course.slug,
                    title=tr.title if tr else course.slug,
                    category_icon=course.category.icon if course.category else None,
                    level=course.level,
                    completed=completed,
                    total=len(lessons),
                    percent=round(completed * 100 / len(lessons)) if lessons else 0,
                    last_activity_at=enrollment.last_activity_at,
                    next_lesson_id=nxt.id if nxt else None,
                    next_lesson_title=nxt_tr.title if nxt_tr else None,
                )
            )

    today = datetime.now(LOCAL_TZ).date()
    active_days = {row.completed_at.astimezone(LOCAL_TZ).date() for row in progress_rows}
    ai_questions = await session.scalar(
        select(func.count(AIMessage.id))
        .join(AIConversation, AIConversation.id == AIMessage.conversation_id)
        .where(AIConversation.user_id == user.id, AIMessage.role == "user")
    )
    return Dashboard(
        stats=DashboardStats(
            courses_started=len(courses),
            courses_completed=sum(1 for c in courses if c.total and c.completed == c.total),
            lessons_completed=len(done),
            minutes_learned=sum(row.duration_minutes for row in progress_rows),
            streak_days=_streak(active_days, today),
            active_days_last_7=sum(1 for d in active_days if (today - d).days < 7),
            ai_questions=int(ai_questions or 0),
        ),
        courses=courses,
    )
