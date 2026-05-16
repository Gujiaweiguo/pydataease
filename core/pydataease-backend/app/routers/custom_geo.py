from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_optional_user
from app.schemas.auth import TokenUser
from app.schemas.custom_geo import CustomGeoAreaCreate, CustomGeoSubAreaCreate
from app.services.custom_geo_service import CustomGeoService, get_custom_geo_service

router = APIRouter(tags=["customGeo"])


@router.get("/customGeo/geoArea/list")
async def list_geo_areas(
    service: CustomGeoService = Depends(get_custom_geo_service),
) -> object:
    return await service.list_areas()


@router.get("/customGeo/geoArea/{area_id}")
async def get_geo_area(
    area_id: str,
    service: CustomGeoService = Depends(get_custom_geo_service),
) -> object:
    return await service.get_area(area_id)


@router.delete("/customGeo/geoArea/{area_id}")
async def delete_geo_area(
    area_id: str,
    service: CustomGeoService = Depends(get_custom_geo_service),
) -> None:
    await service.delete_area(area_id)


@router.post("/customGeo/geoArea/save")
async def save_geo_area(
    payload: CustomGeoAreaCreate,
    user: TokenUser | None = Depends(get_optional_user),
    service: CustomGeoService = Depends(get_custom_geo_service),
) -> object:
    return await service.save_area(payload, user)


@router.delete("/customGeo/geoSubArea/{sub_area_id}")
async def delete_geo_sub_area(
    sub_area_id: int,
    service: CustomGeoService = Depends(get_custom_geo_service),
) -> None:
    await service.delete_sub_area(sub_area_id)


@router.post("/customGeo/geoSubArea/save")
async def save_geo_sub_area(
    payload: CustomGeoSubAreaCreate,
    service: CustomGeoService = Depends(get_custom_geo_service),
) -> object:
    return await service.save_sub_area(payload)


@router.get("/customGeo/geoSubArea/options")
async def list_geo_sub_area_options(
    service: CustomGeoService = Depends(get_custom_geo_service),
) -> object:
    return await service.list_sub_area_options()
