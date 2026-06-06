from __future__ import annotations

# pyright: reportMissingImports=false

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, get_optional_user  # pyright: ignore[reportImplicitRelativeImport]
from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.dependencies.permission import require_menu_permission  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.watermark import WatermarkSaveRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.defaults import is_feature_enabled  # pyright: ignore[reportImplicitRelativeImport]
from app.services.watermark_service import WatermarkService, get_watermark_service  # pyright: ignore[reportImplicitRelativeImport]

router = APIRouter(tags=["watermark"])

_WATERMARK_PERM = require_menu_permission("menu:watermark:use")


@router.get("/watermark/find")
async def get_watermark_info(
    user: TokenUser | None = Depends(get_optional_user),
    session: AsyncSession = Depends(get_db),
    service: WatermarkService = Depends(get_watermark_service),
) -> object:
    _ = user
    feature_enabled = await is_feature_enabled(session, "feature.watermark.enabled")
    return await service.get_watermark_info(feature_enabled=feature_enabled)


@router.post("/watermark/save")
async def save_watermark_info(
    payload: WatermarkSaveRequest,
    _menu: None = Depends(_WATERMARK_PERM),
    user: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    service: WatermarkService = Depends(get_watermark_service),
) -> None:
    _ = user
    if not await is_feature_enabled(session, "feature.watermark.enabled"):
        raise HTTPException(status_code=403, detail="feature_disabled")
    await service.save_watermark_info(payload)
