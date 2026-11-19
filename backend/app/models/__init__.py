"""ORM models.

Import every model module here so Alembic autogenerate sees all tables.
"""

from app.database.base import Base
from app.models.ai import AIConversation, AIMessage
from app.models.assessment import (
    Answer,
    Assignment,
    Question,
    QuestionType,
    Quiz,
    QuizAttempt,
    Submission,
    SubmissionStatus,
)
from app.models.course import (
    Category,
    Course,
    CourseLevel,
    CourseStatus,
    CourseTranslation,
    Lesson,
    LessonTranslation,
    LessonType,
    Module,
)
from app.models.progress import Enrollment, LessonProgress
from app.models.user import Role, RoleName, User, UserProfile

__all__ = [
    "AIConversation",
    "AIMessage",
    "Answer",
    "Assignment",
    "Question",
    "QuestionType",
    "Quiz",
    "QuizAttempt",
    "Submission",
    "SubmissionStatus",
    "Base",
    "Category",
    "Course",
    "CourseLevel",
    "CourseStatus",
    "CourseTranslation",
    "Enrollment",
    "Lesson",
    "LessonProgress",
    "LessonTranslation",
    "LessonType",
    "Module",
    "Role",
    "RoleName",
    "User",
    "UserProfile",
]
