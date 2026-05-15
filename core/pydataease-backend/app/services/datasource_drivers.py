"""Datasource driver abstraction for multi-database support.

Each driver function returns a connection-like object that supports:
  - .fetch(sql, *args) -> list[Record]
  - .fetchval(sql, *args) -> Any
  - .close() -> None

The Record objects support dict-like access (record["column_name"]).
"""
from __future__ import annotations

import re
from typing import Any, Protocol, runtime_checkable

import asyncmy
import asyncpg
from fastapi import HTTPException, status

from app.schemas.datasource import JSONDict


@runtime_checkable
class DatasourceConnection(Protocol):
    async def fetch(self, query: str, *args: Any) -> list[Any]: ...
    async def fetchval(self, query: str, *args: Any) -> Any: ...
    async def close(self) -> None: ...


SUPPORTED_TYPES: dict[str, set[str]] = {
    "postgresql": {"pg", "postgres", "postgresql"},
    "mysql": {"mysql", "mariadb"},
}

_ALIAS_TO_CANONICAL: dict[str, str] = {}
for _canonical, _aliases in SUPPORTED_TYPES.items():
    for _alias in _aliases:
        _ALIAS_TO_CANONICAL[_alias.lower()] = _canonical


def canonical_type(raw_type: str) -> str:
    """Normalize a datasource type string to its canonical form."""
    key = raw_type.lower().strip()
    if key not in _ALIAS_TO_CANONICAL:
        raise ValueError(
            f"Datasource type '{raw_type}' is not supported. "
            f"Supported types: {sorted(_ALIAS_TO_CANONICAL.keys())}"
        )
    return _ALIAS_TO_CANONICAL[key]


def is_supported_type(raw_type: str) -> bool:
    """Check if a datasource type is supported without raising."""
    return raw_type.lower().strip() in _ALIAS_TO_CANONICAL


async def open_connection(ds_type: str, configuration: JSONDict) -> DatasourceConnection:
    """Open a connection to the specified datasource type."""
    canonical = canonical_type(ds_type)
    if canonical == "postgresql":
        return await _connect_postgresql(configuration)
    if canonical == "mysql":
        return await _connect_mysql(configuration)
    raise ValueError(f"Unsupported canonical type: {canonical}")


async def _connect_postgresql(configuration: JSONDict) -> asyncpg.Connection:
    host = _cfg(configuration, "host")
    port = _cfg_int(configuration, "port", 5432)
    user = _cfg(configuration, "username", _cfg(configuration, "user", "postgres"))
    password = str(_cfg(configuration, "password", ""))
    database = _cfg(configuration, "database", _cfg(configuration, "dataBase", "postgres"))
    schema = configuration.get("schema") or configuration.get("currentSchema") or "public"

    return await asyncpg.connect(
        host=str(host),
        port=port,
        user=str(user),
        password=password,
        database=str(database),
        server_settings={"search_path": str(schema)},
    )


async def _connect_mysql(configuration: JSONDict) -> Any:
    host = _cfg(configuration, "host")
    port = _cfg_int(configuration, "port", 3306)
    user = _cfg(configuration, "username", _cfg(configuration, "user", "root"))
    password = str(_cfg(configuration, "password", ""))
    database = _cfg(configuration, "database", _cfg(configuration, "dataBase", "mysql"))

    conn = await asyncmy.connect(
        host=str(host),
        port=port,
        user=str(user),
        password=password,
        db=str(database),
    )
    return _AsyncmyConnectionWrapper(conn)


class _AsyncmyConnectionWrapper:
    """Wrap asyncmy connection with an asyncpg-like interface."""

    def __init__(self, conn: Any) -> None:
        self._conn = conn

    async def fetch(self, query: str, *args: Any) -> list[dict[str, Any]]:
        sql = _mysql_query(query)
        async with self._conn.cursor() as cursor:
            if args:
                await cursor.execute(sql, args)
            else:
                await cursor.execute(sql)
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return [dict(zip(columns, row)) for row in rows]

    async def fetchval(self, query: str, *args: Any) -> Any:
        rows = await self.fetch(query, *args)
        if not rows:
            return None
        return next(iter(rows[0].values()), None)

    async def close(self) -> None:
        self._conn.close()


def _mysql_query(query: str) -> str:
    return re.sub(r"\$\d+", "%s", query)


def _cfg(configuration: JSONDict, key: str, default: object | None = None) -> object:
    value = configuration.get(key, default)
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing datasource configuration field: {key}",
        )
    return value


def _cfg_int(configuration: JSONDict, key: str, default: int) -> int:
    value = _cfg(configuration, key, default)
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Datasource configuration field '{key}' must be numeric",
        )
    try:
        return int(value)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Datasource configuration field '{key}' must be numeric",
        ) from exc
