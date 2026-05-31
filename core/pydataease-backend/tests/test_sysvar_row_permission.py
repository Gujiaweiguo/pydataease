from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.data_permission_service import DataPermissionService  # pyright: ignore[reportImplicitRelativeImport]


def _user(user_id: int = 22, oid: int = 33) -> TokenUser:
    return TokenUser(user_id=user_id, oid=oid)


def _as_session(value: object) -> AsyncSession:
    return cast(AsyncSession, value)


class _ScalarResult:
    def __init__(self, values: list[Any]) -> None:
        self._values = values

    def all(self) -> list[Any]:
        return self._values


class _ExecuteResult:
    def __init__(self, scalars_values: list[Any] | None = None, rows: list[tuple[Any, ...]] | None = None) -> None:
        self._scalars_values = scalars_values or []
        self._rows = rows or []

    def scalars(self) -> _ScalarResult:
        return _ScalarResult(self._scalars_values)

    def all(self) -> list[tuple[Any, ...]]:
        return self._rows


class _SequenceSession:
    def __init__(self, results: list[_ExecuteResult]) -> None:
        self._results = results

    async def execute(self, _stmt: Any) -> _ExecuteResult:
        if not self._results:
            raise AssertionError("No fake execute result remaining")
        return self._results.pop(0)


@pytest.mark.asyncio
async def test_resolve_sysvar_rules_substitutes_placeholder_values() -> None:
    service = DataPermissionService(
        session=_as_session(
            _SequenceSession(
                [
                    _ExecuteResult(
                        scalars_values=[SimpleNamespace(filter_sql="region = ${dept_region} AND owner = ${owner_code}")]
                    ),
                    _ExecuteResult(rows=[("dept_region", "'east'"), ("owner_code", "'alice'")]),
                ]
            )
        )
    )

    assert await service._resolve_sysvar_rules(88, _user()) == ["region = 'east' AND owner = 'alice'"]


@pytest.mark.asyncio
async def test_resolve_sysvar_rules_returns_default_deny_when_variable_value_missing() -> None:
    service = DataPermissionService(
        session=_as_session(
            _SequenceSession(
                [
                    _ExecuteResult(scalars_values=[SimpleNamespace(filter_sql="region = ${dept_region}")]),
                    _ExecuteResult(rows=[]),
                ]
            )
        )
    )

    assert await service._resolve_sysvar_rules(88, _user()) == ["1=0"]


@pytest.mark.asyncio
async def test_collect_row_filters_prefers_user_rules_over_sysvar(monkeypatch: pytest.MonkeyPatch) -> None:
    service = DataPermissionService(session=_as_session(SimpleNamespace()))

    async def fake_is_whitelisted(*_args: Any, **_kwargs: Any) -> bool:
        return False

    async def fake_get_user_role_ids(_user: TokenUser) -> list[int]:
        return [501]

    async def fake_fetch_rules(_dataset_id: int, target_type: str, target_id: int) -> list[Any]:
        rules = {
            ("user", 22): [SimpleNamespace(filter_sql="owner_id = 22")],
            ("role", 501): [SimpleNamespace(filter_sql="region = 'west'")],
            ("org", 33): [SimpleNamespace(filter_sql="tenant_id = 33")],
        }
        return rules.get((target_type, target_id), [])

    async def fake_resolve_sysvar_rules(_dataset_id: int, _user: TokenUser) -> list[str] | None:
        return ["region = 'east'"]

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)
    monkeypatch.setattr(service, "_get_user_role_ids", fake_get_user_role_ids)
    monkeypatch.setattr(service, "_fetch_rules", fake_fetch_rules)
    monkeypatch.setattr(service, "_resolve_sysvar_rules", fake_resolve_sysvar_rules)

    assert await service.collect_row_filters(_user(), 88) == ["owner_id = 22"]


@pytest.mark.asyncio
async def test_collect_row_filters_prefers_sysvar_rules_over_role_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    service = DataPermissionService(session=_as_session(SimpleNamespace()))

    async def fake_is_whitelisted(*_args: Any, **_kwargs: Any) -> bool:
        return False

    async def fake_get_user_role_ids(_user: TokenUser) -> list[int]:
        return [501]

    async def fake_fetch_rules(_dataset_id: int, target_type: str, target_id: int) -> list[Any]:
        rules = {
            ("role", 501): [SimpleNamespace(filter_sql="region = 'west'")],
            ("org", 33): [SimpleNamespace(filter_sql="tenant_id = 33")],
        }
        return rules.get((target_type, target_id), [])

    async def fake_resolve_sysvar_rules(_dataset_id: int, _user: TokenUser) -> list[str] | None:
        return ["region = 'east'"]

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)
    monkeypatch.setattr(service, "_get_user_role_ids", fake_get_user_role_ids)
    monkeypatch.setattr(service, "_fetch_rules", fake_fetch_rules)
    monkeypatch.setattr(service, "_resolve_sysvar_rules", fake_resolve_sysvar_rules)

    assert await service.collect_row_filters(_user(), 88) == ["region = 'east'"]


@pytest.mark.asyncio
async def test_collect_row_filters_preserves_role_and_org_fallbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    service = DataPermissionService(session=_as_session(SimpleNamespace()))

    async def fake_is_whitelisted(*_args: Any, **_kwargs: Any) -> bool:
        return False

    async def fake_resolve_sysvar_rules(_dataset_id: int, _user: TokenUser) -> list[str] | None:
        return None

    async def fake_fetch_rules(_dataset_id: int, target_type: str, target_id: int) -> list[Any]:
        rules = {
            ("role", 501): [SimpleNamespace(filter_sql="region = 'west'")],
            ("org", 33): [SimpleNamespace(filter_sql="tenant_id = 33")],
        }
        return rules.get((target_type, target_id), [])

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)
    monkeypatch.setattr(service, "_resolve_sysvar_rules", fake_resolve_sysvar_rules)
    monkeypatch.setattr(service, "_fetch_rules", fake_fetch_rules)

    async def role_ids(_: TokenUser) -> list[int]:
        return [501]

    monkeypatch.setattr(service, "_get_user_role_ids", role_ids)
    assert await service.collect_row_filters(_user(), 88) == ["region = 'west'"]

    async def no_role_ids(_: TokenUser) -> list[int]:
        return []

    monkeypatch.setattr(service, "_get_user_role_ids", no_role_ids)
    assert await service.collect_row_filters(_user(), 88) == ["tenant_id = 33"]
