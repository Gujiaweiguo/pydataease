from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.visualization import (
    JumpRequest,
    LinkageRequest,
    OuterParamsRequest,
    StoreCreateRequest,
    StoreFavoritedRequest,
    VisualizationFindByIdRequest,
    VisualizationMoveRequest,
    VisualizationRecentRequest,
    VisualizationRenameRequest,
    VisualizationSaveRequest,
    VisualizationTreeRequest,
    VisualizationUpdateRequest,
)
from app.services.visualization_service import VisualizationService, get_visualization_service

router = APIRouter(tags=["visualization"])


@router.post("/dataVisualization/tree")
async def visualization_tree(
    payload: VisualizationTreeRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.tree(payload)


@router.post("/dataVisualization/findById")
async def find_visualization_by_id(
    payload: VisualizationFindByIdRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.find_by_id(payload)


@router.post("/dataVisualization/save")
async def save_visualization(
    payload: VisualizationSaveRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.save(payload, user)


@router.post("/dataVisualization/update")
async def update_visualization(
    payload: VisualizationUpdateRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.update(payload, user)


@router.post("/dataVisualization/delete")
async def delete_visualization(
    payload: dict[str, int],
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.delete(int(payload["id"]), user)


@router.post("/dataVisualization/move")
async def move_visualization(
    payload: VisualizationMoveRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.move(payload, user)


@router.post("/dataVisualization/reName")
async def rename_visualization(
    payload: VisualizationRenameRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.rename(payload, user)


@router.post("/dataVisualization/findRecent")
async def find_recent_visualizations(
    payload: VisualizationRecentRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.find_recent(payload)


@router.get("/dataVisualization/perResource/{visualization_id}")
async def get_visualization_per_resource(
    visualization_id: int,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.per_resource(visualization_id)


@router.get("/dataVisualization/viewDetailList/{visualization_id}")
async def view_detail_list(
    visualization_id: int,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.view_detail_list(visualization_id)


@router.post("/store/favorited")
async def store_favorited(
    payload: StoreFavoritedRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.favorited(payload.resource_id, payload.resource_type, user)


@router.get("/store/favorited/{resource_id}")
async def store_favorited_legacy(
    resource_id: int,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.favorited(resource_id, 0, user)


@router.post("/store/query")
async def query_stores(
    payload: dict,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.query_stores(
        user,
        keyword=payload.get("keyword"),
        type_filter=payload.get("type"),
        asc=payload.get("asc"),
    )


@router.post("/store/{resource_id}")
async def add_store(
    resource_id: int,
    payload: StoreCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.add_store(resource_id, payload.resource_type, user)


@router.post("/store/del/{resource_id}")
async def remove_store(
    resource_id: int,
    payload: StoreCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.remove_store(resource_id, payload.resource_type, user)


@router.post("/linkage/getViewLinkageGather")
async def get_view_linkage_gather(
    payload: LinkageRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.get_view_linkage_gather(payload)


@router.post("/linkage/getViewLinkageGatherArray")
async def get_view_linkage_gather_array(
    payload: LinkageRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.get_view_linkage_gather_array(payload)


@router.post("/linkage/saveLinkage")
async def save_linkage(
    payload: LinkageRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.save_linkage(payload)


@router.get("/linkage/getVisualizationAllLinkageInfo/{dv_id}/{resource_table}")
async def get_visualization_all_linkage_info(
    dv_id: int,
    resource_table: str,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.get_visualization_all_linkage_info(dv_id, resource_table)


@router.post("/linkage/updateLinkageActive")
async def update_linkage_active(
    payload: LinkageRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.update_linkage_active(payload)


@router.post("/linkage/removeLinkage")
async def remove_linkage(
    payload: LinkageRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.remove_linkage(payload)


@router.get("/linkJump/getTableFieldWithViewId/{view_id}")
async def get_table_field_with_view_id(
    view_id: int,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.get_table_field_with_view_id(view_id)


@router.get("/linkJump/queryWithViewId/{dv_id}/{view_id}")
async def query_jump_with_view_id(
    dv_id: int,
    view_id: int,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.query_with_view_id(dv_id, view_id)


@router.post("/linkJump/updateJumpSet")
async def update_jump_set(
    payload: JumpRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.update_jump_set(payload)


@router.post("/linkJump/queryTargetVisualizationJumpInfo")
async def query_target_visualization_jump_info(
    payload: JumpRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.query_target_visualization_jump_info(payload)


@router.get("/linkJump/queryVisualizationJumpInfo/{dv_id}/{resource_table}")
async def query_visualization_jump_info(
    dv_id: int,
    resource_table: str,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.query_visualization_jump_info(dv_id, resource_table)


@router.get("/linkJump/viewTableDetailList/{dv_id}")
async def view_table_detail_list(
    dv_id: int,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.view_detail_list(dv_id)


@router.post("/linkJump/updateJumpSetActive")
async def update_jump_set_active(
    payload: JumpRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.update_jump_set_active(payload)


@router.post("/linkJump/removeJumpSet")
async def remove_jump_set(
    payload: JumpRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.remove_jump_set(payload)


@router.get("/outerParams/queryWithVisualizationId/{dv_id}")
async def query_with_visualization_id(
    dv_id: int,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.query_with_visualization_id(dv_id)


@router.post("/outerParams/updateOuterParamsSet")
async def update_outer_params_set(
    payload: OuterParamsRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.update_outer_params_set(payload)


@router.get("/outerParams/getOuterParamsInfo/{dv_id}")
async def get_outer_params_info(
    dv_id: int,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.get_outer_params_info(dv_id)


@router.post("/watermark/save")
async def save_watermark(
    payload: dict,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.save_watermark(payload)


@router.get("/outerParams/queryDsWithVisualizationId/{dv_id}")
async def query_ds_with_visualization_id(
    dv_id: int,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.query_ds_with_visualization_id(dv_id)
