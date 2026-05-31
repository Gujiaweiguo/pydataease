from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.platform import PlatformBindRequest, PlatformCallbackRequest, PlatformConfigRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.services.platform_service import PlatformService  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.defaults import is_feature_enabled  # pyright: ignore[reportImplicitRelativeImport]

router = APIRouter(tags=["platform"])

SUPPORTED_PLATFORMS = ["wecom", "dingtalk", "lark", "larksuite"]


async def _check_platform(platform: str, session: AsyncSession = Depends(get_db)) -> None:
    if platform not in SUPPORTED_PLATFORMS:
        raise HTTPException(400, f"Unsupported platform: {platform}")
    if not await is_feature_enabled(session, "feature.platformIntegration.enabled"):
        raise HTTPException(403, "Platform integration feature is disabled")


@router.post("/platform/{platform}/save")
async def save_config(
    platform: str,
    payload: PlatformConfigRequest,
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _c: None = Depends(_check_platform),
) -> dict[str, str]:
    _ = user, _c
    await PlatformService(session).save_platform_config(platform, payload.config)
    return {"status": "ok"}


@router.get("/platform/{platform}/config")
async def get_config(
    platform: str,
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _c: None = Depends(_check_platform),
) -> dict[str, str]:
    _ = user, _c
    return await PlatformService(session).get_platform_config(platform)


@router.post("/platform/{platform}/validate")
async def validate_platform(
    platform: str,
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _c: None = Depends(_check_platform),
) -> dict[str, object]:
    _ = user, _c
    return await PlatformService(session).validate_platform(platform)


@router.get("/platform/{platform}/qrinfo")
async def get_qr_info(
    platform: str,
    redirect_uri: str,
    state: str = "default",
    session: AsyncSession = Depends(get_db),
    _c: None = Depends(_check_platform),
) -> dict[str, str]:
    _ = _c
    url = await PlatformService(session).get_qr_url(platform, redirect_uri, state)
    return {"authorizeUrl": url}


@router.post("/platform/{platform}/token")
async def platform_token(
    platform: str,
    payload: PlatformCallbackRequest,
    session: AsyncSession = Depends(get_db),
    _c: None = Depends(_check_platform),
) -> dict[str, object]:
    _ = _c
    return await PlatformService(session).handle_platform_login(platform, payload.code, payload.state or "", payload.redirect_uri or "")


@router.post("/login/platformLogin/{origin}")
async def platform_login_compat(
    origin: str,
    payload: PlatformCallbackRequest,
    session: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    if origin not in SUPPORTED_PLATFORMS:
        raise HTTPException(400, f"Unsupported platform: {origin}")
    if not await is_feature_enabled(session, "feature.platformIntegration.enabled"):
        raise HTTPException(403, "Platform integration feature is disabled")
    return await PlatformService(session).handle_platform_login(origin, payload.code, payload.state or "", payload.redirect_uri or "")


@router.post("/platform/{platform}/bind")
async def bind_platform(
    platform: str,
    payload: PlatformBindRequest,
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _c: None = Depends(_check_platform),
) -> dict[str, str]:
    _ = _c
    redirect_uri = (await PlatformService(session).get_platform_config_raw(platform)).get("callbackDomain", "")
    await PlatformService(session).bind_platform(user.user_id, platform, payload.code, payload.state or "", redirect_uri)
    return {"status": "ok"}


@router.post("/platform/{platform}/unbind")
async def unbind_platform(
    platform: str,
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _c: None = Depends(_check_platform),
) -> dict[str, str]:
    _ = _c
    await PlatformService(session).unbind_platform(user.user_id, platform)
    return {"status": "ok"}


@router.get("/platform/bindings")
async def get_bindings(user: TokenUser = Depends(get_current_user), session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    return await PlatformService(session).get_platform_bindings(user.user_id)
