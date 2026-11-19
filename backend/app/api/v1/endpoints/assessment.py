"""Quizzes (auto-graded) and practical assignments (AI review). Viewing is public;
submitting requires a signed-in student."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.ai.gemini import GeminiClient
from app.api.deps import CurrentUser, SessionDep, SettingsDep, get_optional_user
from app.core.config import Settings
from app.core.errors import AppError
from app.models import SubmissionStatus, User
from app.schemas.assessment import (
    AssignmentOut,
    AttemptResult,
    QuizOut,
    QuizSubmit,
    SubmissionCreate,
    SubmissionOut,
)
from app.services import assessment_service as svc
from app.services import progress_service

router = APIRouter(tags=["assessment"])

Id = Annotated[int, Path(ge=1, le=2_147_483_647)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]

DAILY_SUBMISSION_LIMIT = 20


def get_optional_ai_client(settings: SettingsDep) -> GeminiClient | None:
    """AI reviewer, or None when no key is configured (submission then waits for a teacher)."""
    if not settings.ai_available or settings.gemini_api_key is None:
        return None
    return GeminiClient(settings.gemini_api_key.get_secret_value(), settings.ai_timeout_seconds)


def _models(settings: Settings) -> list[str]:
    return [settings.gemini_model, *settings.gemini_fallback_models]


# ------------------------------------------------------------------ quizzes


@router.get("/quizzes/by-lesson/{lesson_id}", response_model=QuizOut, responses={404: {}})
async def quiz_for_lesson(lesson_id: Id, session: SessionDep, user: OptionalUser) -> QuizOut:
    quiz = await svc.load_quiz(session, lesson_id=lesson_id)
    if quiz is None:
        raise AppError("quiz_not_found", "Quiz not found", status.HTTP_404_NOT_FOUND)
    return await svc.quiz_out(session, quiz, user)


@router.post(
    "/quizzes/{quiz_id}/submit",
    response_model=AttemptResult,
    summary="Submit answers; passing (>= pass_percent) marks the lesson completed",
    responses={401: {}, 404: {}},
)
async def submit_quiz(
    quiz_id: Id, body: QuizSubmit, user: CurrentUser, session: SessionDep
) -> AttemptResult:
    quiz = await svc.load_quiz(session, quiz_id=quiz_id)
    if quiz is None:
        raise AppError("quiz_not_found", "Quiz not found", status.HTTP_404_NOT_FOUND)
    result = await svc.submit_quiz(session, quiz, user, body.answers)
    if result.passed:
        course_id = await svc.course_id_of_lesson(session, quiz.lesson_id)
        if course_id is not None:
            await progress_service.set_lesson_completed(
                session, user, quiz.lesson_id, course_id, True
            )
    return result


# ------------------------------------------------------------------ assignments


@router.get("/assignments/by-lesson/{lesson_id}", response_model=AssignmentOut, responses={404: {}})
async def assignment_for_lesson(
    lesson_id: Id, session: SessionDep, user: OptionalUser
) -> AssignmentOut:
    assignment = await svc.load_assignment(session, lesson_id=lesson_id)
    if assignment is None:
        raise AppError("assignment_not_found", "Assignment not found", status.HTTP_404_NOT_FOUND)
    return AssignmentOut(
        id=assignment.id,
        lesson_id=assignment.lesson_id,
        description_md=assignment.description_md,
        expected_md=assignment.expected_md,
        answer_format=assignment.answer_format,
        submissions=await svc.user_submissions(session, assignment, user) if user else [],
    )


@router.post(
    "/assignments/{assignment_id}/submissions",
    response_model=SubmissionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a solution; reviewed by STUD AI when available",
    responses={401: {}, 404: {}, 429: {}},
)
async def submit_assignment(
    assignment_id: Id,
    body: SubmissionCreate,
    user: CurrentUser,
    session: SessionDep,
    settings: SettingsDep,
    client: Annotated[GeminiClient | None, Depends(get_optional_ai_client)],
) -> SubmissionOut:
    assignment = await svc.load_assignment(session, assignment_id=assignment_id)
    if assignment is None:
        raise AppError("assignment_not_found", "Assignment not found", status.HTTP_404_NOT_FOUND)
    if await svc.submissions_today(session, user) >= DAILY_SUBMISSION_LIMIT:
        raise AppError(
            "rate_limited",
            "Daily submission limit reached",
            status.HTTP_429_TOO_MANY_REQUESTS,
            headers={"Retry-After": "3600"},
        )
    submission = await svc.create_submission(
        session, assignment, user, body.content, client, _models(settings)
    )
    if submission.status == SubmissionStatus.ACCEPTED:
        course_id = await svc.course_id_of_lesson(session, assignment.lesson_id)
        if course_id is not None:
            await progress_service.set_lesson_completed(
                session, user, assignment.lesson_id, course_id, True
            )
    return svc.submission_out(submission)
