from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.dataset_sql_log import SqlLogCreateRequest, SqlLogListRequest
from app.services.dataset_sql_log_service import (
    DatasetSqlLogService,
    get_dataset_sql_log_service,
)

router = APIRouter(tags=["datasetSqlLog"])


@router.post("/datasetTableSqlLog/save")
async def save_sql_log(
    payload: SqlLogCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasetSqlLogService = Depends(get_dataset_sql_log_service),
) -> object:
    return await service.save(payload, user)


@router.post("/datasetTableSqlLog/listByTableId")
async def list_sql_logs_by_table_id(
    payload: SqlLogListRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasetSqlLogService = Depends(get_dataset_sql_log_service),
) -> object:
    table_id = payload.table_id or ""
    return await service.list_by_table_id(table_id)


@router.post("/datasetTableSqlLog/deleteByTableId/{table_id}")
async def delete_sql_logs_by_table_id(
    table_id: str,
    user: TokenUser = Depends(get_current_user),
    service: DatasetSqlLogService = Depends(get_dataset_sql_log_service),
) -> None:
    await service.delete_by_table_id(table_id)
