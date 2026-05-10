from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.datasource import DatasourceCreate, DatasourceUpdate, DatasourceValidateRequest
from app.services.datasource_service import DatasourceService, get_datasource_service

router = APIRouter(prefix="/datasource", tags=["datasource"])


@router.get("/query/{keyWord}")
async def query_datasources(
    keyWord: str,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.query(keyWord)


@router.post("/save")
async def save_datasource(
    payload: DatasourceCreate,
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.save(payload, user)


@router.post("/update")
async def update_datasource(
    payload: DatasourceUpdate,
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.update(payload, user)


@router.post("/validate")
async def validate_datasource(
    payload: DatasourceValidateRequest,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.validate(payload)


@router.get("/getSchema/{datasource_id}")
async def get_schema(
    datasource_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.get_tables(datasource_id)


@router.get("/getTableField/{datasource_id}/{table_name}")
async def get_table_field(
    datasource_id: int,
    table_name: str,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.get_fields(datasource_id, table_name)


@router.post("/delete/{datasource_id}")
async def delete_datasource(
    datasource_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> None:
    await service.delete(datasource_id)
