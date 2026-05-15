from __future__ import annotations

from datetime import datetime, timezone
from typing import final

from fastapi import Depends, HTTPException, status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.org import CoreOrg
from app.repositories.org_repo import OrgRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenUser
from app.schemas.login import LoginRequest, TokenResponse
from app.settings.config import get_settings
from app.utils.password_utils import derive_jwt_secret, verify_password
from app.utils.rsa_utils import decrypt_rsa, get_dekey_response


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.org_repo = OrgRepository(session)
        self.settings = get_settings()

    @final
    async def login(self, request: LoginRequest) -> TokenResponse:
        account = decrypt_rsa(request.name)
        password = decrypt_rsa(request.pwd)
        user = await self.user_repo.get_by_account(account)
        if user is None or not user.enable or not verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        oid = await self._resolve_current_org_id(user.id, user.oid or 0)
        return self._issue_token(user.id, oid, user.password)

    @final
    async def refresh(self, user_id: int) -> TokenResponse:
        return await self.refresh_with_org(user_id, None)

    @final
    async def refresh_with_org(self, user_id: int, oid: int | None) -> TokenResponse:
        user = await self.user_repo.get_by_id(user_id)
        if user is None or not user.enable:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
        resolved_oid = await self._resolve_current_org_id(user.id, (user.oid or 0) if oid is None else oid)
        return self._issue_token(user.id, resolved_oid, user.password)

    @final
    async def get_dekey(self) -> str:
        return get_dekey_response()

    @final
    async def switch_org(self, user: TokenUser, oid: int) -> TokenResponse:
        db_user = await self.user_repo.get_by_id(user.user_id)
        if db_user is None or not db_user.enable:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
        if user.user_id != 1 and not await self.org_repo.is_member(user.user_id, oid):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not belong to the organization")
        if db_user.oid != oid:
            db_user = await self.user_repo.update(db_user, {"oid": oid})
        return self._issue_token(db_user.id, oid, db_user.password)

    @final
    async def get_user_orgs(self, user_id: int) -> list[CoreOrg]:
        return await self.org_repo.get_user_orgs(user_id)

    async def _resolve_current_org_id(self, user_id: int, oid: int) -> int:
        if oid > 0 and await self.org_repo.is_member(user_id, oid):
            return oid
        user_orgs = await self.org_repo.get_user_orgs(user_id)
        if user_orgs:
            return user_orgs[0].id
        return 0

    def _issue_token(self, user_id: int, oid: int, password_hash: str) -> TokenResponse:
        now_seconds = int(datetime.now(timezone.utc).timestamp())
        exp_seconds = now_seconds + self.settings.jwt_exp_seconds
        token = jwt.encode(
            {"uid": user_id, "oid": oid, "exp": exp_seconds},
            derive_jwt_secret(password_hash),
            algorithm=self.settings.jwt_algorithm,
        )
        return TokenResponse(token=token, exp=exp_seconds * 1000)


async def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(session)
