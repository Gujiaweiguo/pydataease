from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.repositories.user_repo import UserRepository
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


@router.get("/user/ipInfo")
async def get_user_ip_info() -> dict:
    return {"data": {"ip": "127.0.0.1", "location": "local"}}


@router.get("/user/info")
async def get_user_info(
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    repo = UserRepository(session)
    db_user = await repo.get_by_id(user.user_id)
    if db_user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return {
        "id": db_user.id,
        "name": db_user.name,
        "account": db_user.account,
        "oid": db_user.oid or 0,
        "language": db_user.language or "zh-CN",
        "enable": db_user.enable,
    }
