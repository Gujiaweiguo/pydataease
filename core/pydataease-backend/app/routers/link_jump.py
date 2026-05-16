from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.link_jump import (
    LinkJumpBaseRequest,
    VisualizationLinkJumpDTO,
)
from app.services.link_jump_service import LinkJumpService, get_link_jump_service

router = APIRouter(tags=["linkJump"])


@router.get("/linkJump/getTableFieldWithViewId/{view_id}")
async def get_table_field_with_view_id(
    view_id: int,
    user: TokenUser = Depends(get_current_user),
    service: LinkJumpService = Depends(get_link_jump_service),
) -> list[dict]:
    """Query available jump fields for a chart view."""
    fields = await service.get_table_field_with_view_id(view_id)
    return [f.model_dump(by_alias=True) for f in fields]


@router.get("/linkJump/queryWithViewId/{dv_id}/{view_id}")
async def query_with_view_id(
    dv_id: int,
    view_id: int,
    user: TokenUser = Depends(get_current_user),
    service: LinkJumpService = Depends(get_link_jump_service),
) -> dict | None:
    """Query jump configuration for a specific chart view in a dashboard."""
    result = await service.query_with_view_id(dv_id, view_id, user.user_id)
    if result is None:
        return None
    return result.model_dump(by_alias=True)


@router.get("/linkJump/queryVisualizationJumpInfo/{dv_id}/{resource_table}")
async def query_visualization_jump_info(
    dv_id: int,
    resource_table: str,
    user: TokenUser = Depends(get_current_user),
    service: LinkJumpService = Depends(get_link_jump_service),
) -> dict:
    """Query all jump info for a visualization/dashboard."""
    result = await service.query_visualization_jump_info(
        dv_id, user.user_id, resource_table
    )
    return result.model_dump(by_alias=True)


@router.post("/linkJump/updateJumpSet")
async def update_jump_set(
    jump_dto: VisualizationLinkJumpDTO,
    user: TokenUser = Depends(get_current_user),
    service: LinkJumpService = Depends(get_link_jump_service),
) -> None:
    """Save/update jump configuration."""
    await service.update_jump_set(jump_dto)


@router.post("/linkJump/queryTargetVisualizationJumpInfo")
async def query_target_visualization_jump_info(
    request: LinkJumpBaseRequest,
    user: TokenUser = Depends(get_current_user),
    service: LinkJumpService = Depends(get_link_jump_service),
) -> dict:
    """Query target jump info for a dashboard."""
    result = await service.query_target_visualization_jump_info(request)
    return result.model_dump(by_alias=True)


@router.get("/linkJump/viewTableDetailList/{dv_id}")
async def view_table_detail_list(
    dv_id: int,
    user: TokenUser = Depends(get_current_user),
    service: LinkJumpService = Depends(get_link_jump_service),
) -> dict:
    """Query view table details for jump targets."""
    result = await service.view_table_detail_list(dv_id)
    return result.model_dump(by_alias=True)


@router.post("/linkJump/updateJumpSetActive")
async def update_jump_set_active(
    request: LinkJumpBaseRequest,
    user: TokenUser = Depends(get_current_user),
    service: LinkJumpService = Depends(get_link_jump_service),
) -> dict:
    """Toggle jump set active/inactive."""
    result = await service.update_jump_set_active(request, user.user_id)
    return result.model_dump(by_alias=True)


@router.post("/linkJump/removeJumpSet")
async def remove_jump_set(
    jump_dto: VisualizationLinkJumpDTO,
    user: TokenUser = Depends(get_current_user),
    service: LinkJumpService = Depends(get_link_jump_service),
) -> None:
    """Delete a jump set."""
    await service.remove_jump_set(jump_dto)
