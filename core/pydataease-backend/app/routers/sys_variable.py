from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.dependencies.permission import require_menu_permission
from app.schemas.auth import TokenUser
from app.schemas.sys_variable import (
    SysVariableCreateRequest,
    SysVariableEditRequest,
    SysVariableQueryRequest,
    SysVariableValueBatchDeleteRequest,
    SysVariableValueCreateRequest,
    SysVariableValueEditRequest,
    SysVariableValuePageRequest,
)
from app.services.sys_variable_service import SysVariableService, get_sys_variable_service
from app.settings.defaults import is_feature_enabled

router = APIRouter(tags=["sysVariable"])

_SYS_VAR_PERM = require_menu_permission("menu:sys-variable:use")


async def _check_feature(session: AsyncSession = Depends(get_db)) -> None:
    if not await is_feature_enabled(session, "feature.sysVariableContract.enabled"):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Feature disabled: system variables")


@router.post("/sysVariable/create")
async def create_variable(
    payload: SysVariableCreateRequest,
    _menu: None = Depends(_SYS_VAR_PERM),
    user: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
    _f=Depends(_check_feature),
) -> object:
    return await service.create(payload, user)


@router.post("/sysVariable/edit")
async def edit_variable(
    payload: SysVariableEditRequest,
    _menu: None = Depends(_SYS_VAR_PERM),
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
    _f=Depends(_check_feature),
) -> object:
    return await service.edit(payload)


@router.get("/sysVariable/detail/{id}")
async def variable_detail(
    id: int,
    _menu: None = Depends(_SYS_VAR_PERM),
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
    _f=Depends(_check_feature),
) -> object:
    return await service.detail(id)


@router.get("/sysVariable/delete/{id}")
async def delete_variable(
    id: int,
    _menu: None = Depends(_SYS_VAR_PERM),
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
    _f=Depends(_check_feature),
) -> None:
    await service.delete(id)
    return None


@router.post("/sysVariable/query")
async def query_variable(
    payload: SysVariableQueryRequest | None = None,
    _menu: None = Depends(_SYS_VAR_PERM),
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
    _f=Depends(_check_feature),
) -> object:
    return await service.query(payload)


@router.post("/sysVariable/value/selected/{page}/{limit}")
async def select_variable_values_page(
    page: int,
    limit: int,
    payload: SysVariableValuePageRequest | None = None,
    _menu: None = Depends(_SYS_VAR_PERM),
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
    _f=Depends(_check_feature),
) -> object:
    return await service.value_page(page, limit, payload)


@router.get("/sysVariable/value/selected/{id}")
async def select_variable_values(
    id: int,
    _menu: None = Depends(_SYS_VAR_PERM),
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
    _f=Depends(_check_feature),
) -> object:
    return await service.value_list(id)


@router.post("/sysVariable/value/create")
async def create_variable_value(
    payload: SysVariableValueCreateRequest,
    _menu: None = Depends(_SYS_VAR_PERM),
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
    _f=Depends(_check_feature),
) -> object:
    return await service.create_value(payload)


@router.post("/sysVariable/value/edit")
async def edit_variable_value(
    payload: SysVariableValueEditRequest,
    _menu: None = Depends(_SYS_VAR_PERM),
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
    _f=Depends(_check_feature),
) -> object:
    return await service.edit_value(payload)


@router.get("/sysVariable/value/delete/{id}")
async def delete_variable_value(
    id: int,
    _menu: None = Depends(_SYS_VAR_PERM),
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
    _f=Depends(_check_feature),
) -> None:
    await service.delete_value(id)
    return None


@router.post("/sysVariable/value/batchDel")
async def batch_delete_variable_values(
    payload: SysVariableValueBatchDeleteRequest,
    _menu: None = Depends(_SYS_VAR_PERM),
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
    _f=Depends(_check_feature),
) -> None:
    await service.batch_delete_values(payload)
    return None
