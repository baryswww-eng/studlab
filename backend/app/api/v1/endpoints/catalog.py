"""Public, read-only course catalog endpoints (no authentication required)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.database.session import get_session
from app.models import CourseLevel
from app.repositories.course_repository import (
    CourseFilters,
    CourseRepository,
    CourseSort,
    PriceFilter,
)
from app.schemas.common import Locale, Page
from app.schemas.course import CategoryOut, CourseCard, CourseDetail, LessonDetail, PublicStats
from app.services import course_service

router = APIRouter(tags=["catalog"])

Session = Annotated[AsyncSession, Depends(get_session)]
LocaleQuery = Annotated[Locale, Query(description="Content language")]


@router.get("/categories", response_model=list[CategoryOut], summary="List categories")
async def list_categories(session: Session, locale: LocaleQuery = "ru") -> list[CategoryOut]:
    rows = await CourseRepository(session).categories_with_counts()
    return [course_service.category_out(c, n, locale) for c, n in rows]


@router.get("/courses", response_model=Page[CourseCard], summary="Search published courses")
async def list_courses(
    session: Session,
    locale: LocaleQuery = "ru",
    q: Annotated[str | None, Query(max_length=100)] = None,
    category: Annotated[str | None, Query(max_length=80, pattern=r"^[a-z0-9-]+$")] = None,
    level: CourseLevel | None = None,
    price: PriceFilter | None = None,
    featured: bool | None = None,
    sort: CourseSort = CourseSort.NEWEST,
    page: Annotated[int, Query(ge=1, le=10_000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=48)] = 12,
) -> Page[CourseCard]:
    filters = CourseFilters(
        locale=locale,
        q=q or None,
        category=category,
        level=level,
        price=price,
        featured=featured,
        sort=sort,
    )
    rows, total = await CourseRepository(session).list_published(
        filters, offset=(page - 1) * page_size, limit=page_size
    )
    items = [course_service.course_card(c, n, d, locale) for c, n, d in rows]
    return Page.build(items, total, page, page_size)


@router.get(
    "/courses/{course}",
    response_model=CourseDetail,
    summary="Published course by slug or id",
    responses={404: {"description": "Course not found"}},
)
async def get_course(
    session: Session,
    course: Annotated[str, Path(max_length=120, pattern=r"^[a-z0-9-]+$")],
    locale: LocaleQuery = "ru",
) -> CourseDetail:
    found = await CourseRepository(session).get_published(course)
    if found is None:
        raise AppError("course_not_found", "Course not found", status.HTTP_404_NOT_FOUND)
    return course_service.course_detail(found, locale)


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonDetail,
    summary="Lesson of a published course (public: watching needs no enrollment)",
    responses={404: {"description": "Lesson not found"}},
)
async def get_lesson(
    session: Session,
    lesson_id: Annotated[int, Path(ge=1, le=2_147_483_647)],
    locale: LocaleQuery = "ru",
) -> LessonDetail:
    repo = CourseRepository(session)
    course_id = await repo.course_id_for_lesson(lesson_id)
    course = await repo.get_published(str(course_id)) if course_id else None
    detail = course_service.lesson_detail(course, lesson_id, locale) if course else None
    if detail is None:
        raise AppError("lesson_not_found", "Lesson not found", status.HTTP_404_NOT_FOUND)
    return detail


@router.get("/stats/public", response_model=PublicStats, summary="Real catalog counters")
async def public_stats(session: Session) -> PublicStats:
    courses, categories, lessons = await CourseRepository(session).public_stats()
    return PublicStats(published_courses=courses, categories=categories, lessons=lessons)
