import logging

from fastapi import APIRouter, Response, status

from app.api.deps import CurrentUser, SessionDep
from app.api.v1.endpoints.auth import user_out
from app.core.errors import AppError
from app.core.passwords import hash_password, verify_password
from app.schemas.progress import Dashboard, PasswordChange
from app.schemas.user import UserOut, UserUpdate
from app.services import progress_service

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger("app.auth")


@router.get("/me", response_model=UserOut, summary="Current user", responses={401: {}})
async def read_me(user: CurrentUser) -> UserOut:
    return user_out(user)


@router.patch("/me", response_model=UserOut, summary="Update own profile", responses={401: {}})
async def update_me(body: UserUpdate, user: CurrentUser, session: SessionDep) -> UserOut:
    user.full_name = " ".join(body.full_name.split())
    await session.commit()
    await session.refresh(user)
    return user_out(user)


@router.get(
    "/me/dashboard",
    response_model=Dashboard,
    summary="Student dashboard: stats and my courses",
    responses={401: {}},
)
async def my_dashboard(user: CurrentUser, session: SessionDep) -> Dashboard:
    return await progress_service.dashboard(session, user, "ru")


@router.post(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change own password",
    responses={400: {}, 401: {}, 422: {}},
)
async def change_password(body: PasswordChange, user: CurrentUser, session: SessionDep) -> Response:
    if not verify_password(body.current_password, user.password_hash):
        raise AppError("wrong_password", "Current password is incorrect", 400)
    if body.current_password == body.new_password:
        raise AppError("same_password", "New password must differ from the current one", 400)
    user.password_hash = hash_password(body.new_password)
    await session.commit()
    logger.info("Password changed for user id=%s", user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
