"""STUD AI tutor (Google Gemini). All AI traffic goes through the backend."""

import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import service
from app.ai.gemini import ChatTurn, GeminiClient, GeminiError
from app.ai.prompts import build_system_prompt
from app.api.deps import SessionDep, SettingsDep, get_optional_user
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.rate_limit import SlidingWindowLimiter
from app.database.session import SessionLocal
from app.models import AIConversation, AIMessage, User
from app.schemas.ai import AIStatus, ChatRequest, ChatResponse

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger("app.ai")

anon_limiter = SlidingWindowLimiter(get_settings().ai_anon_hourly_limit, 3600)


def get_ai_client(settings: SettingsDep) -> GeminiClient:
    """Overridable in tests. 503 with a clear message when no key is configured."""
    if not settings.ai_available or settings.gemini_api_key is None:
        raise AppError(
            "ai_not_configured",
            "AI-преподаватель не настроен: добавьте GEMINI_API_KEY на сервере.",
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return GeminiClient(settings.gemini_api_key.get_secret_value(), settings.ai_timeout_seconds)


def _rate_limited(retry_after: int, message: str) -> AppError:
    return AppError(
        "rate_limited",
        message,
        status.HTTP_429_TOO_MANY_REQUESTS,
        headers={"Retry-After": str(retry_after)},
    )


@router.get("/status", response_model=AIStatus, summary="Is the AI tutor available")
async def ai_status(settings: SettingsDep) -> AIStatus:
    return AIStatus(
        enabled=settings.ai_available,
        model=settings.gemini_model if settings.ai_available else None,
        hourly_limit=settings.ai_user_hourly_limit,
    )


@dataclass
class Prepared:
    turns: list[ChatTurn]
    system: str
    models: list[str]
    conversation_id: int | None
    lesson_context: bool
    remaining: int | None


async def _prepare(
    body: ChatRequest,
    request: Request,
    session: AsyncSession,
    settings: Settings,
    user: User | None,
) -> Prepared:
    """Limits, history, lesson context and system prompt — shared by both chat endpoints."""
    remaining: int | None = None
    if user is not None:
        hour, day = await service.user_usage(session, user)
        if hour >= settings.ai_user_hourly_limit:
            raise _rate_limited(600, "Лимит запросов к AI на этот час исчерпан.")
        if day >= settings.ai_user_daily_limit:
            raise _rate_limited(3600, "Дневной лимит запросов к AI исчерпан.")
        remaining = settings.ai_user_daily_limit - day - 1
    else:
        client_ip = request.client.host if request.client else "unknown"
        wait = anon_limiter.hit(client_ip)
        if wait is not None:
            raise _rate_limited(wait, "Лимит запросов исчерпан. Войдите в аккаунт или подождите.")

    conversation_id: int | None = None
    if user is not None and body.conversation_id is not None:
        conversation = await service.load_conversation(session, user, body.conversation_id)
        if conversation is None:
            raise AppError("conversation_not_found", "Conversation not found", 404)
        history = service.conversation_turns(conversation)
        conversation_id = conversation.id
    else:
        history = [ChatTurn(role=h.role, text=h.content) for h in body.history]
    turns = service.trim_history([*history, ChatTurn(role="user", text=body.message)])

    context = await service.lesson_context(session, body.lesson_id) if body.lesson_id else None
    return Prepared(
        turns=turns,
        system=build_system_prompt(body.mode, context),
        models=[settings.gemini_model, *settings.gemini_fallback_models],
        conversation_id=conversation_id,
        lesson_context=context is not None,
        remaining=remaining,
    )


async def _persist(
    session: AsyncSession,
    user: User,
    body: ChatRequest,
    prep: Prepared,
    reply_text: str,
    model: str,
    prompt_tokens: int,
    output_tokens: int,
) -> int:
    conversation_id = prep.conversation_id
    if conversation_id is None:
        conversation = AIConversation(
            user_id=user.id,
            title=body.message.strip()[:120],
            mode=body.mode.value,
            lesson_id=body.lesson_id if prep.lesson_context else None,
        )
        session.add(conversation)
        await session.flush()
        conversation_id = conversation.id
    session.add_all(
        [
            AIMessage(
                conversation_id=conversation_id,
                role="user",
                content=body.message,
                prompt_tokens=prompt_tokens,
            ),
            AIMessage(
                conversation_id=conversation_id,
                role="model",
                content=reply_text,
                model=model,
                output_tokens=output_tokens,
            ),
        ]
    )
    await session.commit()
    return conversation_id


def _error_for(exc: GeminiError) -> AppError:
    if exc.blocked:
        return AppError(
            "ai_blocked", "AI не может ответить на этот запрос. Переформулируйте вопрос.", 422
        )
    return AppError(
        "ai_unavailable",
        "AI временно недоступен (лимит модели или сбой сервиса). Попробуйте позже.",
        status.HTTP_503_SERVICE_UNAVAILABLE,
    )


ChatDeps = Annotated[Settings, Depends(get_settings)]


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask STUD AI (anonymous: IP-limited; signed in: history is saved)",
    responses={404: {}, 422: {}, 429: {}, 503: {}},
)
async def chat(
    body: ChatRequest,
    request: Request,
    session: SessionDep,
    settings: ChatDeps,
    client: Annotated[GeminiClient, Depends(get_ai_client)],
    user: Annotated[User | None, Depends(get_optional_user)],
) -> ChatResponse:
    prep = await _prepare(body, request, session, settings, user)
    try:
        reply = await client.generate(prep.models, prep.system, prep.turns)
    except GeminiError as exc:
        raise _error_for(exc) from exc

    conversation_id = None
    if user is not None:
        conversation_id = await _persist(
            session,
            user,
            body,
            prep,
            reply.text,
            reply.model,
            reply.prompt_tokens,
            reply.output_tokens,
        )
    logger.info(
        "AI reply user=%s mode=%s model=%s tokens=%s/%s",
        user.id if user else "anon",
        body.mode,
        reply.model,
        reply.prompt_tokens,
        reply.output_tokens,
    )
    return ChatResponse(
        reply=reply.text,
        mode=body.mode,
        model=reply.model,
        conversation_id=conversation_id,
        remaining_today=prep.remaining,
    )


def _sse(event: dict[str, object]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


@router.post(
    "/chat/stream",
    summary="Ask STUD AI with a streamed answer (Server-Sent Events)",
    responses={200: {"content": {"text/event-stream": {}}}, 429: {}, 503: {}},
)
async def chat_stream(
    body: ChatRequest,
    request: Request,
    session: SessionDep,
    settings: ChatDeps,
    client: Annotated[GeminiClient, Depends(get_ai_client)],
    user: Annotated[User | None, Depends(get_optional_user)],
) -> StreamingResponse:
    # Limits and validation happen before the stream starts → normal JSON errors.
    prep = await _prepare(body, request, session, settings, user)
    user_id = user.id if user else None

    async def events() -> AsyncIterator[str]:
        parts: list[str] = []
        try:
            async for chunk in client.stream(prep.models, prep.system, prep.turns):
                if chunk.done:
                    conversation_id = None
                    if user_id is not None:
                        # The request-scoped session may already be closed: use a fresh one.
                        async with SessionLocal() as own:
                            owner = await own.get(User, user_id)
                            if owner is not None:
                                conversation_id = await _persist(
                                    own,
                                    owner,
                                    body,
                                    prep,
                                    "".join(parts),
                                    chunk.model,
                                    chunk.prompt_tokens,
                                    chunk.output_tokens,
                                )
                    logger.info(
                        "AI stream user=%s mode=%s model=%s tokens=%s/%s",
                        user_id or "anon",
                        body.mode,
                        chunk.model,
                        chunk.prompt_tokens,
                        chunk.output_tokens,
                    )
                    yield _sse(
                        {
                            "type": "done",
                            "model": chunk.model,
                            "conversation_id": conversation_id,
                            "remaining_today": prep.remaining,
                        }
                    )
                else:
                    parts.append(chunk.text)
                    yield _sse({"type": "delta", "text": chunk.text})
        except GeminiError as exc:
            yield _sse({"type": "error", "message": _error_for(exc).message})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
