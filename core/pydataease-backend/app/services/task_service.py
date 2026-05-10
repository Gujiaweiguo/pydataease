from __future__ import annotations

from typing import Any
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.export import CoreExportTask
from app.repositories.export_repo import ExportTaskRepository
from app.schemas.auth import TokenUser
from app.schemas.task import TaskRetryResponse, TaskStatusResponse
from app.tasks.export_worker import ExportTaskWorker
from app.tasks.scheduler import get_scheduler, get_task_worker


@final
class TaskService:
    def __init__(
        self,
        session: AsyncSession,
        scheduler: Any,
        worker: ExportTaskWorker,
    ) -> None:
        self.session = session
        self.scheduler = scheduler
        self.worker = worker
        self.task_repo = ExportTaskRepository(session)

    async def get_status(self, task_id: str, user: TokenUser) -> TaskStatusResponse:
        task = await self._get_owned_task(task_id, user.user_id)
        return TaskStatusResponse.model_validate(task)

    async def list_recent_tasks(
        self,
        user: TokenUser,
        limit: int = 20,
    ) -> list[TaskStatusResponse]:
        stmt = (
            select(CoreExportTask)
            .where(CoreExportTask.user_id == user.user_id)
            .order_by(CoreExportTask.export_time.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        tasks = list(result.scalars().all())
        return [TaskStatusResponse.model_validate(task) for task in tasks]

    async def retry_task(self, task_id: str, user: TokenUser) -> TaskRetryResponse:
        task = await self._get_owned_task(task_id, user.user_id)
        if task.export_status != "FAILED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only failed tasks can be retried",
            )
        self.scheduler.add_job(
            self.worker.retry_task,
            trigger="date",
            kwargs={"task_id": task_id},
            id=f"retry-task-{task_id}",
            replace_existing=True,
        )
        return TaskRetryResponse(task_id=task_id, status="INITIATED")

    async def _get_owned_task(self, task_id: str, user_id: int) -> CoreExportTask:
        task = await self.task_repo.get_by_id(task_id)
        if task is None or task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )
        return task


async def get_task_service(
    session: AsyncSession = Depends(get_db),
    scheduler: Any = Depends(get_scheduler),
    worker: ExportTaskWorker = Depends(get_task_worker),
) -> TaskService:
    return TaskService(session, scheduler, worker)
