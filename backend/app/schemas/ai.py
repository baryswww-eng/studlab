from typing import Literal

from pydantic import BaseModel, Field

from app.ai.prompts import AIMode


class ChatHistoryItem(BaseModel):
    role: Literal["user", "model"]
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    mode: AIMode = AIMode.CHAT
    lesson_id: int | None = Field(default=None, ge=1)
    # Signed-in users continue a stored conversation; history is then loaded from the DB.
    conversation_id: int | None = Field(default=None, ge=1)
    # Anonymous users send recent turns themselves (trimmed server-side).
    history: list[ChatHistoryItem] = Field(default_factory=list, max_length=12)


class ChatResponse(BaseModel):
    reply: str
    mode: AIMode
    model: str
    conversation_id: int | None
    remaining_today: int | None


class AIStatus(BaseModel):
    enabled: bool
    model: str | None
    hourly_limit: int
