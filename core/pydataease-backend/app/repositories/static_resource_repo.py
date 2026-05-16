from __future__ import annotations

from typing import final

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.static_resource import StaticResource
from app.repositories.base import AsyncBaseRepository


@final
class StaticResourceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, StaticResource)
        self.session = session

    async def get_by_id(self, resource_id: str) -> StaticResource | None:
        return await self.session.get(StaticResource, resource_id)

    async def create(self, payload: dict[str, object]) -> StaticResource:
        return await self._base.create(payload)

    async def update(
        self, entity: StaticResource, payload: dict[str, object]
    ) -> StaticResource:
        return await self._base.update(entity, payload)
