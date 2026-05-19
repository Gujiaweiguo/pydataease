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

    # BUG-034 fix: Check if DB user is already cached by middleware
    cached_db_user = getattr(request.state, "_db_user", None)
    if cached_db_user is not None:
        return TokenUser(user_id=user.user_id, oid=user.oid, language=getattr(cached_db_user, "language", None) or "zh-CN")

    db_user = await UserRepository(session).get_by_id(user.user_id)
    if db_user is None or not db_user.enable:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is disabled")
    request.state._db_user = db_user  # Cache for reuse
    return TokenUser(user_id=db_user.id, oid=user.oid, language=db_user.language or "zh-CN")


async def get_optional_user(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> TokenUser | None:
    user = cast(TokenUser | None, getattr(request.state, "user", None))
    if user is None:
        return None

    # BUG-034 fix: Check if DB user is already cached by middleware
    cached_db_user = getattr(request.state, "_db_user", None)
    if cached_db_user is not None:
        return TokenUser(user_id=user.user_id, oid=user.oid, language=getattr(cached_db_user, "language", None) or "zh-CN")

    db_user = await UserRepository(session).get_by_id(user.user_id)
    if db_user is None or not db_user.enable:
        return None
    request.state._db_user = db_user  # Cache for reuse
    return TokenUser(user_id=db_user.id, oid=user.oid, language=db_user.language or "zh-CN")
