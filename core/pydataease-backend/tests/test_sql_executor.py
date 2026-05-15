from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.services.sql_executor import apply_limit, validate_readonly_sql


@pytest.mark.parametrize(
    ("sql", "expected"),
    [
        ("SELECT * FROM metrics", "SELECT * FROM metrics"),
        (" WITH recent AS (SELECT 1) SELECT * FROM recent; ", "WITH recent AS (SELECT 1) SELECT * FROM recent"),
    ],
)
def test_validate_readonly_sql_accepts_select_and_with(sql: str, expected: str) -> None:
    assert validate_readonly_sql(sql) == expected


@pytest.mark.parametrize("sql", ["INSERT INTO t VALUES (1)", "UPDATE t SET a = 1", "DELETE FROM t", "DROP TABLE t"])
def test_validate_readonly_sql_rejects_mutating_queries(sql: str) -> None:
    with pytest.raises(HTTPException, match="Only SELECT queries are allowed"):
        validate_readonly_sql(sql)


def test_validate_readonly_sql_rejects_empty_sql() -> None:
    with pytest.raises(HTTPException, match="SQL must not be empty"):
        validate_readonly_sql("  ;  ")


def test_validate_readonly_sql_rejects_multi_statement_sql() -> None:
    with pytest.raises(HTTPException, match="Only a single SELECT query is allowed"):
        validate_readonly_sql("SELECT 1; SELECT 2")


def test_apply_limit_appends_limit_when_missing() -> None:
    assert apply_limit("SELECT * FROM metrics") == "SELECT * FROM metrics LIMIT 1000"


def test_apply_limit_preserves_existing_limit() -> None:
    assert apply_limit("SELECT * FROM metrics LIMIT 5") == "SELECT * FROM metrics LIMIT 5"
