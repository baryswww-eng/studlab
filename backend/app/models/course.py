"""Course catalog: Category → Course → Module → Lesson, with kk/ru translations."""

from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.assessment import Assignment, Quiz
    from app.models.user import User

LOCALES = ("kk", "ru")


def _enum(cls: type[enum.Enum], name: str) -> Enum:
    # Store enum *values* ("beginner"), not member names.
    return Enum(cls, name=name, values_callable=lambda e: [m.value for m in e])


class CourseLevel(enum.StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseStatus(enum.StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    HIDDEN = "hidden"


class LessonType(enum.StrEnum):
    TEXT = "text"
    VIDEO = "video"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name_kk: Mapped[str] = mapped_column(String(120))
    name_ru: Mapped[str] = mapped_column(String(120))
    icon: Mapped[str] = mapped_column(String(40), default="code")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    courses: Mapped[list[Course]] = relationship(back_populates="category")


class Course(TimestampMixin, Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("price >= 0", name="price_non_negative"),
        Index("ix_courses_status_published_at", "status", "published_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), index=True
    )
    instructor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True
    )
    level: Mapped[CourseLevel] = mapped_column(_enum(CourseLevel, "course_level"))
    status: Mapped[CourseStatus] = mapped_column(
        _enum(CourseStatus, "course_status"), default=CourseStatus.DRAFT, index=True
    )
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    currency: Mapped[str] = mapped_column(String(3), default="KZT")
    cover_url: Mapped[str | None] = mapped_column(String(500))
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    category: Mapped[Category | None] = relationship(back_populates="courses")
    instructor: Mapped[User] = relationship(back_populates="courses")
    translations: Mapped[list[CourseTranslation]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
    modules: Mapped[list[Module]] = relationship(
        back_populates="course", cascade="all, delete-orphan", order_by="Module.position"
    )


class CourseTranslation(Base):
    __tablename__ = "course_translations"
    __table_args__ = (UniqueConstraint("course_id", "locale"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    locale: Mapped[str] = mapped_column(String(5))
    title: Mapped[str] = mapped_column(String(200))
    short_description: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default="")
    outcomes: Mapped[list[str]] = mapped_column(JSON, default=list)
    requirements: Mapped[list[str]] = mapped_column(JSON, default=list)

    course: Mapped[Course] = relationship(back_populates="translations")


class Module(TimestampMixin, Base):
    __tablename__ = "modules"
    __table_args__ = (UniqueConstraint("course_id", "position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    title_kk: Mapped[str] = mapped_column(String(200))
    title_ru: Mapped[str] = mapped_column(String(200))

    course: Mapped[Course] = relationship(back_populates="modules")
    lessons: Mapped[list[Lesson]] = relationship(
        back_populates="module", cascade="all, delete-orphan", order_by="Lesson.position"
    )


class Lesson(TimestampMixin, Base):
    __tablename__ = "lessons"
    __table_args__ = (UniqueConstraint("module_id", "position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    type: Mapped[LessonType] = mapped_column(_enum(LessonType, "lesson_type"))
    duration_minutes: Mapped[int] = mapped_column(Integer, default=10)
    is_preview: Mapped[bool] = mapped_column(Boolean, default=False)
    video_url: Mapped[str | None] = mapped_column(String(500))
    # Credit for third-party videos (e.g. the YouTube channel name).
    video_author: Mapped[str | None] = mapped_column(String(120))

    module: Mapped[Module] = relationship(back_populates="lessons")
    translations: Mapped[list[LessonTranslation]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan"
    )
    quiz: Mapped[Quiz | None] = relationship(cascade="all, delete-orphan", uselist=False)
    assignment: Mapped[Assignment | None] = relationship(
        cascade="all, delete-orphan", uselist=False
    )


class LessonTranslation(Base):
    __tablename__ = "lesson_translations"
    __table_args__ = (UniqueConstraint("lesson_id", "locale"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    locale: Mapped[str] = mapped_column(String(5))
    title: Mapped[str] = mapped_column(String(200))
    content_md: Mapped[str] = mapped_column(Text, default="")

    lesson: Mapped[Lesson] = relationship(back_populates="translations")
