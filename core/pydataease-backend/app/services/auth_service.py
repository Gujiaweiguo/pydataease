from __future__ import annotations

from datetime import UTC, datetime

from fastapi import Depends, HTTPException, status
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.login import LoginRequest, TokenResponse
from app.settings.config import get_settings
from app.utils.password_utils import derive_jwt_secret, verify_password
from app.utils.rsa_utils import decrypt_rsa, get_dekey_response


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.settings = get_settings()

    async def login(self, request: LoginRequest) -> TokenResponse:
        account = decrypt_rsa(request.name)
        password = decrypt_rsa(request.pwd)
        user = await self.user_repo.get_by_account(account)
        if user is None or not user.enable or not verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        return self._issue_token(user.id, user.oid or 0, user.password)

    async def refresh(self, user_id: int) -> TokenResponse:
        user = await self.user_repo.get_by_id(user_id)
        if user is None or not user.enable:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
        return self._issue_token(user.id, user.oid or 0, user.password)

    async def get_dekey(self) -> str:
        return get_dekey_response()

    def _issue_token(self, user_id: int, oid: int, password_hash: str) -> TokenResponse:
        now_seconds = int(datetime.now(UTC).timestamp())
        exp_seconds = now_seconds + self.settings.jwt_exp_seconds
        token = jwt.encode(
            {"uid": user_id, "oid": oid, "exp": exp_seconds},
            derive_jwt_secret(password_hash),
            algorithm=self.settings.jwt_algorithm,
        )
        return TokenResponse(token=token, exp=exp_seconds * 1000)


async def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(session)
