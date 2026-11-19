"""Maps ORM entities to localized API schemas."""

import re
from typing import Protocol, cast

from app.models import Category, Course, Lesson, Module, User
from app.schemas.common import Locale
from app.schemas.course import (
    CategoryOut,
    CategorySummary,
    CourseCard,
    CourseDetail,
    InstructorOut,
    InstructorSummary,
    LessonCourseRef,
    LessonDetail,
    LessonOutline,
    ModuleOutline,
)


class _HasLocale(Protocol):
    locale: str


def pick_translation[T: _HasLocale](translations: list[T], locale: str) -> T | None:
    """Requested locale first, then any other available locale."""
    by_locale = {t.locale: t for t in translations}
    return by_locale.get(locale) or next(iter(by_locale.values()), None)


def _name(obj: Category | Module, locale: str) -> str:
    kk, ru = (
        (obj.name_kk, obj.name_ru) if isinstance(obj, Category) else (obj.title_kk, obj.title_ru)
    )
    return (ru or kk) if locale == "ru" else (kk or ru)


def category_out(category: Category, count: int, locale: str) -> CategoryOut:
    return CategoryOut(
        id=category.id,
        slug=category.slug,
        name=_name(category, locale),
        icon=category.icon,
        course_count=count,
    )


def _instructor_summary(user: User) -> InstructorSummary:
    return InstructorSummary(
        id=user.id,
        full_name=user.full_name,
        headline=user.profile.headline if user.profile else None,
    )


def course_card(course: Course, lessons_count: int, duration: int, locale: str) -> CourseCard:
    tr = pick_translation(course.translations, locale)
    return CourseCard(
        id=course.id,
        slug=course.slug,
        locale=cast(Locale, tr.locale if tr else locale),
        title=tr.title if tr else course.slug,
        short_description=tr.short_description if tr else "",
        level=course.level,
        price=course.price,
        currency=course.currency,
        is_free=course.price == 0,
        cover_url=course.cover_url,
        category=(
            CategorySummary(
                slug=course.category.slug,
                name=_name(course.category, locale),
                icon=course.category.icon,
            )
            if course.category
            else None
        ),
        instructor=_instructor_summary(course.instructor),
        lessons_count=lessons_count,
        duration_minutes=duration,
        is_featured=course.is_featured,
        is_demo=course.is_demo,
    )


_YOUTUBE_ID = re.compile(
    r"^https://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})(?:[&?#].*)?$"
)


def youtube_id(url: str | None) -> str | None:
    """Extract a YouTube video id; anything that is not a plain YouTube URL is ignored."""
    match = _YOUTUBE_ID.match(url or "")
    return match.group(1) if match else None


def _lesson_outline(lesson: Lesson, locale: str) -> LessonOutline:
    tr = pick_translation(lesson.translations, locale)
    return LessonOutline(
        id=lesson.id,
        position=lesson.position,
        title=tr.title if tr else f"#{lesson.position}",
        type=lesson.type,
        duration_minutes=lesson.duration_minutes,
        is_preview=lesson.is_preview,
        has_video=youtube_id(lesson.video_url) is not None,
    )


def _modules_outline(course: Course, locale: str) -> list[ModuleOutline]:
    return [
        ModuleOutline(
            id=m.id,
            position=m.position,
            title=_name(m, locale),
            lessons=[_lesson_outline(lesson, locale) for lesson in m.lessons],
        )
        for m in course.modules
    ]


def lesson_detail(course: Course, lesson_id: int, locale: str) -> LessonDetail | None:
    ordered = [(m, lesson) for m in course.modules for lesson in m.lessons]
    index = next((i for i, (_, lesson) in enumerate(ordered) if lesson.id == lesson_id), None)
    if index is None:
        return None
    module, lesson = ordered[index]
    tr = pick_translation(lesson.translations, locale)
    course_tr = pick_translation(course.translations, locale)
    return LessonDetail(
        id=lesson.id,
        title=tr.title if tr else f"#{lesson.position}",
        type=lesson.type,
        duration_minutes=lesson.duration_minutes,
        module_position=module.position,
        module_title=_name(module, locale),
        content_md=tr.content_md if tr else "",
        youtube_id=youtube_id(lesson.video_url),
        video_author=lesson.video_author,
        course=LessonCourseRef(
            id=course.id,
            slug=course.slug,
            title=course_tr.title if course_tr else course.slug,
            is_demo=course.is_demo,
        ),
        modules=_modules_outline(course, locale),
        prev_lesson_id=ordered[index - 1][1].id if index > 0 else None,
        next_lesson_id=ordered[index + 1][1].id if index + 1 < len(ordered) else None,
    )


def course_detail(course: Course, locale: str) -> CourseDetail:
    lessons = [lesson for m in course.modules for lesson in m.lessons]
    card = course_card(course, len(lessons), sum(x.duration_minutes for x in lessons), locale)
    tr = pick_translation(course.translations, locale)
    user = course.instructor
    profile = user.profile
    return CourseDetail(
        **card.model_dump(exclude={"instructor"}),
        description=tr.description if tr else "",
        outcomes=list(tr.outcomes) if tr else [],
        requirements=list(tr.requirements) if tr else [],
        instructor=InstructorOut(
            id=user.id,
            full_name=user.full_name,
            headline=profile.headline if profile else None,
            bio=profile.bio if profile else None,
            avatar_url=profile.avatar_url if profile else None,
        ),
        modules=_modules_outline(course, locale),
        published_at=course.published_at,
    )
