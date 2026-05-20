from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.auth_permission import (
    BusiPerEditor,
    BusiPermissionRequest,
    BusiTargetPerCreator,
    MenuPerEditor,
    MenuPermissionRequest,
    MenuTargetPerCreator,
    PermissionVO,
    ResourceVO,
)
from app.services.auth_permission_service import AuthPermissionService, get_auth_permission_service

router = APIRouter(tags=["auth"])


@router.get("/auth/menuResource")
async def menu_resource(
    user: TokenUser = Depends(get_current_user),
    service: AuthPermissionService = Depends(get_auth_permission_service),
) -> list[ResourceVO]:
    return await service.get_menu_resource_tree(user)


@router.get("/auth/busiResource/{flag}")
async def busi_resource(
    flag: str,
    user: TokenUser = Depends(get_current_user),
    service: AuthPermissionService = Depends(get_auth_permission_service),
) -> list[ResourceVO]:
    return await service.get_busi_resource_tree(flag, user)


@router.post("/auth/busiPermission")
async def busi_permission(
    payload: BusiPermissionRequest,
    user: TokenUser = Depends(get_current_user),
    service: AuthPermissionService = Depends(get_auth_permission_service),
) -> PermissionVO:
    return await service.get_busi_permission(payload, user)


@router.post("/auth/menuPermission")
async def menu_permission(
    payload: MenuPermissionRequest,
    user: TokenUser = Depends(get_current_user),
    service: AuthPermissionService = Depends(get_auth_permission_service),
) -> PermissionVO:
    return await service.get_menu_permission(payload, user)


@router.post("/auth/saveBusiPer")
async def save_busi_per(
    payload: BusiPerEditor,
    user: TokenUser = Depends(get_current_user),
    service: AuthPermissionService = Depends(get_auth_permission_service),
) -> None:
    await service.save_busi_per(payload, user)


@router.post("/auth/saveMenuPer")
async def save_menu_per(
    payload: MenuPerEditor,
    user: TokenUser = Depends(get_current_user),
    service: AuthPermissionService = Depends(get_auth_permission_service),
) -> None:
    await service.save_menu_per(payload, user)


@router.post("/auth/busiTargetPermission")
async def busi_target_permission(
    payload: BusiPermissionRequest,
    user: TokenUser = Depends(get_current_user),
    service: AuthPermissionService = Depends(get_auth_permission_service),
) -> PermissionVO:
    return await service.get_busi_target_permission(payload, user)


@router.post("/auth/menuTargetPermission")
async def menu_target_permission(
    payload: MenuPermissionRequest,
    user: TokenUser = Depends(get_current_user),
    service: AuthPermissionService = Depends(get_auth_permission_service),
) -> PermissionVO:
    return await service.get_menu_target_permission(payload, user)


@router.post("/auth/saveBusiTargetPer")
async def save_busi_target_per(
    payload: BusiTargetPerCreator,
    user: TokenUser = Depends(get_current_user),
    service: AuthPermissionService = Depends(get_auth_permission_service),
) -> None:
    await service.save_busi_target_per(payload, user)


@router.post("/auth/saveMenuTargetPer")
async def save_menu_target_per(
    payload: MenuTargetPerCreator,
    user: TokenUser = Depends(get_current_user),
    service: AuthPermissionService = Depends(get_auth_permission_service),
) -> None:
    await service.save_menu_target_per(payload, user)
