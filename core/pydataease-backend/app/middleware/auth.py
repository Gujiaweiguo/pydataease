from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from fastapi import Request, status
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app.middleware.bigint_json import BigIntJSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.dependencies.database import async_session
from app.middleware.whitelist import is_invalid_path, is_whitelisted_path
from app.models.user import CoreUser
from app.repositories.org_repo import OrgRepository
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenUser
from app.schemas.response import ResultMessage
from app.settings.config import BaseConfig, get_settings
from app.utils.password_utils import derive_jwt_secret

TOKEN_HEADER = "X-DE-TOKEN"
LINK_TOKEN_HEADER = "X-DE-LINK-TOKEN"
EMBEDDED_TOKEN_HEADER = "X-EMBEDDED-TOKEN"


class AuthMiddleware:
    app: ASGIApp
    settings: BaseConfig

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.settings = get_settings()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        path = request.url.path

        if is_invalid_path(path):
            response = self._error_response(status.HTTP_401_UNAUTHORIZED, f"Interface address invalid [{path}]")
            await response(scope, receive, send)
            return

        if is_whitelisted_path(path):
            await self.app(scope, receive, send)
            return

        try:
            user = await self._resolve_user(request)
            scope.setdefault("state", {})
            scope["state"]["user"] = user
            await self.app(scope, receive, send)
        except AuthError as exc:
            response = self._error_response(exc.status_code, exc.message)
            await response(scope, receive, send)

    async def _resolve_user(self, request: Request) -> TokenUser:
        headers = request.headers
        link_token = headers.get(LINK_TOKEN_HEADER)
        if link_token:
            claims = self._decode_token(link_token, self.settings.share_secret_key, token_kind="link token")
            resource_id = claims.get("resourceId")
            if resource_id is not None:
                request.scope.setdefault("state", {})
                request.scope["state"]["share_resource_id"] = resource_id
            return await self._claims_to_user(claims, link_token=True)

        token = headers.get(TOKEN_HEADER) or headers.get(EMBEDDED_TOKEN_HEADER)
        if not token:
            raise AuthError(status.HTTP_401_UNAUTHORIZED, f"token is empty for uri {{{request.url.path}}}")
        claims = await self._decode_user_token(token)
        return await self._claims_to_user(claims)

    async def _decode_user_token(self, token: str) -> Mapping[str, object]:
        unverified_claims = self._get_unverified_claims(token)
        user_id = unverified_claims.get("uid")
        if user_id is None:
            raise AuthError(status.HTTP_401_UNAUTHORIZED, "token格式错误！")

        user = await self._load_user(_to_int(user_id))
        if user is None or not user.enable:
            raise AuthError(status.HTTP_401_UNAUTHORIZED, "用户不存在或已禁用")

        try:
            return self._decode_token(token, derive_jwt_secret(user.password), token_kind="token")
        except AuthError as exc:
            if exc.message != "token is invalid":
                raise
            return self._decode_token(token, self.settings.secret_key, token_kind="token")

    async def _load_user(self, user_id: int) -> CoreUser | None:
        async with async_session() as session:
            return await self._get_user(session, user_id)

    @staticmethod
    async def _get_user(session: AsyncSession, user_id: int) -> CoreUser | None:
        repo = UserRepository(session)
        return await repo.get_by_id(user_id)

    def _get_unverified_claims(self, token: str) -> Mapping[str, object]:
        if len(token) < 20:
            raise AuthError(status.HTTP_401_UNAUTHORIZED, "token is invalid")
        try:
            claims = jwt.get_unverified_claims(token)
            return cast(Mapping[str, object], claims)
        except JWTError as exc:
            raise AuthError(status.HTTP_401_UNAUTHORIZED, "token is invalid") from exc

    def _decode_token(self, token: str, secret: str, *, token_kind: str) -> Mapping[str, object]:
        if len(token) < 20:
            raise AuthError(status.HTTP_401_UNAUTHORIZED, "token is invalid")
        try:
            claims = jwt.decode(token, secret, algorithms=[self.settings.jwt_algorithm])
            return cast(Mapping[str, object], claims)
        except ExpiredSignatureError as exc:
            raise AuthError(status.HTTP_401_UNAUTHORIZED, f"{token_kind} is expired") from exc
        except JWTError as exc:
            raise AuthError(status.HTTP_401_UNAUTHORIZED, "token is invalid") from exc

    async def _claims_to_user(self, claims: Mapping[str, object], *, link_token: bool = False) -> TokenUser:
        user_id = claims.get("uid")
        oid = claims.get("oid")
        if user_id is None:
            message = "link token格式错误！" if link_token else "token格式错误！"
            raise AuthError(status.HTTP_401_UNAUTHORIZED, message)
        resolved_user_id = _to_int(user_id)
        resolved_oid = _to_int(oid) if oid is not None else 0
        if link_token:
            return TokenUser(user_id=resolved_user_id, oid=resolved_oid)
        validated_oid = await self._validate_org_membership(resolved_user_id, resolved_oid)
        return TokenUser(user_id=resolved_user_id, oid=validated_oid)

    async def _validate_org_membership(self, user_id: int, oid: int) -> int:
        async with async_session() as session:
            org_repo = OrgRepository(session)
            if user_id == 1:
                return oid
            if oid > 0 and await org_repo.is_member(user_id, oid):
                return oid
            user_orgs = await org_repo.get_user_orgs(user_id)
            if user_orgs:
                return user_orgs[0].id
            return 0

    @staticmethod
    def _error_response(status_code: int, message: str) -> Response:
        payload = ResultMessage(code=status_code, data=None, msg=message).model_dump()
        return BigIntJSONResponse(status_code=status_code, content=payload)


class AuthError(Exception):
    status_code: int
    message: str

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def _to_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        raise AuthError(status.HTTP_401_UNAUTHORIZED, "token is invalid")
    return int(value)
