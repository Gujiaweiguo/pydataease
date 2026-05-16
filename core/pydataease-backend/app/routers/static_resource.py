from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.static_resource import StaticResourceFindRequest, StaticResourceUploadRequest
from app.services.static_resource_service import (
    StaticResourceService,
    get_static_resource_service,
)

router = APIRouter(tags=["staticResource"])


@router.post("/staticResource/upload/{file_id}")
async def upload_static_resource(
    file_id: str,
    payload: StaticResourceUploadRequest,
    user: TokenUser = Depends(get_current_user),
    service: StaticResourceService = Depends(get_static_resource_service),
) -> object:
    return await service.upload(file_id, payload)


@router.post("/staticResource/findResourceAsBase64")
async def find_resource_as_base64(
    payload: StaticResourceFindRequest,
    user: TokenUser = Depends(get_current_user),
    service: StaticResourceService = Depends(get_static_resource_service),
) -> object:
    return await service.find_as_base64(payload.resource_id)
