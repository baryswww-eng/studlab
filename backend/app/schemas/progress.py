from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.course import CourseLevel
from app.schemas.user import check_password


class CourseProgress(BaseModel):
    course_id: int
    completed_lesson_ids: list[int]
    completed: int
    total: int
    percent: int


class DashboardCourse(BaseModel):
    id: int
    slug: str
    title: str
    category_icon: str | None
    level: CourseLevel
    completed: int
    total: int
    percent: int
    last_activity_at: datetime
    next_lesson_id: int | None
    next_lesson_title: str | None


class DashboardStats(BaseModel):
    courses_started: int
    courses_completed: int
    lessons_completed: int
    minutes_learned: int
    streak_days: int
    active_days_last_7: int
    ai_questions: int


class Dashboard(BaseModel):
    stats: DashboardStats
    courses: list[DashboardCourse]


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def _policy(cls, value: str) -> str:
        return check_password(value)
