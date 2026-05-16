from __future__ import annotations

from typing import final

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.custom_geo import CustomGeoArea, CustomGeoSubArea


@final
class CustomGeoAreaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[CustomGeoArea]:
        result = await self.session.execute(select(CustomGeoArea))
        return list(result.scalars().all())

    async def get_by_id(self, area_id: str) -> CustomGeoArea | None:
        return await self.session.get(CustomGeoArea, area_id)

    async def create(self, payload: dict[str, object]) -> CustomGeoArea:
        entity = CustomGeoArea(**payload)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: CustomGeoArea, payload: dict[str, object]) -> CustomGeoArea:
        for key, value in payload.items():
            setattr(entity, key, value)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: CustomGeoArea) -> None:
        await self.session.delete(entity)
        await self.session.commit()


@final
class CustomGeoSubAreaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_geo_area_id(self, geo_area_id: str) -> list[CustomGeoSubArea]:
        result = await self.session.execute(
            select(CustomGeoSubArea).where(CustomGeoSubArea.geo_area_id == geo_area_id)
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[CustomGeoSubArea]:
        result = await self.session.execute(select(CustomGeoSubArea))
        return list(result.scalars().all())

    async def get_by_id(self, sub_area_id: int) -> CustomGeoSubArea | None:
        return await self.session.get(CustomGeoSubArea, sub_area_id)

    async def create(self, payload: dict[str, object]) -> CustomGeoSubArea:
        entity = CustomGeoSubArea(**payload)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: CustomGeoSubArea, payload: dict[str, object]) -> CustomGeoSubArea:
        for key, value in payload.items():
            setattr(entity, key, value)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: CustomGeoSubArea) -> None:
        await self.session.delete(entity)
        await self.session.commit()

    async def delete_by_geo_area_id(self, geo_area_id: str) -> None:
        await self.session.execute(
            delete(CustomGeoSubArea).where(CustomGeoSubArea.geo_area_id == geo_area_id)
        )
        await self.session.commit()
