from __future__ import annotations

import time
from typing import final

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.dataset_sql_log_repo import DatasetSqlLogRepository
from app.schemas.dataset_sql_log import SqlLogCreateRequest, SqlLogResponse
from app.schemas.auth import TokenUser


@final
class DatasetSqlLogService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = DatasetSqlLogRepository(session)

    async def save(
        self, payload: SqlLogCreateRequest, user: TokenUser
    ) -> SqlLogResponse:
        now_ns = time.time_ns()
        created = await self.repo.create({
            "id": str(now_ns),
            "table_id": payload.table_id,
            "sql_snapshot": payload.sql_snapshot,
            "table_name": payload.table_name,
            "create_time": now_ns,
            "create_by": str(user.user_id),
            "status": payload.status,
            "error_msg": payload.error_msg,
        })
        return SqlLogResponse.model_validate(created)

    async def list_by_table_id(self, table_id: str) -> list[SqlLogResponse]:
        rows = await self.repo.list_by_table_id(table_id)
        return [SqlLogResponse.model_validate(r) for r in rows]

    async def delete_by_table_id(self, table_id: str) -> None:
        await self.repo.delete_by_table_id(table_id)


async def get_dataset_sql_log_service(
    session: AsyncSession = Depends(get_db),
) -> DatasetSqlLogService:
    return DatasetSqlLogService(session)
