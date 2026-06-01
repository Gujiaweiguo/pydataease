from __future__ import annotations

# pyright: reportMissingImports=false

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.dataset import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetEnumValueDsRequest,
    DatasetEnumValueRequest,
    DatasetGroupCreate,
    DatasetGroupMove,
    DatasetGroupRename,
    DatasetGroupUpdate,
    DatasetPreviewDataRequest,
    DatasetTableFieldRequest,
)
from app.services.chart_service import ChartService, get_chart_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_service import DatasetService, get_dataset_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.permission_service import PermissionService, get_permission_service  # pyright: ignore[reportImplicitRelativeImport]

router = APIRouter(tags=["dataset"])


@router.post("/datasetTree/tree")
async def dataset_tree(
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "view")
    return await service.tree()


@router.post("/datasetTree/create")
async def create_dataset(
    payload: DatasetGroupCreate,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "manage")
    return await service.create(payload, user)


@router.post("/datasetTree/save")
async def save_dataset(
    payload: DatasetGroupUpdate,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "manage")
    return await service.save(payload, user)


@router.post("/datasetTree/rename")
async def rename_dataset(
    payload: DatasetGroupRename,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "manage")
    return await service.rename(payload, user)


@router.post("/datasetTree/move")
async def move_dataset(
    payload: DatasetGroupMove,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "manage")
    return await service.move(payload, user)


@router.post("/datasetTree/delete/{group_id}")
async def delete_dataset(
    group_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> None:
    await perm.require_resource_access(user, "dataset", "manage")
    await service.delete(group_id)


@router.post("/datasetTree/perDelete/{group_id}")
async def per_delete_dataset(
    group_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> bool:
    await perm.require_resource_access(user, "dataset", "manage")
    return await service.per_delete(group_id)


@router.get("/datasetTree/barInfo/{group_id}")
async def bar_info(
    group_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "view")
    return await service.get_bar_info(group_id)


@router.post("/datasetTree/get/{group_id}")
async def get_dataset(
    group_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "view")
    return await service.get_dataset_preview(group_id, user)


@router.post("/datasetTree/details/{group_id}")
async def dataset_details(
    group_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "use")
    return await service.get_details(group_id)


@router.post("/datasetTree/exportDataset")
async def export_dataset(
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "export")
    return await service.export_dataset(payload)


@router.post("/datasetTree/dsDetails")
async def ds_details(
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "view")
    return await service.ds_details(payload)


@router.post("/datasetTree/detailWithPerm")
async def detail_with_perm(
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "view")
    return await service.ds_details(payload)


@router.post("/datasetData/tableField")
async def table_field(
    payload: DatasetTableFieldRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "view")
    return await service.get_fields(payload)


@router.post("/datasetData/getDatasetTotal")
async def get_dataset_total(
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "view")
    group_id = int(str(payload.get("id", "0")))
    return await service.get_dataset_total(group_id, user)


@router.post("/datasetData/previewSql")
async def preview_sql(
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "view")
    return await service.preview_sql(payload)


@router.post("/datasetData/previewData")
async def preview_data(
    payload: DatasetPreviewDataRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "view")
    return await service.preview_data(payload, user)


@router.post("/datasetData/enumValue")
async def enum_value(
    payload: DatasetEnumValueRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "view")
    return await service.get_enum_values(payload, user)


@router.post("/datasetData/enumValueObj")
async def enum_value_obj(
    payload: DatasetEnumValueRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "use")
    return await service.get_enum_value_objects(payload, user)


@router.post("/datasetData/enumValueDs")
async def enum_value_ds(
    payload: DatasetEnumValueDsRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "use")
    return await service.get_enum_values_from_datasource(payload)


@router.post("/datasetData/getFieldTree")
async def get_field_tree(
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "use")
    group_id = int(str(payload.get("id", "0")))
    return await service.get_field_tree(group_id)


@router.post("/datasetTree/getSqlParams")
async def get_sql_params(
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: DatasetService = Depends(get_dataset_service),
    perm: PermissionService = Depends(get_permission_service),
) -> list[object]:
    await perm.require_resource_access(user, "dataset", "view")
    _ = service
    group_id = payload.get("id") or payload.get("groupId") or payload.get("group_id")
    if group_id is not None:
        int(str(group_id))
    return []


@router.post("/datasetData/innerExportDataSetDetails")
async def inner_export_dataset_details(
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dataset", "export")
    return await service.inner_export_dataset_details(payload)
