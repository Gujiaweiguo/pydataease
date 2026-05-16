from __future__ import annotations

import time
from typing import final

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.custom_geo_repo import CustomGeoAreaRepository, CustomGeoSubAreaRepository
from app.schemas.custom_geo import (
    CustomGeoAreaCreate,
    CustomGeoAreaResponse,
    CustomGeoSubAreaCreate,
    CustomGeoSubAreaResponse,
)
from app.schemas.auth import TokenUser


@final
class CustomGeoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.area_repo = CustomGeoAreaRepository(session)
        self.sub_area_repo = CustomGeoSubAreaRepository(session)

    async def list_areas(self) -> list[CustomGeoAreaResponse]:
        rows = await self.area_repo.list_all()
        return [CustomGeoAreaResponse.model_validate(a) for a in rows]

    async def get_area(self, area_id: str) -> CustomGeoAreaResponse | None:
        area = await self.area_repo.get_by_id(area_id)
        if area is None:
            return None
        return CustomGeoAreaResponse.model_validate(area)

    async def save_area(
        self, payload: CustomGeoAreaCreate, user: TokenUser | None
    ) -> CustomGeoAreaResponse:
        now_ns = time.time_ns()
        user_id = str(user.user_id) if user else "system"
        if payload.id:
            existing = await self.area_repo.get_by_id(payload.id)
            if existing is not None:
                updated = await self.area_repo.update(existing, {
                    "name": payload.name,
                    "update_by": user_id,
                    "update_time": now_ns,
                })
                return CustomGeoAreaResponse.model_validate(updated)
        area_id = payload.id or str(now_ns)
        created = await self.area_repo.create({
            "id": area_id,
            "name": payload.name,
            "create_by": user_id,
            "create_time": now_ns,
        })
        return CustomGeoAreaResponse.model_validate(created)

    async def delete_area(self, area_id: str) -> None:
        area = await self.area_repo.get_by_id(area_id)
        if area is None:
            return
        await self.sub_area_repo.delete_by_geo_area_id(area_id)
        await self.area_repo.delete(area)

    async def save_sub_area(self, payload: CustomGeoSubAreaCreate) -> CustomGeoSubAreaResponse:
        now_ns = time.time_ns()
        created = await self.sub_area_repo.create({
            "id": now_ns,
            "geo_area_id": payload.geo_area_id,
            "name": payload.name,
            "geo_json": payload.geo_json,
        })
        return CustomGeoSubAreaResponse.model_validate(created)

    async def delete_sub_area(self, sub_area_id: int) -> None:
        sub_area = await self.sub_area_repo.get_by_id(sub_area_id)
        if sub_area is None:
            return
        await self.sub_area_repo.delete(sub_area)

    async def list_sub_area_options(self) -> list[CustomGeoSubAreaResponse]:
        rows = await self.sub_area_repo.list_all()
        return [CustomGeoSubAreaResponse.model_validate(s) for s in rows]


async def get_custom_geo_service(session: AsyncSession = Depends(get_db)) -> CustomGeoService:
    return CustomGeoService(session)
