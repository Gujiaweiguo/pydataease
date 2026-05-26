from __future__ import annotations

import base64
import json

from fastapi import APIRouter, Body, Depends, File, Form, UploadFile

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.datasource import (
    DatasourceCreate,
    DatasourceFolderRequest,
    DatasourceMoveRequest,
    DatasourceRenameRequest,
    DatasourceTablesRequest,
    DatasourceUpdate,
    DatasourceValidateRequest,
)
from app.services.datasource_service import DatasourceService, get_datasource_service
from app.services.permission_service import PermissionService, get_permission_service


def _decode_configuration(payload: dict) -> dict:
    """Decode Base64-encoded configuration string to a dict, if needed."""
    config_raw = payload.get("configuration")
    if isinstance(config_raw, str):
        try:
            payload["configuration"] = json.loads(base64.b64decode(config_raw).decode())
        except Exception:
            # Not Base64 — try plain JSON
            try:
                payload["configuration"] = json.loads(config_raw)
            except Exception:
                pass
    return payload


def _decode_if_base64(value: str | None) -> str | None:
    if not value:
        return value
    try:
        return base64.b64decode(value).decode()
    except Exception:
        return value


def _decode_datasource_payload(payload: dict) -> dict:
    decoded = _decode_configuration(payload)
    if decoded.get("id") == "":
        decoded["id"] = None
    if decoded.get("pid") == "":
        decoded["pid"] = 0
    edit_type = decoded.get("editType")
    if edit_type is not None and not isinstance(edit_type, str):
        decoded["editType"] = str(edit_type)
    for key in ("userName", "passwd"):
        raw = decoded.get(key)
        if isinstance(raw, str):
            decoded[key] = _decode_if_base64(raw)
    return decoded

router = APIRouter(prefix="/datasource", tags=["datasource"])

DATASOURCE_TYPES: list[dict[str, str]] = [
    {"type": "folder", "name": "folder", "category": "folder"},
    {"type": "Excel", "name": "Excel", "category": "localfile"},
    {"type": "ExcelRemote", "name": "Excel Remote", "category": "localfile"},
    {"type": "mysql", "name": "MySQL", "category": "oltp"},
    {"type": "mariadb", "name": "MariaDB", "category": "oltp"},
    {"type": "pg", "name": "PostgreSQL", "category": "oltp"},
]


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
    payload: dict,
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "datasource", "manage")
    typed = DatasourceCreate(**_decode_datasource_payload(payload))
    return await service.save(typed, user)


@router.post("/update")
async def update_datasource(
    payload: dict,
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "datasource", "manage")
    typed = DatasourceUpdate(**_decode_datasource_payload(payload))
    return await service.update(typed, user)


@router.post("/validate")
async def validate_datasource(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    decoded = _decode_datasource_payload(payload)
    # Frontend may send only {id} to validate an existing datasource
    if decoded.get("id") and not decoded.get("name"):
        return await service.validate_by_id(int(decoded["id"]))
    typed = DatasourceValidateRequest(**decoded)
    return await service.validate(typed)


@router.post("/getSchema")
async def get_schema_from_config(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> list[str]:
    decoded = _decode_datasource_payload(payload)
    configuration = decoded.get("configuration", {})
    ds_type = decoded.get("type") or decoded.get("dsType") or "postgresql"
    if not isinstance(configuration, dict):
        configuration = {}
    return await service.get_schemas_from_config(configuration, str(ds_type))


@router.get("/getSchema/{datasource_id}")
async def get_schema(
    datasource_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    tables = await service.get_tables(datasource_id)
    return [
        {"name": table.name, "tableName": table.table_name, "schema": table.schema_name, "type": table.type}
        for table in tables
    ]


@router.get("/getTableField/{datasource_id}/{table_name}")
async def get_table_field(
    datasource_id: int,
    table_name: str,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    fields = await service.get_fields(datasource_id, table_name)
    return [f.model_dump(by_alias=True) for f in fields]


@router.post("/getTableField")
async def get_table_field_post(
    payload: dict = Body(...),
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    datasource_id = payload.get("datasourceId") or payload.get("datasource_id")
    table_name = payload.get("tableName") or payload.get("table_name")
    if datasource_id is None or table_name is None:
        return []
    fields = await service.get_fields(int(datasource_id), str(table_name))
    return [f.model_dump(by_alias=True) for f in fields]


@router.post("/uploadFile")
async def upload_datasource_file(
    file: UploadFile = File(...),
    id: str = Form(None),
    editType: str = Form(None),
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.upload_file(file, id, editType)


@router.post("/loadRemoteFile")
async def load_remote_file(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.load_remote_file(_decode_datasource_payload(payload))


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


@router.post("/move")
async def move_datasource(
    payload: DatasourceMoveRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
    perm: PermissionService = Depends(get_permission_service),
) -> None:
    await perm.require_resource_access(user, "datasource", "manage")
    await service.move(payload.id, payload.pid)


@router.post("/reName")
async def rename_datasource(
    payload: DatasourceRenameRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
    perm: PermissionService = Depends(get_permission_service),
) -> None:
    await perm.require_resource_access(user, "datasource", "manage")
    await service.rename(payload.id, payload.name)


@router.get("/types")
async def list_datasource_types(
    _: TokenUser = Depends(get_current_user),
) -> list[dict[str, str]]:
    return DATASOURCE_TYPES


@router.post("/types")
async def list_datasource_types_post(
    _: TokenUser = Depends(get_current_user),
) -> list[dict[str, str]]:
    return DATASOURCE_TYPES


@router.post("/getTables")
async def get_tables(
    payload: DatasourceTablesRequest,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return [t.model_dump(by_alias=True) for t in await service.get_tables(payload.datasource_id)]


@router.post("/getTableStatus")
async def get_table_status(
    payload: DatasourceTablesRequest,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.get_table_status(payload.datasource_id)


@router.get("/validate/{datasource_id}")
async def validate_by_id(
    datasource_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> dict[str, str]:
    return await service.validate_by_id(datasource_id)


@router.get("/get/{datasource_id}")
async def get_datasource(
    datasource_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.get_full(datasource_id)


@router.get("/hidePw/{datasource_id}")
async def get_datasource_hide_pw(
    datasource_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.get_hide_pw(datasource_id)


@router.post("/createFolder")
async def create_folder(
    payload: DatasourceFolderRequest,
    user: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
    perm: PermissionService = Depends(get_permission_service),
) -> object:
    await perm.require_resource_access(user, "datasource", "manage")
    return await service.create_folder(payload.name, payload.pid, user)


@router.post("/perDelete/{datasource_id}")
async def pre_delete_check(
    datasource_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> dict[str, bool]:
    in_use = await service.check_in_use(datasource_id)
    return {"inUse": in_use}


@router.post("/checkRepeat")
async def check_repeat(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> bool:
    return await service.check_repeat(_decode_datasource_payload(payload))


@router.post("/previewData")
async def preview_data(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.preview_data(payload)


@router.get("/showFinishPage")
async def show_finish_page(
    _: TokenUser = Depends(get_current_user),
) -> bool:
    return True


@router.post("/setShowFinishPage")
async def set_show_finish_page(
    _: dict | None = None,
    __: TokenUser = Depends(get_current_user),
) -> None:
    return None


@router.post("/syncApiTable")
async def sync_api_table(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> None:
    await service.sync_api_table(payload)


@router.post("/syncApiDs")
async def sync_api_datasource(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> None:
    await service.sync_api_datasource(payload)


@router.post("/listSyncRecord/{datasource_id}/{page}/{limit}")
async def list_sync_record(
    datasource_id: int,
    page: int,
    limit: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> dict[str, object]:
    return await service.list_sync_record(datasource_id, page, limit)


@router.post("/checkApiDatasource")
async def check_api_datasource(
    payload: dict,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.check_api_datasource(payload)


@router.get("/getSimpleDs/{datasource_id}")
async def get_simple_datasource(
    datasource_id: int,
    _: TokenUser = Depends(get_current_user),
    service: DatasourceService = Depends(get_datasource_service),
) -> object:
    return await service.get_simple(datasource_id)
