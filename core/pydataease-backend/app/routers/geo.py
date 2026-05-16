from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.geo import GeoMappingRequest, GeoSaveRequest
from app.services.geo_service import GeoService, get_geo_service

router = APIRouter(tags=["geo"])


@router.post("/geometry/save")
async def save_geometry(
    payload: GeoSaveRequest,
    user: TokenUser = Depends(get_current_user),
    service: GeoService = Depends(get_geo_service),
) -> object:
    return await service.save_geo(payload)


@router.post("/geometry/delete/{id}")
async def delete_geometry(
    id: str,
    user: TokenUser = Depends(get_current_user),
    service: GeoService = Depends(get_geo_service),
) -> None:
    await service.delete_geo(id)


@router.post("/geometry/{id}/mapping")
async def geometry_mapping(
    id: str,
    payload: GeoMappingRequest,
    user: TokenUser = Depends(get_current_user),
    service: GeoService = Depends(get_geo_service),
) -> object:
    return await service.mapping(id, payload)
