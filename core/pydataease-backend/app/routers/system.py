from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.system import OnlineMapSaveRequest
from app.services.menu_service import MenuService, get_menu_service
from app.services.system_service import SystemService, get_system_service

router = APIRouter(tags=["system"])


# ── Online Map ───────────────────────────────────────────────────────────────


@router.get("/sysParameter/queryOnlineMap")
async def query_online_map(
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.query_online_map()


@router.get("/sysParameter/queryOnlineMap/{map_type}")
async def query_online_map_by_type(
    map_type: str,
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.query_online_map_by_type(map_type)


@router.post("/sysParameter/saveOnlineMap")
async def save_online_map(
    payload: OnlineMapSaveRequest,
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.save_online_map(payload.key, payload.map_type, payload.security_code)


# ── Basic Settings ───────────────────────────────────────────────────────────


@router.get("/sysParameter/basic/query")
async def query_basic_settings(
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> list[dict[str, str]]:
    return await service.query_basic_settings()


@router.post("/sysParameter/basic/save")
async def save_basic_settings(
    items: list[dict[str, str]],
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> None:
    await service.save_basic_settings(items)


# ── Engine ───────────────────────────────────────────────────────────────────


@router.get("/engine/getEngine")
async def get_engine(
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> dict[str, object]:
    return await service.get_engine()


@router.post("/engine/save")
async def save_engine(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> None:
    await service.save_engine(payload)


@router.post("/engine/validate")
async def validate_engine(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> None:
    await service.validate_engine(payload)


@router.post("/engine/validate/{engine_id}")
async def validate_engine_by_id(
    engine_id: str,
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> None:
    await service.validate_engine_by_id(engine_id)


# ── Map / Geo ────────────────────────────────────────────────────────────────


@router.get("/map/worldTree")
async def get_world_tree(
    service: SystemService = Depends(get_system_service),
) -> list[dict[str, object]]:
    return await service.get_world_tree()


# ── Misc ─────────────────────────────────────────────────────────────────────


@router.get("/sysParameter/requestTimeOut")
async def request_timeout(
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.request_timeout()


@router.get("/menu/query")
async def query_menus(
    user: TokenUser = Depends(get_current_user),
    service: MenuService = Depends(get_menu_service),
) -> list[dict]:
    tree = await service.get_menu_tree(user)
    return [vo.model_dump() for vo in tree]


@router.get("/map/areaEntitys/{pcode}")
async def get_area_entities(
    pcode: str,
    service: SystemService = Depends(get_system_service),
) -> object:
    return await service.get_area_entities(pcode)


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
