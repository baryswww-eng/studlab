from datetime import datetime

from pydantic import BaseModel, Field

from app.models.assessment import QuestionType, SubmissionStatus


class QuizOption(BaseModel):
    id: int
    text: str


class QuizQuestion(BaseModel):
    id: int
    position: int
    type: QuestionType
    text: str
    points: int
    options: list[QuizOption]  # empty for text questions; never includes correctness


class QuestionResult(BaseModel):
    question_id: int
    correct: bool
    points_earned: int
    correct_option_ids: list[int]
    accepted_answers: list[str]
    explanation: str


class AttemptResult(BaseModel):
    attempt_id: int
    score: int
    max_score: int
    percent: int
    passed: bool
    results: list[QuestionResult]
    created_at: datetime


class QuizOut(BaseModel):
    id: int
    lesson_id: int
    pass_percent: int
    questions: list[QuizQuestion]
    last_attempt: AttemptResult | None = None
    attempts_count: int = 0


class QuizSubmit(BaseModel):
    # question id → selected option ids (choice questions) or typed text (text questions)
    answers: dict[int, list[int] | str] = Field(max_length=100)


class SubmissionOut(BaseModel):
    id: int
    status: SubmissionStatus
    content: str
    score: int | None
    feedback_md: str | None
    reviewed_by: str | None
    created_at: datetime


class AssignmentOut(BaseModel):
    id: int
    lesson_id: int
    description_md: str
    expected_md: str
    answer_format: str
    submissions: list[SubmissionOut] = []


class SubmissionCreate(BaseModel):
    content: str = Field(min_length=1, max_length=20_000)
