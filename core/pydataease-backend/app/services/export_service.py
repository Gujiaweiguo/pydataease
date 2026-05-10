from __future__ import annotations

import time
import uuid
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.export_repo import ExportTaskRepository
from app.schemas.auth import TokenUser
from app.schemas.export import ExportTaskCreateRequest, ExportTaskResponse


@final
class ExportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.task_repo = ExportTaskRepository(session)

    async def list_tasks(
        self, export_from: int, user: TokenUser
    ) -> list[ExportTaskResponse]:
        tasks = await self.task_repo.list_by_user_and_from(user.user_id, export_from)
        return [ExportTaskResponse.model_validate(t) for t in tasks]

    async def create_task(
        self, payload: ExportTaskCreateRequest, user: TokenUser
    ) -> ExportTaskResponse:
        task_id = uuid.uuid4().hex
        created = await self.task_repo.create({
            "id": task_id,
            "user_id": user.user_id,
            "file_name": payload.file_name,
            "export_from": payload.export_from,
            "export_from_type": payload.export_from_type,
            "export_status": "INITIATED",
            "export_time": int(time.time() * 1000),
            "export_progress": "0",
            "params": payload.params,
        })
        return ExportTaskResponse.model_validate(created)

    async def delete_task(self, task_id: str) -> None:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Export task not found"
            )
        await self.task_repo.delete_by_id(task_id)

    async def delete_all(self, export_from: int, user: TokenUser) -> None:
        await self.task_repo.delete_all_by_user_and_from(user.user_id, export_from)

    async def download(self, task_id: str) -> dict[str, object]:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Export task not found"
            )
        return {
            "id": task_id,
            "status": task.export_status,
            "msg": "Download stub - not implemented",
        }


async def get_export_service(
    session: AsyncSession = Depends(get_db),
) -> ExportService:
    return ExportService(session)
