from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.system import OnlineMapSaveRequest
from app.services.system_service import SystemService, get_system_service

router = APIRouter(tags=["system"])


@router.get("/sysParameter/queryOnlineMap")
async def query_online_map(
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.query_online_map()


@router.post("/sysParameter/saveOnlineMap")
async def save_online_map(
    payload: OnlineMapSaveRequest,
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.save_online_map(payload.key)


@router.get("/sysParameter/requestTimeOut")
async def request_timeout(
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.request_timeout()


@router.get("/menu/query")
async def query_menus(
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.query_menus()


@router.get("/font/listFont")
async def list_fonts(
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.list_fonts()


@router.get("/font/defaultFont")
async def default_font(
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.default_font()


@router.get("/map/areaEntitys/{pcode}")
async def get_area_entities(
    pcode: str,
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.get_area_entities(pcode)
