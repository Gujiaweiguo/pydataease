from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.schemas.auth import TokenUser
from app.schemas.visualization import (
    JumpRequest,
    LinkageRequest,
    OuterParamsRequest,
    StoreCreateRequest,
    StoreFavoritedRequest,
    VisualizationAppCanvasNameCheckRequest,
    VisualizationCanvasChangeRequest,
    VisualizationCanvasRequest,
    VisualizationDeleteLogicRequest,
    VisualizationFindByIdRequest,
    VisualizationMoveRequest,
    VisualizationNameCheckRequest,
    VisualizationPublishStatusRequest,
    VisualizationRecentRequest,
    VisualizationRenameRequest,
    VisualizationSaveRequest,
    VisualizationTreeRequest,
    VisualizationUpdateBaseRequest,
    VisualizationUpdateRequest,
)
from app.services.visualization_service import VisualizationService, get_visualization_service
from app.services.permission_service import PermissionService, get_permission_service

router = APIRouter(tags=["visualization"])


@router.post("/dataVisualization/tree")
async def visualization_tree(
    payload: VisualizationTreeRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dashboard", "use")
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
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dashboard", "manage")
    return await service.save(payload, user)


@router.post("/dataVisualization/saveCanvas")
async def save_canvas(
    payload: VisualizationCanvasRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.save_canvas(payload, user)


@router.post("/dataVisualization/update")
async def update_visualization(
    payload: VisualizationUpdateRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dashboard", "manage")
    return await service.update(payload, user)


@router.post("/dataVisualization/updateCanvas")
async def update_canvas(
    payload: VisualizationCanvasRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.update_canvas(payload, user)


@router.post("/dataVisualization/updateBase")
async def update_base(
    payload: VisualizationUpdateBaseRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.update_base(payload, user)


@router.post("/dataVisualization/updatePublishStatus")
async def update_publish_status(
    payload: VisualizationPublishStatusRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.update_publish_status(payload, user)


@router.post("/dataVisualization/nameCheck")
async def name_check(
    payload: VisualizationNameCheckRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.name_check(payload)


@router.post("/dataVisualization/checkCanvasChange")
async def check_canvas_change(
    payload: VisualizationCanvasChangeRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.check_canvas_change(payload)


@router.post("/dataVisualization/recoverToPublished")
async def recover_to_published(
    payload: VisualizationFindByIdRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.recover_to_published(payload)


@router.post("/dataVisualization/delete")
async def delete_visualization(
    payload: dict[str, int],
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "dashboard", "manage")
    return await service.delete(int(payload["id"]), user)


@router.post("/dataVisualization/deleteLogic/{dv_id}/{busi_flag}")
async def delete_logic(
    dv_id: int,
    busi_flag: str,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.delete_logic(VisualizationDeleteLogicRequest(dv_id=dv_id, busi_flag=busi_flag), user)


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


@router.get("/dataVisualization/findCopyResource/{dv_id}/{busi_flag}")
async def find_copy_resource(
    dv_id: int,
    busi_flag: str,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.find_copy_resource(dv_id, busi_flag)


@router.post("/dataVisualization/appCanvasNameCheck")
async def app_canvas_name_check(
    payload: VisualizationAppCanvasNameCheckRequest,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.app_canvas_name_check(payload)


@router.post("/dataVisualization/decompression")
async def decompression(
    payload: dict[str, object],
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.decompression(payload)


@router.get("/dataVisualization/findDvType/{dv_id}")
async def find_dv_type(
    dv_id: int,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.find_dv_type(dv_id)


@router.get("/dataVisualization/updateCheckVersion/{dv_id}")
async def update_check_version(
    dv_id: int,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.update_check_version(dv_id)


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
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    keyword = payload.get("keyword")
    type_filter = payload.get("type")
    asc = payload.get("asc")
    return await service.query_stores(
        user,
        keyword=keyword if isinstance(keyword, str) else None,
        type_filter=type_filter if isinstance(type_filter, str) else None,
        asc=asc if isinstance(asc, bool) else None,
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
    payload: dict[str, object],
    user: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.save_watermark(payload)


@router.get("/watermark/find")
async def find_watermark(
    _: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> object:
    from app.services.sys_setting_service import SysSettingService

    setting_svc = SysSettingService(session)
    value = await setting_svc.get_setting("watermarkInfo")
    if value:
        return {"settingContent": value}
    return {"settingContent": '{"type":"nick_name","content":"","enable":false}'}


@router.get("/outerParams/queryDsWithVisualizationId/{dv_id}")
async def query_ds_with_visualization_id(
    dv_id: int,
    _: TokenUser = Depends(get_current_user),
    service: VisualizationService = Depends(get_visualization_service),
) -> object:
    return await service.query_ds_with_visualization_id(dv_id)
