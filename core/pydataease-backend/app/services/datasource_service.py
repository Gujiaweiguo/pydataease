from __future__ import annotations

import time
from typing import cast, final

import asyncpg
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.datasource import CoreDatasource
from app.models.engine import CoreDeEngine
from app.repositories.datasource_repo import DatasourceRepository
from app.schemas.auth import TokenUser
from app.schemas.datasource import (
    JSONDict,
    DatasourceCreate,
    DatasourceFieldResponse,
    DatasourceResponse,
    DatasourceTableResponse,
    DatasourceUpdate,
    DatasourceValidateRequest,
    DatasourceValidateResponse,
    EngineInfoResponse,
)

SUPPORTED_POSTGRES_TYPES = {"pg", "postgres", "postgresql"}


def _build_tree(nodes: list[dict], pid: int = 0) -> list[dict]:
    children = []
    for node in nodes:
        if node.get("pid", 0) == pid:
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

    async def tree(self) -> list[dict]:
        try:
            stmt = select(CoreDatasource).order_by(CoreDatasource.name.asc(), CoreDatasource.update_time.desc())
            result = await self.session.execute(stmt)
            rows = result.scalars().all()
            flat = [
                {"id": row.id, "name": row.name or "", "pid": row.pid or 0,
                 "leaf": True, "weight": 9, "extraFlag": 0, "extraFlag1": 0}
                for row in rows
            ]
            children = _build_tree(flat, pid=0)
        except (AttributeError, TypeError):
            children = []
        root = {"id": 0, "name": "root", "pid": -1, "leaf": False,
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
        merged_configuration = payload.configuration if payload.configuration is not None else existing.configuration
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
        await self._validate_postgres_connection(payload.configuration)
        return DatasourceValidateResponse(success=True, message="Connection successful", datasource_type=payload.type)

    async def get_tables(self, datasource_id: int) -> list[DatasourceTableResponse]:
        datasource = await self._get_entity(datasource_id)
        self._ensure_supported_type(datasource.type)
        configuration = _as_config_dict(datasource.configuration)
        connection = await self._open_connection(configuration)
        schema = self._schema_name(configuration)
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
        self._ensure_supported_type(datasource.type)
        configuration = _as_config_dict(datasource.configuration)
        connection = await self._open_connection(configuration)
        schema = self._schema_name(configuration)
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

    async def _get_entity(self, datasource_id: int) -> CoreDatasource:
        entity = await self.repository.get_by_id(datasource_id)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Datasource not found")
        return entity

    def _ensure_supported_type(self, datasource_type: str) -> None:
        if datasource_type.lower() not in SUPPORTED_POSTGRES_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Datasource type '{datasource_type}' is not supported yet. Only PostgreSQL is available.",
            )

    async def _probe_status(self, datasource_type: str, configuration: JSONDict) -> str:
        try:
            self._ensure_supported_type(datasource_type)
            await self._validate_postgres_connection(configuration)
        except Exception:
            return "Error"
        return "Success"

    async def _validate_postgres_connection(self, configuration: JSONDict) -> None:
        connection = await self._open_connection(configuration)
        try:
            _ = await connection.fetchval("SELECT 1")
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Connection failed: {exc}") from exc
        finally:
            await connection.close()

    async def _open_connection(self, configuration: JSONDict) -> asyncpg.Connection:
        try:
            return cast(
                asyncpg.Connection,
                await asyncpg.connect(
                    host=str(_config_value(configuration, "host")),
                    port=_config_int(configuration, "port", 5432),
                    user=str(_config_value(configuration, "username", _config_value(configuration, "user", "postgres"))),
                    password=str(_config_value(configuration, "password", "")),
                    database=str(_config_value(configuration, "database", _config_value(configuration, "dataBase", "postgres"))),
                    server_settings={"search_path": self._schema_name(configuration)},
                ),
            )
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Connection failed: {exc}") from exc

    @staticmethod
    def _schema_name(configuration: JSONDict) -> str:
        schema = configuration.get("schema") or configuration.get("currentSchema") or "public"
        return str(schema)


async def get_datasource_service(session: AsyncSession = Depends(get_db)) -> DatasourceService:
    return DatasourceService(session=session, repository=DatasourceRepository(session))


def _config_value(configuration: JSONDict, key: str, default: object | None = None) -> object:
    value = configuration.get(key, default)
    if value is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing datasource configuration field: {key}")
    return value


def _config_int(configuration: JSONDict, key: str, default: int) -> int:
    value = _config_value(configuration, key, default)
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Datasource configuration field '{key}' must be numeric")
    return int(value)


def _as_config_dict(configuration: object) -> JSONDict:
    if not isinstance(configuration, dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Datasource configuration must be an object")
    return cast(JSONDict, configuration)


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _new_identifier() -> int:
    return time.time_ns()
