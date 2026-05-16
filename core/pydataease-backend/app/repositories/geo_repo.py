from __future__ import annotations

from typing import final

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geo import MapGeo
from app.repositories.base import AsyncBaseRepository


@final
class GeoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._base = AsyncBaseRepository(session, MapGeo)
        self.session = session

    async def get_by_id(self, geo_id: str) -> MapGeo | None:
        return await self.session.get(MapGeo, geo_id)

    async def create(self, payload: dict[str, object]) -> MapGeo:
        return await self._base.create(payload)

    async def update(
        self, entity: MapGeo, payload: dict[str, object]
    ) -> MapGeo:
        return await self._base.update(entity, payload)

    async def delete(self, entity: MapGeo) -> None:
        await self._base.delete(entity)
