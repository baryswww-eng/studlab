from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.course import CourseLevel, LessonType
from app.schemas.common import Locale


class CategoryOut(BaseModel):
    id: int
    slug: str
    name: str
    icon: str
    course_count: int


class CategorySummary(BaseModel):
    slug: str
    name: str
    icon: str


class InstructorSummary(BaseModel):
    id: int
    full_name: str
    headline: str | None = None


class InstructorOut(InstructorSummary):
    bio: str | None = None
    avatar_url: str | None = None


class CourseCard(BaseModel):
    id: int
    slug: str
    locale: Locale  # locale the texts are actually in (fallback if missing)
    title: str
    short_description: str
    level: CourseLevel
    price: Decimal
    currency: str
    is_free: bool
    cover_url: str | None
    category: CategorySummary | None
    instructor: InstructorSummary
    lessons_count: int
    duration_minutes: int
    is_featured: bool
    is_demo: bool


class LessonOutline(BaseModel):
    id: int
    position: int
    title: str
    type: LessonType
    duration_minutes: int
    is_preview: bool
    has_video: bool = False


class ModuleOutline(BaseModel):
    id: int
    position: int
    title: str
    lessons: list[LessonOutline]


class CourseDetail(CourseCard):
    description: str
    outcomes: list[str]
    requirements: list[str]
    instructor: InstructorOut
    modules: list[ModuleOutline]
    published_at: datetime | None


class LessonCourseRef(BaseModel):
    id: int
    slug: str
    title: str
    is_demo: bool


class LessonDetail(BaseModel):
    id: int
    title: str
    type: LessonType
    duration_minutes: int
    module_position: int
    module_title: str
    content_md: str
    # Only the validated 11-char YouTube id is exposed; the client builds the embed URL.
    youtube_id: str | None
    video_author: str | None
    course: LessonCourseRef
    modules: list[ModuleOutline]
    prev_lesson_id: int | None
    next_lesson_id: int | None


class PublicStats(BaseModel):
    published_courses: int
    categories: int
    lessons: int
