from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.services.datasource_service import DatasourceService, get_datasource_service

router = APIRouter(prefix="/engine", tags=["engine"])


@router.get("/info")
async def engine_info(
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.get_engine_info()
