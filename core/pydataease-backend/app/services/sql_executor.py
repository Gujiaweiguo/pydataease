from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from app.dependencies.database import engine

_LEADING_QUERY_RE = re.compile(r"^\s*(select|with)\b", re.IGNORECASE | re.DOTALL)
_LIMIT_RE = re.compile(r"\blimit\b", re.IGNORECASE)
_FORBIDDEN_SQL_RE = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|merge|call|copy|vacuum|analyze|comment|execute)\b",
    re.IGNORECASE,
)
_LINE_COMMENT_RE = re.compile(r"--.*?(?:\n|$)")
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_SINGLE_QUOTED_RE = re.compile(r"'(?:''|[^'])*'")
_DOUBLE_QUOTED_RE = re.compile(r'"(?:""|[^"])*"')


def _sanitize_sql(sql: str) -> str:
    sanitized = _LINE_COMMENT_RE.sub(" ", sql)
    sanitized = _BLOCK_COMMENT_RE.sub(" ", sanitized)
    sanitized = _SINGLE_QUOTED_RE.sub("''", sanitized)
    sanitized = _DOUBLE_QUOTED_RE.sub('""', sanitized)
    return sanitized


def validate_readonly_sql(sql: str) -> str:
    normalized = sql.strip().rstrip(";").strip()
    if not normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SQL must not be empty")
    if not _LEADING_QUERY_RE.match(normalized):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SELECT queries are allowed",
        )

    sanitized = _sanitize_sql(normalized)
    if ";" in sanitized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only a single SELECT query is allowed",
        )
    if _FORBIDDEN_SQL_RE.search(sanitized):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only SELECT queries are allowed",
        )
    return normalized


def apply_limit(sql: str, limit: int = 1000) -> str:
    if limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be greater than zero",
        )
    if _LIMIT_RE.search(_sanitize_sql(sql)):
        return sql
    return f"{sql} LIMIT {limit}"


class SQLExecutor:
    def __init__(self, db_engine: AsyncEngine | None = None) -> None:
        self._engine = db_engine or engine

    async def execute_select(self, sql: str, limit: int = 1000) -> dict[str, object]:
        normalized_sql = self._normalize_sql(sql)
        executable_sql = self._apply_limit(normalized_sql, limit)

        try:
            async with self._engine.connect() as conn:
                result = await conn.execute(text(executable_sql))
                rows = [list(row) for row in result.all()]
                fields = self._build_fields(result, rows)
        except HTTPException:
            raise
        except SQLAlchemyError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SQL preview failed: {exc}",
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SQL preview failed: {exc}",
            ) from exc

        return {"sql": executable_sql, "data": rows, "fields": fields, "total": len(rows)}

    def _normalize_sql(self, sql: str) -> str:
        return validate_readonly_sql(sql)

    def _apply_limit(self, sql: str, limit: int) -> str:
        return apply_limit(sql, limit)

    def _build_fields(self, result: Result[Any], rows: Sequence[list[object]]) -> list[dict[str, str]]:
        keys = list(result.keys())
        description = self._cursor_description(result)
        fields: list[dict[str, str]] = []
        for index, name in enumerate(keys):
            field_type = self._description_type(description, index)
            if field_type is None:
                field_type = self._infer_type(rows, index)
            fields.append({"name": name, "type": field_type or "unknown"})
        return fields

    @staticmethod
    def _sanitize_sql(sql: str) -> str:
        return _sanitize_sql(sql)

    @staticmethod
    def _cursor_description(result: Result[Any]) -> Sequence[object] | None:
        cursor = getattr(result, "cursor", None)
        if cursor is None:
            return None
        description = getattr(cursor, "description", None)
        if isinstance(description, Sequence):
            return description
        return None

    @staticmethod
    def _description_type(description: Sequence[object] | None, index: int) -> str | None:
        if description is None or index >= len(description):
            return None
        column = description[index]
        if not isinstance(column, Sequence) or len(column) < 2:
            return None
        type_code = column[1]
        if type_code is None:
            return None
        if isinstance(type_code, str):
            return type_code.lower()
        type_name = getattr(type_code, "name", None)
        if isinstance(type_name, str):
            return type_name.lower()
        dunder_name = getattr(type_code, "__name__", None)
        if isinstance(dunder_name, str):
            return dunder_name.lower()
        return str(type_code).lower()

    def _infer_type(self, rows: Sequence[list[object]], index: int) -> str | None:
        for row in rows:
            if index >= len(row):
                continue
            value = row[index]
            if value is None:
                continue
            return self._python_type_name(value)
        return None

    @staticmethod
    def _python_type_name(value: object) -> str:
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "float"
        if isinstance(value, Decimal):
            return "numeric"
        if isinstance(value, str):
            return "varchar"
        if isinstance(value, bytes):
            return "bytea"
        if isinstance(value, datetime):
            return "timestamp"
        if isinstance(value, date):
            return "date"
        if isinstance(value, time):
            return "time"
        if isinstance(value, dict | list):
            return "jsonb"
        return type(value).__name__.lower()
