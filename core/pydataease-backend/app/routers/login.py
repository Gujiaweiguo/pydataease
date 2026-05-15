from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.repositories.org_repo import OrgRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenUser
from app.schemas.login import LoginRequest
from app.services.auth_service import AuthService, get_auth_service
from app.settings.config import get_settings
from app.utils.password_utils import derive_jwt_secret

router = APIRouter(tags=["login"])


@router.post("/login/localLogin")
@limiter.limit("5/minute")
async def local_login(
    request: Request,
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> object:
    return await service.login(payload)


@router.get("/login/refresh")
async def refresh_token(
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> object:
    token = request.headers.get("X-DE-TOKEN") or request.headers.get("X-EMBEDDED-TOKEN")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token is empty")

    try:
        claims = jwt.get_unverified_claims(token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token is invalid") from exc

    user_id = claims.get("uid")
    oid = claims.get("oid")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token格式错误！")

    db_user = await service.user_repo.get_by_id(int(user_id))
    if db_user is None or not db_user.enable:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")

    try:
        jwt.decode(
            token,
            derive_jwt_secret(db_user.password),
            algorithms=[get_settings().jwt_algorithm],
            options={"verify_exp": False},
        )
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token is invalid") from exc

    return await service.refresh_with_org(db_user.id, int(oid) if oid is not None else None)


@router.get("/logout")
async def logout(_: TokenUser = Depends(get_current_user)) -> None:
    return None


@router.get("/dekey")
async def get_dekey(service: AuthService = Depends(get_auth_service)) -> object:
    return await service.get_dekey()


@router.get("/user/ipInfo")
async def get_user_ip_info() -> dict[str, object]:
    return {"data": {"ip": "127.0.0.1", "location": "local"}}


@router.get("/user/info")
async def get_user_info(
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    repo = UserRepository(session)
    org_repo = OrgRepository(session)
    db_user = await repo.get_by_id(user.user_id)
    if db_user is None:
        raise HTTPException(status_code=401, detail="User not found")
    current_org = await org_repo.get_by_id(user.oid) if user.oid > 0 else None
    user_orgs = await org_repo.get_user_orgs(user.user_id)
    return {
        "id": db_user.id,
        "name": db_user.name,
        "account": db_user.account,
        "oid": user.oid,
        "language": db_user.language or "zh-CN",
        "enable": db_user.enable,
        "currentOrg": None if current_org is None else {"id": current_org.id, "name": current_org.name},
        "orgList": [{"id": org.id, "name": org.name, "pid": org.pid or 0} for org in user_orgs],
    }


@router.post("/user/switch/{oid}")
async def switch_user_org(
    oid: int,
    user: TokenUser = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> object:
    return await service.switch_org(user, oid)
