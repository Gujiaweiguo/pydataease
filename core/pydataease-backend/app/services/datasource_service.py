from __future__ import annotations

import time
from typing import Any, cast, final

from fastapi import Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.datasource import CoreDatasource
from app.models.engine import CoreDeEngine
from app.repositories.datasource_repo import DatasourceRepository
from app.services.datasource_drivers import canonical_type, is_supported_type, open_connection
from app.utils.id_utils import _sid
from app.schemas.auth import TokenUser
from app.schemas.datasource import (
    JSONDict,
    DatasourceCreate,
    DatasourceFieldResponse,
    DatasourceResponse,
    DatasourceSimpleResponse,
    DatasourceTableResponse,
    DatasourceUpdate,
    DatasourceValidateRequest,
    DatasourceValidateResponse,
    EngineInfoResponse,
)

def _build_tree(nodes: list[dict[str, Any]], pid: str = "0") -> list[dict[str, Any]]:
    children: list[dict[str, Any]] = []
    for node in nodes:
        if node.get("pid", "0") == pid:
            node_copy = dict(node)
            node_copy["children"] = _build_tree(nodes, node["id"])
            children.append(node_copy)
    return children


@final
class DatasourceService:
    session: AsyncSession
    repository: DatasourceRepository

    def __init__(self, session: AsyncSession, repository: DatasourceRepository) -> None:
        self.session = session
        self.repository = repository

    async def query(self, keyword: str) -> list[DatasourceResponse]:
        records = await self.repository.search(keyword)
        return [DatasourceResponse.model_validate(record) for record in records]

    async def tree(self) -> list[dict[str, Any]]:
        try:
            stmt = select(CoreDatasource).where(CoreDatasource.id != 0).order_by(CoreDatasource.name.asc(), CoreDatasource.update_time.desc())
            result = await self.session.execute(stmt)
            rows = result.scalars().all()
            flat = [
                {"id": _sid(row.id), "name": row.name or "", "pid": _sid(row.pid) if row.pid else "0",
                 "leaf": True, "weight": 9, "extraFlag": 0, "extraFlag1": 0}
                for row in rows
            ]
            children = _build_tree(flat, pid="0")
        except (AttributeError, TypeError):
            children = []
        root = {"id": "0", "name": "root", "pid": -1, "leaf": False,
                "weight": 7, "extraFlag": 0, "extraFlag1": 0, "children": children}
        return [root]

    async def save(self, payload: DatasourceCreate, user: TokenUser) -> DatasourceResponse:
        if payload.id:
            update_payload = DatasourceUpdate(**payload.model_dump())
            return await self.update(update_payload, user)

        self._ensure_supported_type(payload.type)
        now = _timestamp_ms()
        status_value = await self._probe_status(payload.type, payload.configuration)
        pid_value = None if payload.pid == 0 else payload.pid
        created = await self.repository.create(
            {
                "id": _new_identifier(),
                "name": payload.name.strip(),
                "description": payload.description,
                "type": payload.type,
                "pid": pid_value,
                "edit_type": payload.edit_type,
                "configuration": payload.configuration,
                "create_time": now,
                "update_time": now,
                "update_by": user.user_id,
                "create_by": str(user.user_id),
                "status": status_value,
                "qrtz_instance": None,
                "task_status": "WaitingForExecution",
                "enable_data_fill": payload.enable_data_fill,
            }
        )
        return DatasourceResponse.model_validate(created)

    async def update(self, payload: DatasourceUpdate, user: TokenUser) -> DatasourceResponse:
        existing = await self._get_entity(payload.id)
        merged_configuration = payload.configuration if payload.configuration is not None else _as_config_dict(existing.configuration)
        merged_type = payload.type or existing.type

        self._ensure_supported_type(merged_type)
        raw_pid = payload.pid if payload.pid is not None else existing.pid
        pid_value = None if raw_pid == 0 else raw_pid
        updated = await self.repository.update(
            existing,
            {
                "name": payload.name.strip() if payload.name is not None else existing.name,
                "description": payload.description if payload.description is not None else existing.description,
                "type": merged_type,
                "pid": pid_value,
                "edit_type": payload.edit_type if payload.edit_type is not None else existing.edit_type,
                "configuration": merged_configuration,
                "update_time": _timestamp_ms(),
                "update_by": user.user_id,
                "status": await self._probe_status(merged_type, merged_configuration),
                "enable_data_fill": payload.enable_data_fill if payload.enable_data_fill is not None else existing.enable_data_fill,
            },
        )
        return DatasourceResponse.model_validate(updated)

    async def delete(self, datasource_id: int) -> None:
        entity = await self._get_entity(datasource_id)
        await self.repository.delete(entity)

    async def validate(self, payload: DatasourceValidateRequest) -> DatasourceValidateResponse:
        self._ensure_supported_type(payload.type)
        await self._validate_connection(payload.type, payload.configuration)
        return DatasourceValidateResponse(success=True, message="Connection successful", datasource_type=payload.type)

    async def get_schemas_from_config(self, configuration: JSONDict, ds_type: str = "postgresql") -> list[str]:
        connection = await self._open_connection(configuration, ds_type)
        try:
            rows = await connection.fetch(
                "SELECT schema_name FROM information_schema.schemata ORDER BY schema_name"
            )
        finally:
            await connection.close()
        return [row["schema_name"] for row in rows]

    async def get_tables(self, datasource_id: int) -> list[DatasourceTableResponse]:
        datasource = await self._get_entity(datasource_id)
        ds_type = canonical_type(datasource.type)
        configuration = _as_config_dict(datasource.configuration)
        connection = await self._open_connection(configuration, datasource.type)
        schema = self._schema_name(configuration, ds_type)
        try:
            rows = await connection.fetch(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = $1 AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """,
                schema,
            )
        finally:
            await connection.close()
        return [DatasourceTableResponse(name=row["table_name"], schema_name=schema) for row in rows]

    async def get_fields(self, datasource_id: int, table_name: str) -> list[DatasourceFieldResponse]:
        datasource = await self._get_entity(datasource_id)
        ds_type = canonical_type(datasource.type)
        configuration = _as_config_dict(datasource.configuration)
        connection = await self._open_connection(configuration, datasource.type)
        schema = self._schema_name(configuration, ds_type)
        try:
            rows = await connection.fetch(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = $1 AND table_name = $2
                ORDER BY ordinal_position
                """,
                schema,
                table_name,
            )
        finally:
            await connection.close()
        return [
            DatasourceFieldResponse(
                name=row["column_name"],
                data_type=row["data_type"],
                nullable=row["is_nullable"] == "YES",
            )
            for row in rows
        ]

    async def get_engine_info(self) -> EngineInfoResponse:
        result = await self.session.execute(select(CoreDeEngine).limit(1))
        engine = result.scalars().first()
        if engine is None:
            return EngineInfoResponse(configured=False, type=None, status=None, name=None)
        return EngineInfoResponse(
            configured=True,
            type=engine.type,
            status=engine.status,
            name=engine.name,
        )

    async def latest_use(self) -> list[str]:
        try:
            stmt = (
                select(CoreDatasource.type)
                .where(CoreDatasource.type != "folder")
                .order_by(CoreDatasource.create_time.desc())
                .limit(5)
            )
            result = await self.session.execute(stmt)
            types = list(set(row[0] for row in result.all() if row[0]))
            return types[:5]
        except (AttributeError, TypeError):
            return []

    async def move(self, datasource_id: int, pid: int) -> None:
        entity = await self._get_entity(datasource_id)
        pid_value = None if pid == 0 else pid
        await self.repository.update(entity, {"pid": pid_value})

    async def rename(self, datasource_id: int, name: str) -> None:
        entity = await self._get_entity(datasource_id)
        await self.repository.update(entity, {"name": name.strip(), "update_time": _timestamp_ms()})

    async def create_folder(self, name: str, pid: int, user: TokenUser) -> DatasourceResponse:
        now = _timestamp_ms()
        pid_value = None if pid == 0 else pid
        created = await self.repository.create(
            {
                "id": _new_identifier(),
                "name": name.strip(),
                "type": "folder",
                "pid": pid_value,
                "configuration": {},
                "description": None,
                "edit_type": None,
                "create_time": now,
                "update_time": now,
                "update_by": user.user_id,
                "create_by": str(user.user_id),
                "status": "Success",
                "qrtz_instance": None,
                "task_status": "WaitingForExecution",
                "enable_data_fill": None,
            }
        )
        return DatasourceResponse.model_validate(created)

    async def get_full(self, datasource_id: int) -> DatasourceResponse:
        entity = await self._get_entity(datasource_id)
        return DatasourceResponse.model_validate(entity)

    async def get_hide_pw(self, datasource_id: int) -> DatasourceResponse:
        entity = await self._get_entity(datasource_id)
        resp = DatasourceResponse.model_validate(entity)
        if resp.configuration and isinstance(resp.configuration, dict):
            _mask_passwords(resp.configuration)
        return resp

    async def get_simple(self, datasource_id: int) -> DatasourceSimpleResponse:
        entity = await self._get_entity(datasource_id)
        return DatasourceSimpleResponse.model_validate(entity)

    async def validate_by_id(self, datasource_id: int) -> dict[str, str]:
        entity = await self._get_entity(datasource_id)
        config = entity.configuration if isinstance(entity.configuration, dict) else {}
        ds_type = entity.type
        status_value = await self._probe_status(ds_type, config)
        return {"status": status_value}

    async def check_in_use(self, datasource_id: int) -> bool:
        from app.models.dataset import CoreDatasetTable

        stmt = select(func.count()).select_from(CoreDatasetTable).where(
            CoreDatasetTable.datasource_id == datasource_id
        )
        result = await self.session.execute(stmt)
        count = result.scalar() or 0
        return count > 0

    async def _get_entity(self, datasource_id: int) -> CoreDatasource:
        entity = await self.repository.get_by_id(datasource_id)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Datasource not found")
        return entity

    def _ensure_supported_type(self, datasource_type: str) -> None:
        if not is_supported_type(datasource_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Datasource type '{datasource_type}' is not supported. "
                    "Supported: PostgreSQL (pg/postgres/postgresql), MySQL (mysql/mariadb)."
                ),
            )

    async def _probe_status(self, datasource_type: str, configuration: JSONDict) -> str:
        try:
            self._ensure_supported_type(datasource_type)
            await self._validate_connection(datasource_type, configuration)
        except Exception:
            return "Error"
        return "Success"

    async def _validate_connection(self, ds_type: str, configuration: JSONDict) -> None:
        connection = await self._open_connection(configuration, ds_type)
        try:
            _ = await connection.fetchval("SELECT 1")
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Connection failed: {exc}") from exc
        finally:
            await connection.close()

    async def _open_connection(self, configuration: JSONDict, ds_type: str | None = None) -> Any:
        type_str = ds_type or "postgresql"
        try:
            return await open_connection(type_str, configuration)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Connection failed: {exc}") from exc

    @staticmethod
    def _schema_name(configuration: JSONDict, ds_type: str = "postgresql") -> str:
        schema = configuration.get("schema") or configuration.get("currentSchema")
        if schema:
            return str(schema)
        if ds_type == "mysql":
            database = configuration.get("database") or configuration.get("dataBase") or "mysql"
            return str(database)
        schema = "public"
        return str(schema)

    async def upload_file(self, file: object, id: str | None = None, edit_type: str | None = None) -> dict[str, object]:
        return {"sheets": [], "fileName": ""}


async def get_datasource_service(session: AsyncSession = Depends(get_db)) -> DatasourceService:
    return DatasourceService(session=session, repository=DatasourceRepository(session))

def _as_config_dict(configuration: object) -> JSONDict:
    if not isinstance(configuration, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Datasource configuration must be an object")
    return cast(JSONDict, configuration)


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _new_identifier() -> int:
    return time.time_ns()


def _mask_passwords(config: dict) -> None:
    for key in list(config.keys()):
        if key.lower() in ("password", "pwd", "pass", "accesskey", "secretkey"):
            config[key] = "******"
        elif isinstance(config[key], dict):
            _mask_passwords(config[key])
