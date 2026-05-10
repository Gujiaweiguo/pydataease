from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.export import ExportTaskCreateRequest
from app.services.export_service import ExportService, get_export_service

router = APIRouter(prefix="/exportCenter", tags=["export"])


@router.post("/exportTasks/create")
async def create_export_task(
    payload: ExportTaskCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> object:
    return await service.create_task(payload, user)


@router.post("/exportTasks/{export_from}")
async def list_export_tasks(
    export_from: int,
    user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> object:
    return await service.list_tasks(export_from, user)


@router.post("/exportTasks/{export_from}/delete")
async def delete_export_task(
    export_from: int,
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> None:
    task_id = str(payload.get("id", ""))
    await service.delete_task(task_id)


@router.post("/exportTasks/{export_from}/deleteAll")
async def delete_all_export_tasks(
    export_from: int,
    user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> None:
    await service.delete_all(export_from, user)


@router.get("/download/{task_id}")
async def download_export(
    task_id: str,
    service: ExportService = Depends(get_export_service),
) -> object:
    return await service.download(task_id)
