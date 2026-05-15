from __future__ import annotations

import os
from pathlib import Path
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

    async def list_task_records(self, user: TokenUser) -> dict[str, int]:
        return await self.task_repo.count_by_user_grouped_by_status(user.user_id)

    async def list_tasks_paginated(
        self,
        status: str,
        page: int,
        limit: int,
        user: TokenUser,
    ) -> dict[str, object]:
        safe_page = max(page, 1)
        safe_limit = max(limit, 1)
        offset = (safe_page - 1) * safe_limit
        total, tasks = await self.task_repo.list_paginated_by_user_and_status(
            user.user_id,
            status,
            offset,
            safe_limit,
        )
        return {
            "total": total,
            "records": [ExportTaskResponse.model_validate(t).model_dump() for t in tasks],
        }

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

    async def delete_tasks(self, ids: list[str], user: TokenUser) -> None:
        await self.task_repo.delete_by_ids(user.user_id, ids)

    async def delete_all(self, export_from: int, user: TokenUser) -> None:
        await self.task_repo.delete_all_by_user_and_from(user.user_id, export_from)

    async def delete_all_by_status(self, status: str, ids: list[str], user: TokenUser) -> None:
        if ids:
            await self.task_repo.delete_by_ids(user.user_id, ids)
            return
        await self.task_repo.delete_all_by_user_and_status(user.user_id, status)

    async def generate_download_uri(self, task_id: str) -> dict[str, str]:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export task not found",
            )
        return {"uri": f"/de2api/exportCenter/download/{task_id}"}

    async def export_limit(self) -> bool:
        return True

    async def retry_task(self, task_id: str) -> dict[str, object]:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export task not found",
            )
        if task.export_status != "FAILED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Export task cannot be retried",
            )
        task.export_status = "INITIATED"
        task.export_progress = "0"
        task.msg = None
        task.export_time = int(time.time() * 1000)
        await self.session.commit()
        return ExportTaskResponse.model_validate(task).model_dump()

    async def download(self, task_id: str) -> dict[str, object]:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Export task not found"
            )
        if task.export_status != "SUCCESS":
            return {
                "id": task_id,
                "status": task.export_status,
                "msg": task.msg or "Export file is not ready",
            }

        file_name = task.file_name
        if not file_name:
            return {
                "id": task_id,
                "status": task.export_status,
                "msg": "Export file metadata is missing",
            }

        export_dir = Path(os.getenv("DE_EXPORT_DIR", "/tmp/de-exports"))
        file_path = export_dir / Path(file_name).name
        if not file_path.exists() or not file_path.is_file():
            return {
                "id": task_id,
                "status": task.export_status,
                "msg": "Export file not found",
            }

        return {
            "id": task_id,
            "status": task.export_status,
            "path": str(file_path),
            "file_name": Path(file_name).name,
            "file_size": task.file_size,
            "msg": task.msg or "Export task completed",
        }


async def get_export_service(
    session: AsyncSession = Depends(get_db),
) -> ExportService:
    return ExportService(session)
