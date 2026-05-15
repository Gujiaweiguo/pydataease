from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.services.datasource_drivers import _cfg, _cfg_int, canonical_type, is_supported_type


@pytest.mark.parametrize(
    ("raw_type", "expected"),
    [("pg", "postgresql"), ("postgres", "postgresql"), ("postgresql", "postgresql")],
)
def test_canonical_type_normalizes_postgresql_aliases(raw_type: str, expected: str) -> None:
    assert canonical_type(raw_type) == expected


@pytest.mark.parametrize(("raw_type", "expected"), [("mysql", "mysql"), ("mariadb", "mysql")])
def test_canonical_type_normalizes_mysql_aliases(raw_type: str, expected: str) -> None:
    assert canonical_type(raw_type) == expected


@pytest.mark.parametrize("raw_type", ["oracle", "clickhouse"])
def test_canonical_type_rejects_unsupported_types(raw_type: str) -> None:
    with pytest.raises(ValueError, match="not supported"):
        canonical_type(raw_type)


@pytest.mark.parametrize(
    ("raw_type", "expected"),
    [("pg", True), ("postgresql", True), ("mysql", True), ("mariadb", True), ("oracle", False)],
)
def test_is_supported_type(raw_type: str, expected: bool) -> None:
    assert is_supported_type(raw_type) is expected


def test_cfg_helpers_return_values_and_defaults() -> None:
    config = {"host": "localhost", "port": "3306"}

    assert _cfg(config, "host") == "localhost"
    assert _cfg(config, "database", "analytics") == "analytics"
    assert _cfg_int(config, "port", 5432) == 3306
    assert _cfg_int(config, "missing_port", 5432) == 5432


def test_cfg_helpers_raise_for_missing_and_invalid_values() -> None:
    with pytest.raises(HTTPException, match="Missing datasource configuration field: host"):
        _cfg({}, "host")

    with pytest.raises(HTTPException, match="must be numeric"):
        _cfg_int({"port": "not-a-number"}, "port", 5432)
