from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.user import (
    DefaultPasswordResponse,
    UserByCurrentOrgRequest,
    UserCreateRequest,
    UserDetailResponse,
    UserEditRequest,
    UserEnableRequest,
    UserListItemResponse,
    UserPagerRequest,
    UserPagerResponse,
    UserRoleSelectedRequest,
)
from app.services.user_service import UserService, get_user_service

router = APIRouter(tags=["user"])


@router.post("/user/pager/{page}/{limit}")
async def user_pager(
    page: int,
    limit: int,
    payload: UserPagerRequest | None = None,
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserPagerResponse:
    return await service.pager(page, limit, payload, user)


@router.post("/user/create")
async def create_user(
    payload: UserCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserDetailResponse:
    return await service.create(payload, user)


@router.post("/user/edit")
async def edit_user(
    payload: UserEditRequest,
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserDetailResponse:
    return await service.edit(payload, user)


@router.post("/user/delete/{uid}")
async def delete_user(
    uid: int,
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.delete(uid, user)


@router.post("/user/enable")
async def enable_user(
    payload: UserEnableRequest,
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.enable(payload, user)


@router.post("/user/resetPwd/{uid}")
async def reset_user_password(
    uid: int,
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.reset_password(uid, user)


@router.get("/user/queryById/{uid}")
async def query_user_by_id(
    uid: int,
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserDetailResponse:
    return await service.query_by_id(uid, user)


@router.get("/user/defaultPwd")
async def user_default_password(
    _: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> DefaultPasswordResponse:
    return await service.default_password()


@router.post("/user/role/selected/{page}/{limit}")
async def users_selected_for_role(
    page: int,
    limit: int,
    payload: UserRoleSelectedRequest,
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserPagerResponse:
    return await service.users_in_role(page, limit, payload, user)


@router.post("/user/byCurOrg")
async def users_by_current_org(
    payload: UserByCurrentOrgRequest | None = None,
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> list[UserListItemResponse]:
    return await service.by_current_org(payload, user)
