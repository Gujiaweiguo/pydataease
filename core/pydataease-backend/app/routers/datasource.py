from __future__ import annotations

import base64
import json

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.datasource import (
    DatasourceCreate,
    DatasourceUpdate,
    DatasourceValidateRequest,
    DatasourceValidateResponse,
)
from app.services.datasource_service import DatasourceService, get_datasource_service
from app.services.permission_service import PermissionService, get_permission_service


def _decode_configuration(payload: dict) -> dict:
    """Decode Base64-encoded configuration string to a dict, if needed."""
    config_raw = payload.get("configuration")
    if isinstance(config_raw, str):
        payload["configuration"] = json.loads(base64.b64decode(config_raw).decode())
    return payload

router = APIRouter(prefix="/datasource", tags=["datasource"])


@router.post("/tree")
async def datasource_tree(
    payload: dict | None = None,
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "datasource", "use")
    return await service.tree()


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
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "datasource", "manage")
    return await service.save(payload, user)


@router.post("/update")
async def update_datasource(
    payload: DatasourceUpdate,
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "datasource", "manage")
    return await service.update(payload, user)


@router.post("/validate")
async def validate_datasource(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> DatasourceValidateResponse:
    decoded = _decode_configuration(payload)
    typed = DatasourceValidateRequest(**decoded)
    return await service.validate(typed)


@router.post("/getSchema")
async def get_schema_from_config(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> list[str]:
    decoded = _decode_configuration(payload)
    configuration = decoded.get("configuration", {})
    if not isinstance(configuration, dict):
        configuration = {}
    return await service.get_schemas_from_config(configuration)


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


@router.post("/uploadFile")
async def upload_datasource_file(
    file: UploadFile = File(...),
    id: str = Form(None),
    editType: str = Form(None),
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.upload_file(file, id, editType)


@router.post("/delete/{datasource_id}")
async def delete_datasource(
    datasource_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
    perm: PermissionService = Depends(get_permission_service),
) -> None:
    await perm.require_resource_access(user, "datasource", "manage")
    await service.delete(datasource_id)


@router.post("/latestUse")
async def latest_use(
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> list[str]:
    return await service.latest_use()
