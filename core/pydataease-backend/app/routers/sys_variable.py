from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
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

router = APIRouter(tags=["sysVariable"])


@router.post("/sysVariable/create")
async def create_variable(
    payload: SysVariableCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
) -> object:
    return await service.create(payload, user)


@router.post("/sysVariable/edit")
async def edit_variable(
    payload: SysVariableEditRequest,
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
) -> object:
    return await service.edit(payload)


@router.get("/sysVariable/detail/{id}")
async def variable_detail(
    id: int,
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
) -> object:
    return await service.detail(id)


@router.get("/sysVariable/delete/{id}")
async def delete_variable(
    id: int,
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
) -> None:
    await service.delete(id)
    return None


@router.post("/sysVariable/query")
async def query_variable(
    payload: SysVariableQueryRequest | None = None,
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
) -> object:
    return await service.query(payload)


@router.post("/sysVariable/value/selected/{page}/{limit}")
async def select_variable_values_page(
    page: int,
    limit: int,
    payload: SysVariableValuePageRequest | None = None,
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
) -> object:
    return await service.value_page(page, limit, payload)


@router.get("/sysVariable/value/selected/{id}")
async def select_variable_values(
    id: int,
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
) -> object:
    return await service.value_list(id)


@router.post("/sysVariable/value/create")
async def create_variable_value(
    payload: SysVariableValueCreateRequest,
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
) -> object:
    return await service.create_value(payload)


@router.post("/sysVariable/value/edit")
async def edit_variable_value(
    payload: SysVariableValueEditRequest,
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
) -> object:
    return await service.edit_value(payload)


@router.get("/sysVariable/value/delete/{id}")
async def delete_variable_value(
    id: int,
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
) -> None:
    await service.delete_value(id)
    return None


@router.post("/sysVariable/value/batchDel")
async def batch_delete_variable_values(
    payload: SysVariableValueBatchDeleteRequest,
    _: TokenUser = Depends(get_current_user),
    service: SysVariableService = Depends(get_sys_variable_service),
) -> None:
    await service.batch_delete_values(payload)
    return None
