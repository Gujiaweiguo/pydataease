from __future__ import annotations

from typing import cast

from fastapi import HTTPException, Request, status

from app.schemas.auth import TokenUser


async def get_current_user(request: Request) -> TokenUser:
    user = cast(TokenUser | None, getattr(request.state, "user", None))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


async def get_optional_user(request: Request) -> TokenUser | None:
    return cast(TokenUser | None, getattr(request.state, "user", None))
