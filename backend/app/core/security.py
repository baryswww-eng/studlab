"""Our own session token (HS256 JWT in an HttpOnly cookie).

Issued after a successful /auth/login or /auth/register; the browser then only
carries this signed session cookie (not readable from JavaScript).
"""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Response

from app.core.config import Settings

ALGORITHM = "HS256"


def create_session_token(user_id: int, settings: Settings) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(days=settings.session_expire_days),
        "typ": "session",
    }
    return jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=ALGORITHM)


def decode_session_token(token: str, settings: Settings) -> int | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError:
        return None
    if payload.get("typ") != "session":
        return None
    try:
        return int(payload["sub"])
    except (TypeError, ValueError):
        return None


def set_session_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_expire_days * 24 * 3600,
        httponly=True,  # not readable from JavaScript (XSS-safe)
        secure=settings.cookie_secure,
        samesite="lax",  # not sent on cross-site POSTs (CSRF mitigation)
        path="/",
    )


def clear_session_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )
