from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser

router = APIRouter(tags=["sync"])


def _empty_page() -> dict[str, Any]:
    return {"items": [], "total": 0}


def _empty_object() -> dict[str, Any]:
    return {}


def _invalid_result() -> dict[str, bool]:
    return {"valid": False}


# --- Sync Datasource ---
@router.post("/sync/datasource/source/pager/{page}/{limit}")
async def sync_ds_source_pager(page: int, limit: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = (page, limit)
    return _empty_page()


@router.post("/sync/datasource/target/pager/{page}/{limit}")
async def sync_ds_target_pager(page: int, limit: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = (page, limit)
    return _empty_page()


@router.post("/sync/datasource/latestUse/{sourceType}")
async def sync_ds_latest_use(sourceType: str, _user: TokenUser = Depends(get_current_user)) -> list[Any]:
    _ = sourceType
    return []


@router.post("/sync/datasource/validate")
async def sync_ds_validate(_user: TokenUser = Depends(get_current_user)) -> dict[str, bool]:
    return _invalid_result()


@router.post("/sync/datasource/getSchema")
async def sync_ds_get_schema(_user: TokenUser = Depends(get_current_user)) -> list[Any]:
    return []


@router.post("/sync/datasource/save")
async def sync_ds_save(_user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    return _empty_object()


@router.get("/sync/datasource/get/{id}")
async def sync_ds_get(id: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = id
    return _empty_object()


@router.post("/sync/datasource/update")
async def sync_ds_update(_user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    return _empty_object()


@router.post("/sync/datasource/delete/{id}")
async def sync_ds_delete(id: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = id
    return _empty_object()


@router.post("/sync/datasource/batchDel")
async def sync_ds_batch_delete(_user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    return _empty_object()


@router.post("/sync/datasource/fields")
async def sync_ds_fields(_user: TokenUser = Depends(get_current_user)) -> list[Any]:
    return []


@router.get("/sync/datasource/validate/{id}")
async def sync_ds_validate_by_id(id: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, bool]:
    _ = id
    return _invalid_result()


# --- Sync Task ---
@router.get("/sync/datasource/list/{type}")
async def sync_ds_list_by_type(type: str, _user: TokenUser = Depends(get_current_user)) -> list[Any]:
    _ = type
    return []


@router.post("/sync/task/pager/{page}/{limit}")
async def sync_task_pager(page: int, limit: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = (page, limit)
    return _empty_page()


@router.get("/sync/task/execute/{id}")
async def sync_task_execute(id: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = id
    return _empty_object()


@router.get("/sync/task/start/{id}")
async def sync_task_start(id: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = id
    return _empty_object()


@router.get("/sync/task/stop/{id}")
async def sync_task_stop(id: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = id
    return _empty_object()


@router.post("/sync/task/add")
async def sync_task_add(_user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    return _empty_object()


@router.post("/sync/task/remove/{taskId}")
async def sync_task_remove(taskId: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = taskId
    return _empty_object()


@router.post("/sync/task/batch/del")
async def sync_task_batch_delete(_user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    return _empty_object()


@router.post("/sync/task/update")
async def sync_task_update(_user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    return _empty_object()


@router.get("/sync/task/get/{taskId}")
async def sync_task_get(taskId: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = taskId
    return _empty_object()


@router.get("/sync/datasource/table/list/{dsId}")
async def sync_ds_table_list(dsId: int, _user: TokenUser = Depends(get_current_user)) -> list[Any]:
    _ = dsId
    return []


# --- Sync Task Log ---
@router.post("/sync/task/log/pager/{current}/{size}")
async def sync_task_log_pager(current: int, size: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = (current, size)
    return _empty_page()


@router.post("/sync/task/log/delete/{logId}")
async def sync_task_log_delete(logId: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = logId
    return _empty_object()


@router.get("/sync/task/log/detail/{logId}/{fromLineNum}")
async def sync_task_log_detail(logId: int, fromLineNum: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = (logId, fromLineNum)
    return {"logContent": "", "end": True}


@router.post("/sync/task/log/clear")
async def sync_task_log_clear(_user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    return _empty_object()


@router.post("/sync/task/log/terminationTask/{logId}")
async def sync_task_log_terminate(logId: int, _user: TokenUser = Depends(get_current_user)) -> dict[str, Any]:
    _ = logId
    return _empty_object()


# --- Sync Summary ---
@router.post("/sync/summary/resourceCount")
async def sync_summary_resource_count(_user: TokenUser = Depends(get_current_user)) -> dict[str, int]:
    return {"taskCount": 0, "sourceCount": 0}


@router.post("/sync/summary/logChartData")
async def sync_summary_log_chart_data(_user: TokenUser = Depends(get_current_user)) -> list[Any]:
    return []
