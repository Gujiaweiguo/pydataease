from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from fastapi.responses import FileResponse

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


@router.post("/exportTasks/records")
async def export_task_records(
    user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> object:
    return await service.list_task_records(user)


@router.post("/exportTasks/{status}/{page}/{limit}")
async def list_export_tasks_paginated(
    status: str,
    page: int,
    limit: int,
    user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> object:
    return await service.list_tasks_paginated(status, page, limit, user)


@router.post("/exportTasks/{export_from}")
async def list_export_tasks(
    export_from: int,
    user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> object:
    return await service.list_tasks(export_from, user)


@router.post("/delete/{task_id}")
async def delete_export_task_get(
    task_id: str,
    _user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> None:
    _ = _user
    await service.delete_task(task_id)


@router.post("/delete")
async def delete_export_tasks_post(
    payload: object = Body(...),
    user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> None:
    ids = payload if isinstance(payload, list) else [str(payload.get("id", ""))] if isinstance(payload, dict) else []
    ids = [str(task_id) for task_id in ids if str(task_id)]
    await service.delete_tasks(ids, user)


@router.post("/deleteAll/{status}")
async def delete_all_export_tasks_by_status(
    status: str,
    payload: object = Body(...),
    user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> None:
    ids = payload if isinstance(payload, list) else []
    ids = [str(task_id) for task_id in ids if str(task_id)]
    await service.delete_all_by_status(status, ids, user)


@router.get("/generateDownloadUri/{task_id}")
async def generate_download_uri(
    task_id: str,
    _user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> object:
    _ = _user
    return await service.generate_download_uri(task_id)


@router.post("/exportLimit")
async def export_limit(
    _user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> bool:
    _ = _user
    return await service.export_limit()


@router.post("/exportTasks/{export_from}/delete")
async def delete_export_task(
    export_from: int,
    payload: dict[str, object],
    _user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> None:
    _ = export_from, _user
    task_id = str(payload.get("id", ""))
    await service.delete_task(task_id)


@router.post("/exportTasks/{export_from}/deleteAll")
async def delete_all_export_tasks(
    export_from: int,
    user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> None:
    await service.delete_all(export_from, user)


@router.post("/retry/{task_id}")
async def retry_export(
    task_id: str,
    user: TokenUser = Depends(get_current_user),
    service: ExportService = Depends(get_export_service),
) -> object:
    return await service.retry_task(task_id)


@router.get("/download/{task_id}")
async def download_export(
    task_id: str,
    user: TokenUser = Depends(get_current_user),  # BUG-050 fix: require auth
    service: ExportService = Depends(get_export_service),
) -> object:
    _ = user
    result = await service.download(task_id)
    if "path" not in result:
        return result
    return FileResponse(
        path=str(result["path"]),
        filename=str(result.get("file_name") or task_id),
        media_type="application/octet-stream",
    )
