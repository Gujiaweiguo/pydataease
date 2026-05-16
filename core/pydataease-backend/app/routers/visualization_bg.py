from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.services.visualization_bg_service import (
    VisualizationBackgroundService,
    get_bg_service,
)

router = APIRouter(tags=["visualization-background"])


@router.get("/visualizationBackground/findAll")
async def find_all_backgrounds(
    user: TokenUser = Depends(get_current_user),
    service: VisualizationBackgroundService = Depends(get_bg_service),
) -> object:
    return await service.find_all_grouped()
