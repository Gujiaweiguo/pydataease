from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.chart import ChartDataRequest, ChartSaveRequest, ChartUpdateRequest, ChartViewListRequest
from app.services.chart_service import ChartService, get_chart_service

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
    payload: dict,
    user: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.export_details(payload)


@router.post("/chart/viewDetailList")
async def chart_view_detail_list(
    payload: ChartViewListRequest,
    _: TokenUser = Depends(get_current_user),
    service: ChartService = Depends(get_chart_service),
) -> object:
    return await service.view_detail_list(payload.scene_id)
