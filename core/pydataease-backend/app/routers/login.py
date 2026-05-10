from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.login import LoginRequest
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(tags=["login"])


@router.post("/login/localLogin")
async def local_login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> object:
    return await service.login(payload)


@router.get("/login/refresh")
async def refresh_token(
    user: TokenUser = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> object:
    return await service.refresh(user.user_id)


@router.get("/logout")
async def logout(_: TokenUser = Depends(get_current_user)) -> None:
    return None


@router.get("/dekey")
async def get_dekey(service: AuthService = Depends(get_auth_service)) -> object:
    return await service.get_dekey()
