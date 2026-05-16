from __future__ import annotations

import secrets
import time
from typing import final

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.api_key_repo import ApiKeyRepository
from app.schemas.api_key import ApiKeyEnableEditor, ApiKeyResponse
from app.schemas.auth import TokenUser


@final
class ApiKeyService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ApiKeyRepository(session)

    async def generate(self, user: TokenUser) -> dict:
        """Generate new API key pair."""
        ak = secrets.token_urlsafe(16)
        sk = secrets.token_hex(32)
        created = await self.repo.create(
            {
                "id": time.time_ns(),
                "access_key": ak,
                "access_secret": sk,
                "enable": True,
                "create_time": int(time.time() * 1000),
                "creator": user.user_id,
            }
        )
        return ApiKeyResponse.model_validate(created).model_dump(by_alias=True)

    async def query(self, user: TokenUser) -> list[dict]:
        keys = await self.repo.list_by_creator(user.user_id)
        return [
            ApiKeyResponse.model_validate(k).model_dump(by_alias=True)
            for k in keys
        ]

    async def switch_enable(
        self, payload: ApiKeyEnableEditor, user: TokenUser
    ) -> None:
        key = await self.repo.get_by_id(payload.id)
        if key is None:
            raise HTTPException(404, "API key not found")
        if key.creator != user.user_id:
            raise HTTPException(403, "Not your API key")
        await self.repo.update(key, {"enable": payload.enable})

    async def delete_key(self, key_id: int, user: TokenUser) -> None:
        key = await self.repo.get_by_id(key_id)
        if key is None:
            raise HTTPException(404, "API key not found")
        if key.creator != user.user_id:
            raise HTTPException(403, "Not your API key")
        await self.repo.delete(key)


async def get_api_key_service(session: AsyncSession = Depends(get_db)) -> ApiKeyService:
    return ApiKeyService(session)
