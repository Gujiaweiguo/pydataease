from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.permission import require_menu_permission
from app.schemas.auth import TokenUser
from app.schemas.role import (
    RoleBeforeUnmountRequest,
    RoleCreateRequest,
    RoleCreateWithPermsRequest,
    RoleDetailResponse,
    RoleEditRequest,
    RoleMountExternalRequest,
    RoleMountRequest,
    RolePermissionDetailResponse,
    RoleQueryRequest,
    RoleResponse,
    RoleSetPermsRequest,
    RoleUnmountRequest,
    RoleUserOptionRequest,
    RoleUserOptionResponse,
)
from app.services.role_service import RoleService, get_role_service

router = APIRouter(tags=["role"])

_ROLE_PERM = require_menu_permission("menu:role-management:use")


@router.post("/role/query")
async def query_roles(
    payload: RoleQueryRequest | None = None,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> list[RoleDetailResponse]:
    return await service.query(payload, user)


@router.post("/role/create")
async def create_role(
    payload: RoleCreateRequest,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> RoleResponse:
    return await service.create(payload, user)


@router.post("/role/edit")
async def edit_role(
    payload: RoleEditRequest,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> RoleResponse:
    return await service.edit(payload, user)


@router.get("/role/detail/{rid}")
async def role_detail(
    rid: int,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> RoleDetailResponse:
    return await service.detail(rid, user)


@router.post("/role/delete/{rid}")
async def delete_role(
    rid: int,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> None:
    await service.delete(rid, user)


@router.post("/role/user/option")
async def role_user_option(
    payload: RoleUserOptionRequest | None = None,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> list[RoleUserOptionResponse]:
    return await service.user_option(payload, user)


@router.get("/role/searchExternalUser/{keyword}")
async def search_external_user(
    keyword: str,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> list[RoleUserOptionResponse]:
    return await service.search_external_user(keyword, user)


@router.post("/role/mountUser")
async def mount_user(
    payload: RoleMountRequest,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> None:
    await service.mount_user(payload, user)


@router.post("/role/beforeUnmountInfo")
async def before_unmount_info(
    payload: RoleBeforeUnmountRequest,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> object:
    return await service.before_unmount_info(payload, user)


@router.post("/role/mountExternalUser")
async def mount_external_user(
    payload: RoleMountExternalRequest,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> object:
    return await service.mount_external_user(payload, user)


@router.post("/role/unMountUser")
async def unmount_user(
    payload: RoleUnmountRequest,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> None:
    await service.unmount_user(payload, user)


@router.post("/role/byCurOrg")
async def roles_by_current_org(
    payload: RoleQueryRequest | None = None,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> list[RoleResponse]:
    return await service.by_org(payload, user)


@router.post("/role/createWithPerms")
async def create_role_with_permissions(
    payload: RoleCreateWithPermsRequest,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> RolePermissionDetailResponse:
    return await service.create_with_permissions(payload, user)


@router.get("/role/permissionDetail/{rid}")
async def role_permission_detail(
    rid: int,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> RolePermissionDetailResponse:
    return await service.get_role_permissions(rid, user)


@router.post("/role/setPerms/{rid}")
async def set_role_permissions(
    rid: int,
    payload: RoleSetPermsRequest,
    _menu: None = Depends(_ROLE_PERM),
    user: TokenUser = Depends(get_current_user),
    service: RoleService = Depends(get_role_service),
) -> RolePermissionDetailResponse:
    return await service.set_role_permissions(rid, payload, user)
