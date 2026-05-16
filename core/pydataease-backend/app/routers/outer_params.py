from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.outer_params import VisualizationOuterParamsDTO
from app.services.outer_params_service import OuterParamsService, get_outer_params_service

router = APIRouter(tags=["outerParams"])


@router.get("/outerParams/queryWithVisualizationId/{dv_id}")
async def query_with_visualization_id(
    dv_id: str,
    user: TokenUser = Depends(get_current_user),
    service: OuterParamsService = Depends(get_outer_params_service),
) -> dict | None:
    """Query outer params for a visualization."""
    result = await service.query_with_visualization_id(dv_id)
    if result is None:
        return None
    return result.model_dump(by_alias=True)


@router.post("/outerParams/updateOuterParamsSet")
async def update_outer_params_set(
    dto: VisualizationOuterParamsDTO,
    user: TokenUser = Depends(get_current_user),
    service: OuterParamsService = Depends(get_outer_params_service),
) -> None:
    """Save/update outer params configuration."""
    await service.update_outer_params_set(dto)


@router.get("/outerParams/getOuterParamsInfo/{dv_id}")
async def get_outer_params_info(
    dv_id: str,
    user: TokenUser = Depends(get_current_user),
    service: OuterParamsService = Depends(get_outer_params_service),
) -> dict:
    """Get outer params info mapping."""
    result = await service.get_outer_params_info(dv_id)
    return result.model_dump(by_alias=True)


@router.get("/outerParams/queryDsWithVisualizationId/{dv_id}")
async def query_ds_with_visualization_id(
    dv_id: str,
    user: TokenUser = Depends(get_current_user),
    service: OuterParamsService = Depends(get_outer_params_service),
) -> list[dict]:
    """Query datasets associated with visualization outer params."""
    return await service.query_ds_with_visualization_id(dv_id)
