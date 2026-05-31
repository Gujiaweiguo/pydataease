from __future__ import annotations

from types import SimpleNamespace
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.data_permission_service import (  # pyright: ignore[reportImplicitRelativeImport]
    DataPermissionService,
    _mask_value,
    _mask_value_range,
)


def _user(user_id: int = 22, oid: int = 33) -> TokenUser:
    return TokenUser(user_id=user_id, oid=oid)


def _as_session(value: object) -> AsyncSession:
    return cast(AsyncSession, value)


class _ScalarResult:
    def __init__(self, values):
        self._values = values

    def all(self):
        return self._values


class _ExecuteResult:
    def __init__(self, values):
        self._values = values

    def scalars(self):
        return _ScalarResult(self._values)


class _FieldSession:
    def __init__(self, fields):
        self._fields = fields

    async def execute(self, stmt):
        return _ExecuteResult(self._fields)


def test_mask_value_range_masks_custom_positions():
    assert _mask_value_range("1234567890", 3, 7) == "123****890"


def test_mask_value_range_preserves_default_behavior_when_range_not_set():
    assert _mask_value_range("1234567890", None, None) == _mask_value("1234567890")


def test_mask_value_range_ignores_start_beyond_length():
    assert _mask_value_range("1234567890", 20, 25) == "1234567890"


@pytest.mark.asyncio
async def test_apply_column_rules_keeps_other_actions_working_with_custom_mask(monkeypatch):
    field_phone_id = 7001
    field_ssn_id = 7002
    field_email_id = 7003
    session = _FieldSession(
        [
            SimpleNamespace(id=field_phone_id, origin_name="phone", name="Phone", dataease_name=None),
            SimpleNamespace(id=field_ssn_id, origin_name="ssn", name="SSN", dataease_name=None),
            SimpleNamespace(id=field_email_id, origin_name="email", name="Email", dataease_name=None),
        ]
    )
    service = DataPermissionService(session=_as_session(session))

    async def fake_is_whitelisted(*args, **kwargs) -> bool:
        return False

    async def fake_get_user_role_ids(user: TokenUser) -> list[int]:
        return []

    async def fake_fetch_column_rules(dataset_id: int, user: TokenUser, role_ids: list[int]):
        return [
            SimpleNamespace(field_id=field_phone_id, action="mask", target_type="user", mask_start=3, mask_end=7),
            SimpleNamespace(field_id=field_ssn_id, action="desensitize", target_type="user", mask_start=None, mask_end=None),
            SimpleNamespace(field_id=field_email_id, action="disable", target_type="user", mask_start=None, mask_end=None),
        ]

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)
    monkeypatch.setattr(service, "_get_user_role_ids", fake_get_user_role_ids)
    monkeypatch.setattr(service, "_fetch_column_rules", fake_fetch_column_rules)

    fields = [{"name": "Phone"}, {"name": "SSN"}, {"name": "Email"}]
    rows = [["1234567890", "123-45-6789", "alice@example.com"]]

    new_fields, new_rows = await service.apply_column_rules(_user(), 88, fields, rows)

    assert new_fields == [{"name": "Phone"}, {"name": "SSN"}]
    assert new_rows == [["123****890", "***"]]
