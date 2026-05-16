from __future__ import annotations

from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.geo import MapGeo
from app.repositories.geo_repo import GeoRepository
from app.schemas.geo import GeoMappingRequest, GeoSaveRequest


@final
class GeoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.geo_repo = GeoRepository(session)

    async def save_geo(self, payload: GeoSaveRequest) -> dict:
        """Create or update a geometry record."""
        existing = await self.geo_repo.get_by_id(payload.id)
        if existing is not None:
            update_data: dict[str, object] = {}
            if payload.name is not None:
                update_data["name"] = payload.name
            if payload.geo_json is not None:
                update_data["geo_json"] = payload.geo_json
            updated = await self.geo_repo.update(existing, update_data)
            return _geo_to_dict(updated)

        data: dict[str, object] = {
            "id": payload.id,
            "name": payload.name,
            "geo_json": payload.geo_json,
        }
        geo = await self.geo_repo.create(data)
        return _geo_to_dict(geo)

    async def delete_geo(self, geo_id: str) -> None:
        """Delete geometry record by id."""
        geo = await self.geo_repo.get_by_id(geo_id)
        if geo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Geometry not found",
            )
        await self.geo_repo.delete(geo)

    async def mapping(self, geo_id: str, payload: GeoMappingRequest) -> dict:
        """Map place names to geometry (stub: return mapping as-is)."""
        geo = await self.geo_repo.get_by_id(geo_id)
        if geo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Geometry not found",
            )
        return {"id": geo.id, "name": geo.name, "mapping": payload.mapping}


def _geo_to_dict(geo: MapGeo) -> dict:
    return {
        "id": geo.id,
        "name": geo.name,
        "geoJson": geo.geo_json,
    }


async def get_geo_service(
    session: AsyncSession = Depends(get_db),
) -> GeoService:
    return GeoService(session)
