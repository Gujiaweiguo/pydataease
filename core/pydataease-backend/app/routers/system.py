from __future__ import annotations

# pyright: reportMissingImports=false

import time

from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.bigint_json import BigIntJSONResponse  # pyright: ignore[reportImplicitRelativeImport]

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.system import OnlineMapSaveRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.services.menu_service import MenuService, get_menu_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.sys_setting_service import SysSettingService, get_sys_setting_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.system_service import SystemService, get_system_service  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.defaults import is_feature_enabled  # pyright: ignore[reportImplicitRelativeImport]

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
    if not await is_feature_enabled(service.session, "feature.adminConfig.enabled"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Feature disabled: admin config")
    await service.save_basic_settings(items)


@router.post("/sysParameter/feature/toggle")
async def toggle_feature_flag(
    payload: dict[str, str | bool],
    _: TokenUser = Depends(get_current_user),
    service: SysSettingService = Depends(get_sys_setting_service),
) -> dict[str, str | bool]:
    key = payload.get("key")
    enabled = payload.get("enabled")

    if not isinstance(key, str) or not key.startswith("feature."):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Feature flag key must start with 'feature.'")
    if not isinstance(enabled, bool):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="'enabled' must be a boolean")

    await service.upsert_setting(key, "true" if enabled else "false", "feature")
    return {"key": key, "enabled": enabled}


@router.post("/sysParameter/appearance/save")
async def save_appearance_settings(
    payload: list[dict[str, str]],
    _: TokenUser = Depends(get_current_user),
    service: SysSettingService = Depends(get_sys_setting_service),
) -> dict[str, str]:
    if not await is_feature_enabled(service.session, "feature.appearance.enabled"):
        return BigIntJSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"code": 1, "data": None, "msg": "feature_disabled"})  # pyright: ignore[reportReturnType]

    for item in payload:
        key = item.get("pkey")
        value = item.get("pval")
        if not isinstance(key, str) or (not key.startswith("ui.") and key != "basic.siteName"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Appearance setting key must start with 'ui.' or equal 'basic.siteName'")
        if not isinstance(value, str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Appearance setting value must be a string")
        await service.upsert_setting(key, value, key.split(".", 1)[0])

    current_cache_version = await service.get_setting("ui.cacheVersion")
    try:
        cache_version = int(current_cache_version or "0") + 1
    except ValueError:
        cache_version = 1
    await service.upsert_setting("ui.cacheVersion", str(cache_version), "ui")
    await service.upsert_setting("ui.updatedAt", str(int(time.time() * 1000)), "ui")
    return {"status": "ok"}


# ── Engine ───────────────────────────────────────────────────────────────────


@router.get("/engine/getEngine")
async def get_engine(
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> dict[str, object]:
    return await service.get_engine()


@router.post("/engine/save")
async def save_engine(
    payload: dict[str, object],
    _: TokenUser = Depends(get_current_user),
    service: SystemService = Depends(get_system_service),
) -> None:
    await service.save_engine(payload)


@router.post("/engine/validate")
async def validate_engine(
    payload: dict[str, object],
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
) -> list[dict[str, object]]:
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
