"""Shared FastAPI dependencies: settings, DB session, current user, role checks."""

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.security import decode_session_token
from app.database.session import get_session
from app.models import RoleName, User

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_optional_user(
    request: Request, session: SessionDep, settings: SettingsDep
) -> User | None:
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        return None
    user_id = decode_session_token(token, settings)
    if user_id is None:
        return None
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None or not user.is_active:
        return None
    return user


async def get_current_user(user: Annotated[User | None, Depends(get_optional_user)]) -> User:
    if user is None:
        raise AppError("unauthorized", "Authentication required", status.HTTP_401_UNAUTHORIZED)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: RoleName) -> Callable[[User], Awaitable[User]]:
    """Usage: Depends(require_role(RoleName.ADMIN)) — checked on the server for every request."""

    async def checker(user: CurrentUser) -> User:
        if user.role.name not in {r.value for r in roles}:
            raise AppError("forbidden", "Insufficient permissions", status.HTTP_403_FORBIDDEN)
        return user

    return checker
