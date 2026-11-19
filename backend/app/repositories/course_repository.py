"""Read-side queries for the public course catalog."""

from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy import Select, and_, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, selectinload

from app.models import (
    Category,
    Course,
    CourseLevel,
    CourseStatus,
    CourseTranslation,
    Lesson,
    Module,
    User,
)


class CourseSort(StrEnum):
    NEWEST = "newest"
    TITLE = "title"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"


class PriceFilter(StrEnum):
    FREE = "free"
    PAID = "paid"


@dataclass(frozen=True)
class CourseFilters:
    locale: str
    q: str | None = None
    category: str | None = None
    level: CourseLevel | None = None
    price: PriceFilter | None = None
    featured: bool | None = None
    sort: CourseSort = CourseSort.NEWEST


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# Aggregates per course: number of lessons and total duration.
_lesson_stats = (
    select(
        Module.course_id.label("course_id"),
        func.count(Lesson.id).label("lessons_count"),
        func.coalesce(func.sum(Lesson.duration_minutes), 0).label("duration_minutes"),
    )
    .join(Lesson, Lesson.module_id == Module.id)
    .group_by(Module.course_id)
    .subquery()
)


class CourseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _published(self) -> Select[tuple[Course]]:
        return select(Course).where(Course.status == CourseStatus.PUBLISHED)

    async def list_published(
        self, filters: CourseFilters, offset: int, limit: int
    ) -> tuple[list[tuple[Course, int, int]], int]:
        stmt = self._published()

        if filters.q:
            pattern = f"%{_escape_like(filters.q.strip())}%"
            stmt = stmt.where(
                exists().where(
                    CourseTranslation.course_id == Course.id,
                    or_(
                        CourseTranslation.title.ilike(pattern, escape="\\"),
                        CourseTranslation.short_description.ilike(pattern, escape="\\"),
                    ),
                )
            )
        if filters.category:
            stmt = stmt.join(Category, Category.id == Course.category_id).where(
                Category.slug == filters.category
            )
        if filters.level:
            stmt = stmt.where(Course.level == filters.level)
        if filters.price == PriceFilter.FREE:
            stmt = stmt.where(Course.price == 0)
        elif filters.price == PriceFilter.PAID:
            stmt = stmt.where(Course.price > 0)
        if filters.featured is not None:
            stmt = stmt.where(Course.is_featured == filters.featured)

        total = await self.session.scalar(
            select(func.count()).select_from(stmt.with_only_columns(Course.id).subquery())
        )

        stmt = stmt.outerjoin(_lesson_stats, _lesson_stats.c.course_id == Course.id).add_columns(
            func.coalesce(_lesson_stats.c.lessons_count, 0),
            func.coalesce(_lesson_stats.c.duration_minutes, 0),
        )

        match filters.sort:
            case CourseSort.TITLE:
                tr = aliased(CourseTranslation)
                stmt = stmt.outerjoin(
                    tr, and_(tr.course_id == Course.id, tr.locale == filters.locale)
                ).order_by(tr.title.asc().nulls_last(), Course.id)
            case CourseSort.PRICE_ASC:
                stmt = stmt.order_by(Course.price.asc(), Course.id)
            case CourseSort.PRICE_DESC:
                stmt = stmt.order_by(Course.price.desc(), Course.id)
            case _:
                stmt = stmt.order_by(Course.published_at.desc().nulls_last(), Course.id.desc())

        stmt = stmt.options(
            selectinload(Course.translations),
            joinedload(Course.category),
            joinedload(Course.instructor).joinedload(User.profile),
        )
        rows = (await self.session.execute(stmt.offset(offset).limit(limit))).unique().all()
        return [(row[0], int(row[1]), int(row[2])) for row in rows], int(total or 0)

    async def get_published(self, slug_or_id: str) -> Course | None:
        stmt = self._published().options(
            selectinload(Course.translations),
            joinedload(Course.category),
            joinedload(Course.instructor).joinedload(User.profile),
            selectinload(Course.modules)
            .selectinload(Module.lessons)
            .selectinload(Lesson.translations),
        )
        if slug_or_id.isdigit():
            stmt = stmt.where(Course.id == int(slug_or_id))
        else:
            stmt = stmt.where(Course.slug == slug_or_id)
        return (await self.session.execute(stmt)).unique().scalar_one_or_none()

    async def course_id_for_lesson(self, lesson_id: int) -> int | None:
        """Course id of a lesson, only if that course is published."""
        return await self.session.scalar(
            select(Course.id)
            .join(Module, Module.course_id == Course.id)
            .join(Lesson, Lesson.module_id == Module.id)
            .where(Lesson.id == lesson_id, Course.status == CourseStatus.PUBLISHED)
        )

    async def categories_with_counts(self) -> list[tuple[Category, int]]:
        count = (
            select(func.count(Course.id))
            .where(Course.category_id == Category.id, Course.status == CourseStatus.PUBLISHED)
            .correlate(Category)
            .scalar_subquery()
        )
        rows = await self.session.execute(
            select(Category, count).order_by(Category.sort_order, Category.id)
        )
        return [(c, int(n)) for c, n in rows.all()]

    async def public_stats(self) -> tuple[int, int, int]:
        published = Course.status == CourseStatus.PUBLISHED
        courses = await self.session.scalar(select(func.count(Course.id)).where(published))
        categories = await self.session.scalar(select(func.count(Category.id)))
        lessons = await self.session.scalar(
            select(func.count(Lesson.id))
            .join(Module, Module.id == Lesson.module_id)
            .join(Course, Course.id == Module.course_id)
            .where(published)
        )
        return int(courses or 0), int(categories or 0), int(lessons or 0)


__all__ = ["CourseFilters", "CourseRepository", "CourseSort", "PriceFilter"]
