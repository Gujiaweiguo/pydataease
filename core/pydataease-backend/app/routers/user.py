from __future__ import annotations

import io

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, case, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.dependencies.permission import require_menu_permission
from app.models.sys_variable import CoreSysVariable, CoreSysVariableValue
from app.schemas.auth import TokenUser
from app.schemas.auth_permission import UserOrgOptionResponse
from app.schemas.user import (
    PersonEditRequest,
    DefaultPasswordResponse,
    UserBatchDeleteRequest,
    UserByCurrentOrgRequest,
    UserCreateRequest,
    UserDetailResponse,
    UserEditRequest,
    UserEnableRequest,
    UserImportResponse,
    UserListItemResponse,
    UserPagerRequest,
    UserPagerResponse,
    UserRoleSelectedRequest,
    UserSwitchLanguageRequest,
)
from app.services.user_service import UserService, get_user_service

router = APIRouter(tags=["user"])

_USER_MGMT_PERM = require_menu_permission("menu:user-management:use")


@router.post("/user/pager/{page}/{limit}")
async def user_pager(
    page: int,
    limit: int,
    payload: UserPagerRequest | None = None,
    _menu: None = Depends(_USER_MGMT_PERM),
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserPagerResponse:
    return await service.pager(page, limit, payload, user)


@router.post("/user/create")
async def create_user(
    payload: UserCreateRequest,
    _menu: None = Depends(_USER_MGMT_PERM),
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserDetailResponse:
    return await service.create(payload, user)


@router.post("/user/edit")
async def edit_user(
    payload: UserEditRequest,
    _menu: None = Depends(_USER_MGMT_PERM),
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserDetailResponse:
    return await service.edit(payload, user)


@router.get("/user/personInfo")
async def person_info(
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> object:
    return await service.person_info(user)


@router.post("/user/personEdit")
async def person_edit(
    payload: PersonEditRequest,
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> object:
    return await service.person_edit(payload, user)


@router.post("/user/delete/{uid}")
async def delete_user(
    uid: int,
    _menu: None = Depends(_USER_MGMT_PERM),
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.delete(uid, user)


@router.post("/user/enable")
async def enable_user(
    payload: UserEnableRequest,
    _menu: None = Depends(_USER_MGMT_PERM),
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.enable(payload, user)


@router.post("/user/resetPwd/{uid}")
async def reset_user_password(
    uid: int,
    _menu: None = Depends(_USER_MGMT_PERM),
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.reset_password(uid, user)


@router.post("/user/switchLanguage")
async def switch_language(
    payload: UserSwitchLanguageRequest,
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> object:
    return await service.switch_language(payload, user)


@router.get("/user/personSysVariableInfo/{uid}")
async def person_sys_variable_info(
    uid: int,
    _: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    stmt = (
        select(CoreSysVariable.name, CoreSysVariableValue.value)
        .outerjoin(
            CoreSysVariableValue,
            and_(
                CoreSysVariableValue.variable_id == CoreSysVariable.id,
                or_(CoreSysVariableValue.user_id == uid, CoreSysVariableValue.user_id.is_(None)),
            ),
        )
        .order_by(
            CoreSysVariable.id.asc(),
            case((CoreSysVariableValue.user_id.is_not(None), 0), else_=1),
            CoreSysVariableValue.create_time.asc(),
            CoreSysVariableValue.id.asc(),
        )
    )
    result = await session.execute(stmt)

    values: dict[str, object] = {}
    for name, value in result.all():
        if name not in values:
            values[name] = value
    return values


@router.get("/user/queryById/{uid}")
async def query_user_by_id(
    uid: int,
    _menu: None = Depends(_USER_MGMT_PERM),
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
    _menu: None = Depends(_USER_MGMT_PERM),
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserPagerResponse:
    return await service.users_in_role(page, limit, payload, user)


@router.post("/user/byCurOrg")
async def users_by_current_org(
    payload: UserByCurrentOrgRequest | None = None,
    _menu: None = Depends(_USER_MGMT_PERM),
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> list[UserListItemResponse]:
    return await service.by_current_org(payload, user)


@router.post("/user/batchDel")
async def batch_delete(
    payload: UserBatchDeleteRequest,
    _menu: None = Depends(_USER_MGMT_PERM),
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    await service.batch_delete(payload, user)


@router.post("/user/batchImport")
async def batch_import(
    file: UploadFile = File(...),
    _menu: None = Depends(_USER_MGMT_PERM),
    _user: TokenUser = Depends(get_current_user),
) -> UserImportResponse:
    _ = file.filename, _user.user_id
    return UserImportResponse()


@router.post("/user/excelTemplate")
async def excel_template(
    _menu: None = Depends(_USER_MGMT_PERM),
    _: TokenUser = Depends(get_current_user),
) -> StreamingResponse:
    return StreamingResponse(
        io.BytesIO(b""),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=user_import_template.xlsx"},
    )


@router.get("/user/errorRecord/{key}")
async def error_record(
    key: str,
    _menu: None = Depends(_USER_MGMT_PERM),
    _: TokenUser = Depends(get_current_user),
) -> StreamingResponse:
    return StreamingResponse(
        io.BytesIO(b""),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=error_record_{key}.xlsx"},
    )


@router.get("/user/clearErrorRecord/{key}")
async def clear_error_record(
    _key: str,
    _menu: None = Depends(_USER_MGMT_PERM),
    _: TokenUser = Depends(get_current_user),
) -> dict[str, bool]:
    return {"success": True}


@router.get("/user/org/option")
async def user_org_option(
    user: TokenUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> list[UserOrgOptionResponse]:
    return await service.org_option(user)
