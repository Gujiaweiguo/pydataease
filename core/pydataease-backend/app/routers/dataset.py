from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.dataset import (
    DatasetGroupCreate,
    DatasetGroupMove,
    DatasetGroupRename,
    DatasetGroupUpdate,
    DatasetTableFieldRequest,
)
from app.services.dataset_service import DatasetService, get_dataset_service

router = APIRouter(tags=["dataset"])


@router.post("/datasetTree/tree")
async def dataset_tree(
    _: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> object:
    return await service.tree()


@router.post("/datasetTree/create")
async def create_dataset(
    payload: DatasetGroupCreate,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> object:
    return await service.create(payload, user)


@router.post("/datasetTree/save")
async def save_dataset(
    payload: DatasetGroupUpdate,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> object:
    return await service.save(payload, user)


@router.post("/datasetTree/rename")
async def rename_dataset(
    payload: DatasetGroupRename,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> object:
    return await service.rename(payload, user)


@router.post("/datasetTree/move")
async def move_dataset(
    payload: DatasetGroupMove,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> object:
    return await service.move(payload, user)


@router.post("/datasetTree/delete/{group_id}")
async def delete_dataset(
    group_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> None:
    await service.delete(group_id)


@router.post("/datasetTree/perDelete/{group_id}")
async def per_delete_dataset(
    group_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> bool:
    return await service.per_delete(group_id)


@router.get("/datasetTree/barInfo/{group_id}")
async def bar_info(
    group_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> object:
    return await service.get_bar_info(group_id)


@router.post("/datasetTree/get/{group_id}")
async def get_dataset(
    group_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> object:
    return await service.get_details(group_id)


@router.post("/datasetTree/details/{group_id}")
async def dataset_details(
    group_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> object:
    return await service.get_details(group_id)


@router.post("/datasetData/tableField")
async def table_field(
    payload: DatasetTableFieldRequest,
    _: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> object:
    return await service.get_fields(payload)


@router.post("/datasetData/previewSql")
async def preview_sql(
    payload: dict[str, object],
    _: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
) -> object:
    sql = str(payload.get("sql", ""))
    return await service.preview_sql_stub(sql)
