from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.services.task_service import TaskService, get_task_service

router = APIRouter(prefix="/task", tags=["task"])


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    user: TokenUser = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> object:
    return await service.get_status(task_id, user)


@router.post("/retry/{task_id}")
async def retry_task(
    task_id: str,
    user: TokenUser = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> object:
    return await service.retry_task(task_id, user)


@router.get("/list")
async def list_recent_tasks(
    limit: int = Query(default=20, ge=1, le=100),
    user: TokenUser = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> object:
    return await service.list_recent_tasks(user, limit)
