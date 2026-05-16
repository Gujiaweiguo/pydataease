from __future__ import annotations

from collections.abc import Sequence
from typing import final

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import XpackApiKey
from app.repositories.base import AsyncBaseRepository


@final
class ApiKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, XpackApiKey)
        self.session = session

    async def list_by_creator(self, creator: int) -> Sequence[XpackApiKey]:
        stmt = select(XpackApiKey).where(XpackApiKey.creator == creator)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, key_id: int) -> XpackApiKey | None:
        return await self._base.get_by_id(key_id)

    async def create(self, payload: dict[str, object]) -> XpackApiKey:
        return await self._base.create(payload)

    async def update(self, entity: XpackApiKey, payload: dict[str, object]) -> XpackApiKey:
        return await self._base.update(entity, payload)

    async def delete(self, entity: XpackApiKey) -> None:
        await self._base.delete(entity)
