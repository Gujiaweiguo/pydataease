from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.embed_control_service import EmbedControlService, get_embed_control_service

router = APIRouter(tags=["embed-control"])


@router.get("/embed-control/list")
async def list_configs(
    user: TokenUser = Depends(get_current_user),
    service: EmbedControlService = Depends(get_embed_control_service),
) -> list[dict]:
    """List all embed configurations. Admin only."""
    return await service.list_configs()


@router.get("/embed-control/{resource_type}")
async def get_config(
    resource_type: str,
    user: TokenUser = Depends(get_current_user),
    service: EmbedControlService = Depends(get_embed_control_service),
) -> dict:
    """Get embed config for a resource type. Admin only."""
    result = await service.get_config(resource_type)
    if result is None:
        raise HTTPException(status_code=404, detail="Embed config not found")
    return result


@router.put("/embed-control/{resource_type}")
async def update_config(
    resource_type: str,
    payload: dict,
    user: TokenUser = Depends(get_current_user),
    service: EmbedControlService = Depends(get_embed_control_service),
) -> dict:
    """Update embed config for a resource type. Admin only."""
    result = await service.update_config(resource_type, payload)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.get("/embed-control/{resource_type}/check")
async def check_embed_allowed(
    resource_type: str,
    domain: str | None = None,
    service: EmbedControlService = Depends(get_embed_control_service),
) -> dict:
    """Check if embedding is allowed for this resource type. Public endpoint."""
    allowed = await service.is_embed_allowed(resource_type, domain)
    return {"allowed": allowed, "resourceType": resource_type}
