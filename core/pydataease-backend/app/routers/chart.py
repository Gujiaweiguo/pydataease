from __future__ import annotations

# pyright: reportMissingImports=false

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.chart import (  # pyright: ignore[reportImplicitRelativeImport]
    ChartDataRequest,
    ChartDrillRequest,
    ChartFieldEnumRequest,
    ChartSaveRequest,
    ChartUpdateRequest,
    ChartViewListRequest,
)
from app.services.chart_service import ChartService, get_chart_service  # pyright: ignore[reportImplicitRelativeImport]

router = APIRouter(tags=["chart"])


@router.get("/chart/{chart_id}")
async def get_chart(
    chart_id: int,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.get_by_id(chart_id)


@router.post("/chart/getChart/{chart_id}")
async def get_chart_legacy(
    chart_id: int,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.get_by_id(chart_id)


@router.post("/chart/save")
async def save_chart(
    payload: ChartSaveRequest,
    user: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.save(payload, user)


@router.post("/chart/update")
async def update_chart(
    payload: ChartUpdateRequest,
    user: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.update(payload, user)


@router.post("/chart/del/{chart_id}")
async def delete_chart(
    chart_id: int,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> None:
    await service.delete(chart_id)


@router.post("/chart/getData")
@router.post("/chartData/getData")
async def get_chart_data(
    payload: ChartDataRequest,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.get_data(payload)


@router.get("/chart/getDetail/{chart_id}")
@router.post("/chart/getDetail/{chart_id}")
async def get_chart_detail(
    chart_id: int,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.get_detail(chart_id)


@router.post("/chartData/innerExportDetails")
async def export_chart_details(
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.export_details(payload)  # pyright: ignore[reportAttributeAccessIssue]


@router.post("/chart/viewDetailList")
async def chart_view_detail_list(
    payload: ChartViewListRequest,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.view_detail_list(payload.scene_id)


@router.post("/chart/listByDQ/{dataset_group_id}/{chart_id}")
async def list_fields_by_dq(
    dataset_group_id: int,
    chart_id: int,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.list_fields_by_dq(dataset_group_id, chart_id)


@router.post("/chart/copyField/{field_id}/{chart_id}")
async def copy_field(
    field_id: int,
    chart_id: int,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.copy_field(field_id, chart_id)


@router.post("/chart/deleteField/{field_id}")
async def delete_field(
    field_id: int,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> None:
    await service.delete_chart_field(field_id)


@router.post("/chart/deleteFieldByChart/{chart_id}")
async def delete_field_by_chart(
    chart_id: int,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> None:
    await service.delete_all_chart_fields(chart_id)


@router.post("/chartData/getFieldData/{field_id}/{field_type}")
async def get_field_data(
    field_id: int,
    field_type: str,
    payload: ChartFieldEnumRequest,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.get_field_enum_data(field_id, field_type, payload)


@router.post("/chartData/getDrillFieldData/{field_id}")
async def get_drill_field_data(
    field_id: int,
    payload: ChartDrillRequest,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.get_drill_field_data(field_id, payload)


@router.get("/chart/checkSameDataSet/{source_view_id}/{target_view_id}")
async def check_same_dataset(
    source_view_id: int,
    target_view_id: int,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> bool:
    return await service.check_same_dataset(source_view_id, target_view_id)
