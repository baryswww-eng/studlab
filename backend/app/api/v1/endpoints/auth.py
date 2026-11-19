"""Email + password authentication. Passwords: Argon2id hashes; session: HttpOnly cookie."""

import logging

from fastapi import APIRouter, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import SessionDep, SettingsDep
from app.core.errors import AppError
from app.core.passwords import hash_password, needs_rehash, verify_password, verify_unknown_user
from app.core.rate_limit import SlidingWindowLimiter
from app.core.security import clear_session_cookie, create_session_token, set_session_cookie
from app.models import Role, RoleName, User, UserProfile
from app.schemas.user import LoginRequest, RegisterRequest, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("app.auth")

# Brute-force protection (per process; move to Redis when running several instances).
login_limiter = SlidingWindowLimiter(limit=10, window_seconds=15 * 60)
register_limiter = SlidingWindowLimiter(limit=5, window_seconds=60 * 60)


def user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=RoleName(user.role.name),
        created_at=user.created_at,
    )


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _too_many(wait: int) -> AppError:
    return AppError(
        "too_many_attempts",
        "Too many attempts, try again later",
        status.HTTP_429_TOO_MANY_REQUESTS,
        headers={"Retry-After": str(wait)},
    )


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a student account and sign in",
    responses={409: {}, 422: {}, 429: {}},
)
async def register(
    body: RegisterRequest,
    request: Request,
    response: Response,
    session: SessionDep,
    settings: SettingsDep,
) -> UserOut:
    if (wait := register_limiter.hit(_client_ip(request))) is not None:
        raise _too_many(wait)

    email = body.email.lower()
    if await session.scalar(select(User.id).where(User.email == email)):
        raise AppError("email_taken", "Email is already registered", status.HTTP_409_CONFLICT)

    role = await session.scalar(select(Role).where(Role.name == RoleName.STUDENT))
    if role is None:
        raise AppError("roles_missing", "Roles are not initialized", 500)

    user = User(
        email=email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role=role,
        profile=UserProfile(preferred_locale="ru"),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as exc:  # race: same email registered concurrently
        await session.rollback()
        raise AppError("email_taken", "Email is already registered", 409) from exc
    await session.refresh(user)

    set_session_cookie(response, create_session_token(user.id, settings), settings)
    logger.info("New user registered id=%s", user.id)
    return user_out(user)


@router.post(
    "/login",
    response_model=UserOut,
    summary="Sign in with email and password",
    responses={401: {}, 403: {}, 429: {}},
)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    session: SessionDep,
    settings: SettingsDep,
) -> UserOut:
    email = body.email.lower()
    if (wait := login_limiter.hit(f"{_client_ip(request)}|{email}")) is not None:
        raise _too_many(wait)

    user = await session.scalar(select(User).where(User.email == email))
    if user is None:
        verify_unknown_user(body.password)
        raise AppError("invalid_credentials", "Invalid email or password", 401)
    if not verify_password(body.password, user.password_hash):
        logger.info("Failed login for user id=%s", user.id)
        raise AppError("invalid_credentials", "Invalid email or password", 401)
    if not user.is_active:
        raise AppError("account_disabled", "Account is disabled", status.HTTP_403_FORBIDDEN)

    if user.password_hash and needs_rehash(user.password_hash):
        user.password_hash = hash_password(body.password)
        await session.commit()

    set_session_cookie(response, create_session_token(user.id, settings), settings)
    logger.info("User signed in id=%s", user.id)
    return user_out(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Clear the session")
async def logout(response: Response, settings: SettingsDep) -> Response:
    clear_session_cookie(response, settings)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
