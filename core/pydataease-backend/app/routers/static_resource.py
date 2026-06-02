from __future__ import annotations

import base64
import re

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.static_resource import StaticResourceFindRequest, StaticResourceUploadRequest
from app.services.static_resource_service import (
    StaticResourceService,
    get_static_resource_service,
)

router = APIRouter(tags=["staticResource"])

# Matches data URIs: data:<mime>;base64,<payload>
_DATA_URI_RE = re.compile(r"^data:(?P<mime>[^;]+);base64,(?P<payload>.+)$", re.DOTALL)


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


@router.get("/appearance/image/{resource_id}")
async def get_appearance_image(
    resource_id: str,
    service: StaticResourceService = Depends(get_static_resource_service),
) -> Response:
    """Serve an appearance image stored as base64 in static_resource.

    This is a public endpoint (no auth required) because appearance images
    (logos, backgrounds) are visible to all users.
    """
    resource = await service.get_resource_by_id(resource_id)
    if resource is None or not resource.content:
        return Response(status_code=404)

    content = resource.content
    match = _DATA_URI_RE.match(content)
    if match:
        mime_type = match.group("mime")
        payload = match.group("payload")
    else:
        # Assume PNG if no data URI prefix
        mime_type = "image/png"
        payload = content

    try:
        image_bytes = base64.b64decode(payload)
    except Exception:
        return Response(status_code=400)

    return Response(content=image_bytes, media_type=mime_type)
