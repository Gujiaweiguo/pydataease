"""Service for MySQLBot advanced assistant callback operations."""

from __future__ import annotations

import base64
import logging
from typing import Any

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.datasource_repo import DatasourceRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.sys_setting_repo import SysSettingRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.mysqlbot import (  # pyright: ignore[reportImplicitRelativeImport]
    MysqlBotDatasource,
    MysqlBotField,
    MysqlBotQueryResponse,
    MysqlBotTable,
)
from app.services.datasource_drivers import open_connection  # pyright: ignore[reportImplicitRelativeImport]
from app.services.sql_executor import validate_readonly_sql, apply_limit  # pyright: ignore[reportImplicitRelativeImport]

logger = logging.getLogger(__name__)

# Maximum rows returned by the MySQLBot query endpoint.
_QUERY_ROW_LIMIT = 1000

# Fields that MySQLBot expects to be AES-encrypted when encryption is enabled.
_AES_SENSITIVE_FIELDS = ("host", "user", "password", "dataBase", "db_schema", "mode")

# AES block size in bits for PKCS7 padding.
_AES_BLOCK_SIZE = 128


def _simple_aes_encrypt(plaintext: str, key: str, iv: str) -> str:
    """Encrypt a string using AES-256-CBC with PKCS7 padding.

    Compatible with MySQLBot's ``simple_aes_encrypt`` — same algorithm,
    same Base64 output format.
    """
    key_bytes = key[:32].ljust(32, "\x00").encode()
    iv_bytes = iv[:16].ljust(16, "\x00").encode()
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv_bytes))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(_AES_BLOCK_SIZE).padder()
    padded = padder.update(plaintext.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(ciphertext).decode()


async def _get_aes_config(session: AsyncSession) -> tuple[str, str] | None:
    """Return (key, iv) if AES encryption is configured, else None."""
    repo = SysSettingRepository(session)
    key_row = await repo.get_by_key("sqlbot.aesKey")
    iv_row = await repo.get_by_key("sqlbot.aesIv")
    aes_key = key_row.setting_value if key_row and key_row.setting_value else ""
    aes_iv = iv_row.setting_value if iv_row and iv_row.setting_value else ""
    if aes_key:
        return (aes_key, aes_iv or "sqlbot_em_aes_iv")
    return None


class MysqlBotService:
    """Handles datasource metadata and query execution for MySQLBot callbacks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = DatasourceRepository(session)

    async def list_datasources(self) -> list[MysqlBotDatasource]:
        """Return all real datasources (not folders) with connection credentials."""
        rows = await self.repo.search("")
        aes_config = await _get_aes_config(self.session)
        result: list[MysqlBotDatasource] = []
        for row in rows:
            if row.type == "folder":
                continue
            config = row.configuration if isinstance(row.configuration, dict) else {}
            ds = MysqlBotDatasource(
                id=row.id,
                name=row.name or "",
                type=row.type or "unknown",
                type_name=_type_display_name(row.type),
                comment=row.description or "",
                host=str(config.get("host") or ""),
                port=int(str(config.get("port") or "0")),
                dataBase=str(config.get("dataBase") or config.get("database") or ""),
                user=str(config.get("username") or config.get("user") or ""),
                password=str(config.get("password") or ""),
                extraParams=str(config.get("extraParams") or config.get("extraParameters") or ""),
                db_schema=str(config.get("currentSchema") or config.get("schema") or ""),
            )
            # Encrypt sensitive fields if AES is configured (MySQLBot compat).
            if aes_config is not None:
                ds = _encrypt_datasource_fields(ds, aes_config[0], aes_config[1])
            result.append(ds)
        return result

    async def get_datasource_or_raise(self, datasource_id: int) -> Any:
        """Fetch a datasource by ID or raise ValueError if not found."""
        row = await self.repo.get_by_id(datasource_id)
        if row is None:
            raise ValueError(f"Datasource {datasource_id} not found")
        return row

    async def list_tables(self, datasource_id: int) -> list[MysqlBotTable]:
        """Return all tables in the specified datasource."""
        ds = await self.get_datasource_or_raise(datasource_id)
        config = ds.configuration if isinstance(ds.configuration, dict) else {}
        ds_type = ds.type or "unknown"
        conn = await open_connection(ds_type, config)
        try:
            sql, args = _tables_sql(ds_type, config.get("currentSchema") or config.get("schema") or "public")
            rows = await conn.fetch(sql, *args)
            return [
                MysqlBotTable(
                    name=str(r["table_name"] or r[0]),
                    comment=str(r.get("table_schema", "") or ""),
                )
                for r in rows
            ]
        finally:
            await conn.close()

    async def list_fields(self, datasource_id: int, table_name: str) -> list[MysqlBotField]:
        """Return column metadata for the specified table."""
        ds = await self.get_datasource_or_raise(datasource_id)
        config = ds.configuration if isinstance(ds.configuration, dict) else {}
        ds_type = ds.type or "unknown"
        conn = await open_connection(ds_type, config)
        try:
            schema_name = config.get("currentSchema") or config.get("schema") or ""
            sql, args = _fields_sql(ds_type, schema_name, table_name)
            rows = await conn.fetch(sql, *args)
            return [
                MysqlBotField(
                    name=str(r["column_name"] or r[0]),
                    type=str(r.get("data_type", "") or ""),
                    comment=str(r.get("column_comment", "") or "") if "column_comment" in r.keys() else None,
                )
                for r in rows
            ]
        finally:
            await conn.close()

    async def execute_query(self, datasource_id: int, sql: str) -> MysqlBotQueryResponse:
        """Execute a read-only SQL query against the specified datasource."""
        ds = await self.get_datasource_or_raise(datasource_id)
        config = ds.configuration if isinstance(ds.configuration, dict) else {}
        ds_type = ds.type or "unknown"

        # Security: validate read-only
        validate_readonly_sql(sql)
        sql = apply_limit(sql, _QUERY_ROW_LIMIT)

        conn = await open_connection(ds_type, config)
        try:
            rows = await conn.fetch(sql)
            fields: list[str] = list(rows[0].keys()) if rows else []
            data: list[list[object]] = [
                [r.get(f) for f in fields] for r in rows
            ]
            return MysqlBotQueryResponse(fields=fields, data=data, total=len(data))
        finally:
            await conn.close()


def _encrypt_datasource_fields(
    ds: MysqlBotDatasource, key: str, iv: str
) -> MysqlBotDatasource:
    """Encrypt sensitive fields on a datasource using AES-256-CBC."""
    for field in _AES_SENSITIVE_FIELDS:
        value = getattr(ds, field, None)
        if isinstance(value, str):
            setattr(ds, field, _simple_aes_encrypt(value, key, iv))
    return ds


def _tables_sql(ds_type: str, schema: str) -> tuple[str, list[str]]:
    """Return (parameterized SQL, args) to list tables for a given datasource type."""
    if ds_type in ("postgresql", "pg", "postgres"):
        return (
            "SELECT tablename AS table_name, schemaname AS table_schema "
            "FROM pg_tables WHERE schemaname = $1 "
            "ORDER BY tablename",
            [schema],
        )
    # MySQL / MariaDB / default — DATABASE() is safe (no user input).
    return (
        "SELECT table_name, table_schema "
        "FROM information_schema.tables "
        "WHERE table_schema = DATABASE() "
        "ORDER BY table_name",
        [],
    )


def _fields_sql(ds_type: str, schema: str, table_name: str) -> tuple[str, list[str]]:
    """Return (parameterized SQL, args) to list columns for a given table."""
    if ds_type in ("postgresql", "pg", "postgres"):
        return (
            "SELECT column_name, data_type, is_nullable "
            "FROM information_schema.columns "
            "WHERE table_schema = $1 AND table_name = $2 "
            "ORDER BY ordinal_position",
            [schema, table_name],
        )
    # MySQL / MariaDB / default
    return (
        "SELECT column_name, data_type, is_nullable "
        "FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = %s "
        "ORDER BY ordinal_position",
        [table_name],
    )


def get_mysqlbot_service(session: AsyncSession = Depends(get_db)) -> MysqlBotService:
    return MysqlBotService(session)


_TYPE_DISPLAY: dict[str, str] = {
    "mysql": "MySQL",
    "mariadb": "MariaDB",
    "postgresql": "PostgreSQL",
    "pg": "PostgreSQL",
    "postgres": "PostgreSQL",
    "clickhouse": "ClickHouse",
    "doris": "Doris",
    "starrocks": "StarRocks",
    "oracle": "Oracle",
    "sqlserver": "SQL Server",
    "db2": "Db2",
    "tidb": "TiDB",
    "impala": "Impala",
    "redshift": "RedShift",
    "mongo-bi": "MongoDB-BI",
}


def _type_display_name(ds_type: str | None) -> str:
    if not ds_type:
        return "Unknown"
    return _TYPE_DISPLAY.get(ds_type.lower(), ds_type)
