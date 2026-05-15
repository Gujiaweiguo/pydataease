from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.column_permission import (
    ColumnPermissionCreateRequest,
    ColumnPermissionListRequest,
    ColumnPermissionResponse,
    ColumnPermissionUpdateRequest,
)
from app.services.column_permission_service import ColumnPermissionService, get_column_permission_service

router = APIRouter(tags=["columnPermission"])


@router.post("/columnPermission/list")
async def list_column_permissions(
    payload: ColumnPermissionListRequest,
    user: TokenUser = Depends(get_current_user),
    service: ColumnPermissionService = Depends(get_column_permission_service),
) -> list[ColumnPermissionResponse]:
    return await service.list_rules(payload, user)


@router.post("/columnPermission/create")
async def create_column_permission(
    payload: ColumnPermissionCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: ColumnPermissionService = Depends(get_column_permission_service),
) -> ColumnPermissionResponse:
    return await service.create_rule(payload, user)


@router.post("/columnPermission/edit")
async def edit_column_permission(
    payload: ColumnPermissionUpdateRequest,
    user: TokenUser = Depends(get_current_user),
    service: ColumnPermissionService = Depends(get_column_permission_service),
) -> ColumnPermissionResponse:
    return await service.update_rule(payload, user)


@router.post("/columnPermission/delete/{rule_id}")
async def delete_column_permission(
    rule_id: int,
    user: TokenUser = Depends(get_current_user),
    service: ColumnPermissionService = Depends(get_column_permission_service),
) -> None:
    await service.delete_rule(rule_id, user)
