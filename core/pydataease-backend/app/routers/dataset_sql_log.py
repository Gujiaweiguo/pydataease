from __future__ import annotations

# pyright: reportMissingImports=false

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.dataset_sql_log import (  # pyright: ignore[reportImplicitRelativeImport]
    SqlLogCreateRequest,
    SqlLogListRequest,
)
from app.services.dataset_sql_log_service import DatasetSqlLogService, get_dataset_sql_log_service  # pyright: ignore[reportImplicitRelativeImport]

router = APIRouter(tags=["datasetSqlLog"])


@router.post("/datasetTableSqlLog/save")
async def save_sql_log(
    payload: SqlLogCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasetSqlLogService = Depends(get_dataset_sql_log_service),
) -> object:
    result = await service.save(payload, user)
    if hasattr(result, 'model_dump'):
        return result.model_dump(by_alias=True)
    return result


@router.post("/datasetTableSqlLog/listByTableId")
async def list_sql_logs_by_table_id(
    payload: SqlLogListRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasetSqlLogService = Depends(get_dataset_sql_log_service),
) -> object:
    _ = user
    table_id = payload.table_id or ""
    results = await service.list_by_table_id(table_id)
    return [r.model_dump(by_alias=True) if hasattr(r, 'model_dump') else r for r in results]


@router.post("/datasetTableSqlLog/deleteByTableId/{table_id}")
async def delete_sql_logs_by_table_id(
    table_id: str,
    user: TokenUser = Depends(get_current_user),
    service: DatasetSqlLogService = Depends(get_dataset_sql_log_service),
) -> None:
    _ = user
    await service.delete_by_table_id(table_id)
