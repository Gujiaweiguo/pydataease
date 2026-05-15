from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.row_permission import (
    RowPermissionCreateRequest,
    RowPermissionListRequest,
    RowPermissionResponse,
    RowPermissionUpdateRequest,
)
from app.services.row_permission_service import RowPermissionService, get_row_permission_service

router = APIRouter(tags=["rowPermission"])


@router.post("/rowPermission/list")
async def list_row_permissions(
    payload: RowPermissionListRequest,
    user: TokenUser = Depends(get_current_user),
    service: RowPermissionService = Depends(get_row_permission_service),
) -> list[RowPermissionResponse]:
    return await service.list_rules(payload, user)


@router.post("/rowPermission/create")
async def create_row_permission(
    payload: RowPermissionCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: RowPermissionService = Depends(get_row_permission_service),
) -> RowPermissionResponse:
    return await service.create_rule(payload, user)


@router.post("/rowPermission/edit")
async def edit_row_permission(
    payload: RowPermissionUpdateRequest,
    user: TokenUser = Depends(get_current_user),
    service: RowPermissionService = Depends(get_row_permission_service),
) -> RowPermissionResponse:
    return await service.update_rule(payload, user)


@router.post("/rowPermission/delete/{rule_id}")
async def delete_row_permission(
    rule_id: int,
    user: TokenUser = Depends(get_current_user),
    service: RowPermissionService = Depends(get_row_permission_service),
) -> None:
    await service.delete_rule(rule_id, user)


class WhitelistCreateRequest(BaseModel):
    user_id: int
    dataset_id: int
    scope: str


@router.post("/permissionWhitelist/list")
async def list_whitelist(
    user: TokenUser = Depends(get_current_user),
    service: RowPermissionService = Depends(get_row_permission_service),
) -> list[dict]:
    return await service.list_whitelist(user)


@router.post("/permissionWhitelist/create")
async def create_whitelist(
    payload: WhitelistCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: RowPermissionService = Depends(get_row_permission_service),
) -> dict:
    return await service.add_whitelist(payload.user_id, payload.dataset_id, payload.scope, user)


@router.post("/permissionWhitelist/delete/{whitelist_id}")
async def delete_whitelist(
    whitelist_id: int,
    user: TokenUser = Depends(get_current_user),
    service: RowPermissionService = Depends(get_row_permission_service),
) -> None:
    await service.remove_whitelist(whitelist_id, user)
