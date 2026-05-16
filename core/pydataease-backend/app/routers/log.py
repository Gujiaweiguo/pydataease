from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.log import LogGridRequest
from app.services.log_service import LogService, get_log_service

router = APIRouter(tags=["log"])


@router.post("/log/pager/{goPage}/{pageSize}")
async def log_pager(
    goPage: int,
    pageSize: int,
    payload: LogGridRequest,
    user: TokenUser = Depends(get_current_user),
    service: LogService = Depends(get_log_service),
) -> object:
    return await service.pager(goPage, pageSize, payload)


@router.post("/log/export")
async def log_export(
    payload: LogGridRequest,
    user: TokenUser = Depends(get_current_user),
    service: LogService = Depends(get_log_service),
) -> None:
    return await service.export_logs(payload)


@router.get("/log/options")
async def log_options(
    user: TokenUser = Depends(get_current_user),
    service: LogService = Depends(get_log_service),
) -> object:
    return await service.log_options()
