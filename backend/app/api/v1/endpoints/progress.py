"""Lesson progress of the signed-in student (watching itself stays public)."""

from typing import Annotated

from fastapi import APIRouter, Path, status
from sqlalchemy import select

from app.api.deps import CurrentUser, SessionDep
from app.core.errors import AppError
from app.models import Course, CourseStatus
from app.schemas.progress import CourseProgress
from app.services import progress_service

router = APIRouter(prefix="/progress", tags=["progress"])

LessonId = Annotated[int, Path(ge=1, le=2_147_483_647)]


async def _course_for_lesson(session: SessionDep, lesson_id: int) -> int:
    course_id = await progress_service.published_course_of_lesson(session, lesson_id)
    if course_id is None:
        raise AppError("lesson_not_found", "Lesson not found", status.HTTP_404_NOT_FOUND)
    return course_id


@router.put(
    "/lessons/{lesson_id}",
    response_model=CourseProgress,
    summary="Mark a lesson as completed (idempotent)",
    responses={401: {}, 404: {}},
)
async def complete_lesson(
    lesson_id: LessonId, user: CurrentUser, session: SessionDep
) -> CourseProgress:
    course_id = await _course_for_lesson(session, lesson_id)
    return await progress_service.set_lesson_completed(session, user, lesson_id, course_id, True)


@router.delete(
    "/lessons/{lesson_id}",
    response_model=CourseProgress,
    summary="Unmark a completed lesson",
    responses={401: {}, 404: {}},
)
async def uncomplete_lesson(
    lesson_id: LessonId, user: CurrentUser, session: SessionDep
) -> CourseProgress:
    course_id = await _course_for_lesson(session, lesson_id)
    return await progress_service.set_lesson_completed(session, user, lesson_id, course_id, False)


@router.get(
    "/courses/{slug}",
    response_model=CourseProgress,
    summary="My progress in a course",
    responses={401: {}, 404: {}},
)
async def my_course_progress(
    slug: Annotated[str, Path(max_length=120, pattern=r"^[a-z0-9-]+$")],
    user: CurrentUser,
    session: SessionDep,
) -> CourseProgress:
    course_id = await session.scalar(
        select(Course.id).where(Course.slug == slug, Course.status == CourseStatus.PUBLISHED)
    )
    if course_id is None:
        raise AppError("course_not_found", "Course not found", status.HTTP_404_NOT_FOUND)
    return await progress_service.course_progress(session, user, course_id)
