from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user, get_optional_user
from app.schemas.auth import TokenUser
from app.schemas.watermark import WatermarkSaveRequest
from app.services.watermark_service import WatermarkService, get_watermark_service

router = APIRouter(tags=["watermark"])


@router.get("/watermark/find")
async def get_watermark_info(
    user: TokenUser | None = Depends(get_optional_user),
    service: WatermarkService = Depends(get_watermark_service),
) -> object:
    return await service.get_watermark_info()


@router.post("/watermark/save")
async def save_watermark_info(
    payload: WatermarkSaveRequest,
    user: TokenUser = Depends(get_current_user),
    service: WatermarkService = Depends(get_watermark_service),
) -> None:
    await service.save_watermark_info(payload)
