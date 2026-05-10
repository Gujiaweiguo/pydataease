from __future__ import annotations

from typing import cast

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenUser


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> TokenUser:
    user = cast(TokenUser | None, getattr(request.state, "user", None))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    db_user = await UserRepository(session).get_by_id(user.user_id)
    if db_user is None or not db_user.enable:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is disabled")

    return TokenUser(user_id=db_user.id, oid=db_user.oid or 0, language=db_user.language or "zh-CN")


async def get_optional_user(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> TokenUser | None:
    user = cast(TokenUser | None, getattr(request.state, "user", None))
    if user is None:
        return None

    db_user = await UserRepository(session).get_by_id(user.user_id)
    if db_user is None or not db_user.enable:
        return None

    return TokenUser(user_id=db_user.id, oid=db_user.oid or 0, language=db_user.language or "zh-CN")
