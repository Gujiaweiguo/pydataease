from __future__ import annotations

import os
from types import SimpleNamespace
from typing import cast

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.column_permission import CoreColumnPermission  # pyright: ignore[reportImplicitRelativeImport]
from app.models.dataset import (  # pyright: ignore[reportImplicitRelativeImport]
    CoreDatasetGroup,
    CoreDatasetTable,
    CoreDatasetTableField,
)
from app.models.permission_whitelist import CorePermissionWhitelist  # pyright: ignore[reportImplicitRelativeImport]
from app.models.role import CoreRole  # pyright: ignore[reportImplicitRelativeImport]
from app.models.role_user import CoreRoleUser  # pyright: ignore[reportImplicitRelativeImport]
from app.models.row_permission import CoreRowPermission  # pyright: ignore[reportImplicitRelativeImport]
from app.models.user import CoreUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.data_permission_service import (  # pyright: ignore[reportImplicitRelativeImport]
    DataPermissionService,
    _mask_value,
    apply_row_filters,
)
from app.utils.password_utils import hash_password  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import (  # pyright: ignore[reportImplicitRelativeImport]
    cleanup_groups,
    stamp,
    timestamp_ms,
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


@pytest.mark.parametrize(
    ("sql", "filters", "expected"),
    [
        ("SELECT * FROM sales", [], "SELECT * FROM sales"),
        (
            "SELECT * FROM sales WHERE active = 1",
            ["region = 'east'", "owner = 'alice'"],
            "SELECT * FROM (SELECT * FROM sales WHERE active = 1) AS _perm_filtered WHERE (region = 'east') AND (owner = 'alice')",
        ),
        (
            "SELECT * FROM sales ORDER BY id DESC",
            ["region = 'east'"],
            "SELECT * FROM (SELECT * FROM sales ORDER BY id DESC) AS _perm_filtered WHERE (region = 'east')",
        ),
        (
            "SELECT region, count(*) FROM sales GROUP BY region LIMIT 5",
            ["tenant_id = 7"],
            "SELECT * FROM (SELECT region, count(*) FROM sales GROUP BY region LIMIT 5) AS _perm_filtered WHERE (tenant_id = 7)",
        ),
    ],
)
def test_apply_row_filters_handles_where_and_clause_insertion(sql, filters, expected):
    assert apply_row_filters(sql, filters) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("a", "*"), ("ab", "a*"), ("abcd", "a**d")],
)
def test_mask_value_handles_short_and_long_inputs(value, expected):
    assert _mask_value(value) == expected


@pytest.mark.asyncio
async def test_collect_row_filters_returns_empty_for_admin():
    service = DataPermissionService(session=_as_session(SimpleNamespace()))

    assert await service.collect_row_filters(_user(user_id=1), dataset_id=88) == []


@pytest.mark.asyncio
async def test_collect_row_filters_returns_empty_for_whitelisted_user(monkeypatch):
    service = DataPermissionService(session=_as_session(SimpleNamespace()))

    async def fake_is_whitelisted(user_id: int, dataset_id: int, scope: str) -> bool:
        assert (user_id, dataset_id, scope) == (22, 88, "row")
        return True

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)

    assert await service.collect_row_filters(_user(), dataset_id=88) == []


@pytest.mark.asyncio
async def test_collect_row_filters_prefers_user_rules_over_role_and_org(monkeypatch):
    service = DataPermissionService(session=_as_session(SimpleNamespace()))

    async def fake_is_whitelisted(*args, **kwargs) -> bool:
        return False

    async def fake_get_user_role_ids(user: TokenUser) -> list[int]:
        return [501]

    async def fake_fetch_rules(dataset_id: int, target_type: str, target_id: int):
        rules = {
            ("user", 22): [SimpleNamespace(filter_sql="owner_id = 22")],
            ("role", 501): [SimpleNamespace(filter_sql="region = 'east'")],
            ("org", 33): [SimpleNamespace(filter_sql="tenant_id = 33")],
        }
        return rules.get((target_type, target_id), [])

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)
    monkeypatch.setattr(service, "_get_user_role_ids", fake_get_user_role_ids)
    monkeypatch.setattr(service, "_fetch_rules", fake_fetch_rules)

    assert await service.collect_row_filters(_user(), dataset_id=88) == ["owner_id = 22"]


@pytest.mark.asyncio
async def test_collect_row_filters_aggregates_role_rules_when_no_user_rule(monkeypatch):
    service = DataPermissionService(session=_as_session(SimpleNamespace()))

    async def fake_is_whitelisted(*args, **kwargs) -> bool:
        return False

    async def fake_get_user_role_ids(user: TokenUser) -> list[int]:
        return [501, 502]

    async def fake_fetch_rules(dataset_id: int, target_type: str, target_id: int):
        rules = {
            ("role", 501): [SimpleNamespace(filter_sql="region = 'east'")],
            ("role", 502): [SimpleNamespace(filter_sql="dept = 'ops'")],
            ("org", 33): [SimpleNamespace(filter_sql="tenant_id = 33")],
        }
        return rules.get((target_type, target_id), [])

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)
    monkeypatch.setattr(service, "_get_user_role_ids", fake_get_user_role_ids)
    monkeypatch.setattr(service, "_fetch_rules", fake_fetch_rules)

    assert await service.collect_row_filters(_user(), dataset_id=88) == ["region = 'east'", "dept = 'ops'"]


@pytest.mark.asyncio
async def test_collect_row_filters_falls_back_to_org_rules(monkeypatch):
    service = DataPermissionService(session=_as_session(SimpleNamespace()))

    async def fake_is_whitelisted(*args, **kwargs) -> bool:
        return False

    async def fake_get_user_role_ids(user: TokenUser) -> list[int]:
        return []

    async def fake_fetch_rules(dataset_id: int, target_type: str, target_id: int):
        if (target_type, target_id) == ("org", 33):
            return [SimpleNamespace(filter_sql="tenant_id = 33")]
        return []

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)
    monkeypatch.setattr(service, "_get_user_role_ids", fake_get_user_role_ids)
    monkeypatch.setattr(service, "_fetch_rules", fake_fetch_rules)

    assert await service.collect_row_filters(_user(), dataset_id=88) == ["tenant_id = 33"]


@pytest.mark.asyncio
async def test_collect_row_filters_returns_empty_when_no_rules(monkeypatch):
    service = DataPermissionService(session=_as_session(SimpleNamespace()))

    async def fake_is_whitelisted(*args, **kwargs) -> bool:
        return False

    async def fake_get_user_role_ids(user: TokenUser) -> list[int]:
        return []

    async def fake_fetch_rules(dataset_id: int, target_type: str, target_id: int):
        return []

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)
    monkeypatch.setattr(service, "_get_user_role_ids", fake_get_user_role_ids)
    monkeypatch.setattr(service, "_fetch_rules", fake_fetch_rules)

    assert await service.collect_row_filters(_user(), dataset_id=88) == []


@pytest.mark.asyncio
async def test_apply_column_rules_returns_original_data_for_admin():
    fields = [{"name": "email"}]
    rows = [["alice@example.com"]]
    service = DataPermissionService(session=_as_session(SimpleNamespace()))

    new_fields, new_rows = await service.apply_column_rules(_user(user_id=1), 88, fields, rows)

    assert new_fields == fields
    assert new_rows == rows


@pytest.mark.asyncio
async def test_apply_column_rules_returns_original_data_for_whitelisted_user(monkeypatch):
    fields = [{"name": "email"}]
    rows = [["alice@example.com"]]
    service = DataPermissionService(session=_as_session(SimpleNamespace()))

    async def fake_is_whitelisted(user_id: int, dataset_id: int, scope: str) -> bool:
        assert (user_id, dataset_id, scope) == (22, 88, "column")
        return True

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)

    new_fields, new_rows = await service.apply_column_rules(_user(), 88, fields, rows)

    assert new_fields == fields
    assert new_rows == rows


@pytest.mark.asyncio
async def test_apply_column_rules_enforces_priority_disable_mask_and_desensitize(monkeypatch):
    field_email_id = 7001
    field_phone_id = 7002
    field_ssn_id = 7003
    session = _FieldSession(
        [
            SimpleNamespace(id=field_email_id, origin_name="email", name="Email", dataease_name="emailAlias"),
            SimpleNamespace(id=field_phone_id, origin_name="phone", name="Phone", dataease_name=None),
            SimpleNamespace(id=field_ssn_id, origin_name="ssn", name=None, dataease_name="SocialSecurity"),
        ]
    )
    service = DataPermissionService(session=_as_session(session))

    async def fake_is_whitelisted(*args, **kwargs) -> bool:
        return False

    async def fake_get_user_role_ids(user: TokenUser) -> list[int]:
        return [501]

    async def fake_fetch_column_rules(dataset_id: int, user: TokenUser, role_ids: list[int]):
        return [
            SimpleNamespace(field_id=field_email_id, action="mask", target_type="org"),
            SimpleNamespace(field_id=field_email_id, action="disable", target_type="user"),
            SimpleNamespace(field_id=field_phone_id, action="mask", target_type="role"),
            SimpleNamespace(field_id=field_ssn_id, action="desensitize", target_type="org"),
        ]

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)
    monkeypatch.setattr(service, "_get_user_role_ids", fake_get_user_role_ids)
    monkeypatch.setattr(service, "_fetch_column_rules", fake_fetch_column_rules)

    fields = [{"name": "Email"}, {"name": "phone"}, {"name": "SocialSecurity"}, {"name": "city"}]
    rows = [["alice@example.com", "13912345678", "123-45-6789", "Shanghai"]]

    new_fields, new_rows = await service.apply_column_rules(_user(), 88, fields, rows)

    assert new_fields == [{"name": "phone"}, {"name": "SocialSecurity"}, {"name": "city"}]
    assert new_rows == [["1*********8", "***", "Shanghai"]]


@pytest.mark.asyncio
async def test_apply_column_rules_returns_original_when_no_field_matches(monkeypatch):
    session = _FieldSession([SimpleNamespace(id=7001, origin_name="other", name="Other", dataease_name=None)])
    service = DataPermissionService(session=_as_session(session))

    async def fake_is_whitelisted(*args, **kwargs) -> bool:
        return False

    async def fake_get_user_role_ids(user: TokenUser) -> list[int]:
        return []

    async def fake_fetch_column_rules(dataset_id: int, user: TokenUser, role_ids: list[int]):
        return [SimpleNamespace(field_id=7001, action="disable", target_type="user")]

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)
    monkeypatch.setattr(service, "_get_user_role_ids", fake_get_user_role_ids)
    monkeypatch.setattr(service, "_fetch_column_rules", fake_fetch_column_rules)

    fields = [{"name": "email"}]
    rows = [["alice@example.com"]]

    new_fields, new_rows = await service.apply_column_rules(_user(), 88, fields, rows)

    assert new_fields == fields
    assert new_rows == rows


@pytest.mark.asyncio
async def test_apply_column_rules_handles_empty_rows(monkeypatch):
    session = _FieldSession([SimpleNamespace(id=7001, origin_name="email", name=None, dataease_name=None)])
    service = DataPermissionService(session=_as_session(session))

    async def fake_is_whitelisted(*args, **kwargs) -> bool:
        return False

    async def fake_get_user_role_ids(user: TokenUser) -> list[int]:
        return []

    async def fake_fetch_column_rules(dataset_id: int, user: TokenUser, role_ids: list[int]):
        return [SimpleNamespace(field_id=7001, action="mask", target_type="user")]

    monkeypatch.setattr(service, "_is_whitelisted", fake_is_whitelisted)
    monkeypatch.setattr(service, "_get_user_role_ids", fake_get_user_role_ids)
    monkeypatch.setattr(service, "_fetch_column_rules", fake_fetch_column_rules)

    fields = [{"name": "email"}]
    rows: list[list[str]] = []

    new_fields, new_rows = await service.apply_column_rules(_user(), 88, fields, rows)

    assert new_fields == fields
    assert new_rows == []


pytestmark_e2e = pytest.mark.skipif(
    os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)"
)


async def _insert_permission_fixture_data(db_session, *, dataset_id: int, user_id: int, oid: int):
    now = timestamp_ms()
    role_id = stamp()
    dataset_table_id = stamp()
    field_email_id = stamp()
    field_phone_id = stamp()
    field_ssn_id = stamp()

    user = CoreUser(
        id=user_id,
        account=f"perm_user_{user_id}",
        name=f"perm_user_{user_id}",
        password=hash_password("DataEase@123456"),
        enable=True,
        oid=oid,
        origin=0,
        language="zh-CN",
        create_time=now,
        update_time=now,
    )
    role = CoreRole(
        id=role_id,
        name=f"perm_role_{role_id}",
        description="permission coverage role",
        oid=oid,
        type=1,
        create_time=now,
        update_time=now,
    )
    group = CoreDatasetGroup(
        id=dataset_id,
        name=f"perm_group_{dataset_id}",
        pid=0,
        level=1,
        node_type="dataset",
        type="sql",
        mode=1,
        info={},
        create_by=str(user_id),
        create_time=now,
        update_by=str(user_id),
        last_update_time=now,
        qrtz_instance=None,
        sync_status=None,
        union_sql=None,
        is_cross=False,
    )
    table = CoreDatasetTable(
        id=dataset_table_id,
        name="perm_table",
        table_name="perm_table",
        datasource_id=None,
        dataset_group_id=dataset_id,
        type="db",
        info="{}",
        sql_variable_details=None,
    )
    email_field = CoreDatasetTableField(
        id=field_email_id,
        datasource_id=None,
        dataset_table_id=dataset_table_id,
        dataset_group_id=dataset_id,
        chart_id=None,
        origin_name="email",
        name="Email",
        description="email",
        dataease_name="emailAlias",
        field_short_name=None,
        group_list=None,
        other_group=None,
        group_type=None,
        type="varchar",
        size=255,
        de_type=0,
        de_extract_type=0,
        ext_field=0,
        checked=True,
        column_index=1,
        last_sync_time=now,
        accuracy=None,
        date_format=None,
        date_format_type=None,
        params=None,
        order_checked=True,
    )
    phone_field = CoreDatasetTableField(
        id=field_phone_id,
        datasource_id=None,
        dataset_table_id=dataset_table_id,
        dataset_group_id=dataset_id,
        chart_id=None,
        origin_name="phone",
        name="Phone",
        description="phone",
        dataease_name=None,
        field_short_name=None,
        group_list=None,
        other_group=None,
        group_type=None,
        type="varchar",
        size=255,
        de_type=0,
        de_extract_type=0,
        ext_field=0,
        checked=True,
        column_index=2,
        last_sync_time=now,
        accuracy=None,
        date_format=None,
        date_format_type=None,
        params=None,
        order_checked=True,
    )
    ssn_field = CoreDatasetTableField(
        id=field_ssn_id,
        datasource_id=None,
        dataset_table_id=dataset_table_id,
        dataset_group_id=dataset_id,
        chart_id=None,
        origin_name="ssn",
        name="SSN",
        description="ssn",
        dataease_name="socialSecurity",
        field_short_name=None,
        group_list=None,
        other_group=None,
        group_type=None,
        type="varchar",
        size=255,
        de_type=0,
        de_extract_type=0,
        ext_field=0,
        checked=True,
        column_index=3,
        last_sync_time=now,
        accuracy=None,
        date_format=None,
        date_format_type=None,
        params=None,
        order_checked=True,
    )
    role_user = CoreRoleUser(id=stamp(), role_id=role_id, user_id=user_id, oid=oid)

    db_session.add_all([user, role, group, table, email_field, phone_field, ssn_field])
    await db_session.flush()
    db_session.add(role_user)
    await db_session.commit()
    return {
        "role_id": role_id,
        "field_email_id": field_email_id,
        "field_phone_id": field_phone_id,
        "field_ssn_id": field_ssn_id,
    }


async def _cleanup_permission_records(db_session, *, dataset_id: int, user_id: int, oid: int):
    stmts = [
        delete(CorePermissionWhitelist).where(
            CorePermissionWhitelist.user_id == user_id,
            (CorePermissionWhitelist.dataset_id == dataset_id) | (CorePermissionWhitelist.dataset_id == 0),
        ),
        delete(CoreColumnPermission).where(CoreColumnPermission.dataset_id == dataset_id),
        delete(CoreRowPermission).where(CoreRowPermission.dataset_id == dataset_id),
        delete(CoreRoleUser).where(CoreRoleUser.user_id == user_id, CoreRoleUser.oid == oid),
        delete(CoreRole).where(CoreRole.oid == oid, CoreRole.name.like("perm_role_%")),
        delete(CoreUser).where(CoreUser.id == user_id),
    ]
    for stmt in stmts:
        await db_session.execute(stmt)
    await db_session.commit()
    await cleanup_groups(db_session, [dataset_id])


@pytest.mark.asyncio
@pytestmark_e2e
async def test_collect_row_filters_integration_prefers_user_rules(db_session):
    dataset_id = stamp()
    user_id = stamp()
    oid = stamp()
    fixture = await _insert_permission_fixture_data(db_session, dataset_id=dataset_id, user_id=user_id, oid=oid)
    now = timestamp_ms()
    try:
        db_session.add_all(
            [
                CoreRowPermission(
                    id=stamp(),
                    dataset_id=dataset_id,
                    target_type="org",
                    target_id=oid,
                    filter_sql="tenant_id = 1",
                    enabled=True,
                    create_time=now,
                    update_time=now,
                ),
                CoreRowPermission(
                    id=stamp(),
                    dataset_id=dataset_id,
                    target_type="role",
                    target_id=fixture["role_id"],
                    filter_sql="region = 'east'",
                    enabled=True,
                    create_time=now,
                    update_time=now,
                ),
                CoreRowPermission(
                    id=stamp(),
                    dataset_id=dataset_id,
                    target_type="user",
                    target_id=user_id,
                    filter_sql="owner_id = 9",
                    enabled=True,
                    create_time=now,
                    update_time=now,
                ),
            ]
        )
        await db_session.commit()

        service = DataPermissionService(db_session)

        assert await service.collect_row_filters(TokenUser(user_id=user_id, oid=oid), dataset_id) == [
            "owner_id = 9"
        ]
    finally:
        await _cleanup_permission_records(db_session, dataset_id=dataset_id, user_id=user_id, oid=oid)


@pytest.mark.asyncio
@pytestmark_e2e
async def test_collect_row_filters_integration_whitelist_bypasses_all_rules(db_session):
    dataset_id = stamp()
    user_id = stamp()
    oid = stamp()
    fixture = await _insert_permission_fixture_data(db_session, dataset_id=dataset_id, user_id=user_id, oid=oid)
    now = timestamp_ms()
    try:
        db_session.add_all(
            [
                CorePermissionWhitelist(
                    id=stamp(), user_id=user_id, dataset_id=dataset_id, scope="both", create_time=now
                ),
                CoreRowPermission(
                    id=stamp(),
                    dataset_id=dataset_id,
                    target_type="role",
                    target_id=fixture["role_id"],
                    filter_sql="region = 'east'",
                    enabled=True,
                    create_time=now,
                    update_time=now,
                ),
            ]
        )
        await db_session.commit()

        service = DataPermissionService(db_session)

        assert await service.collect_row_filters(TokenUser(user_id=user_id, oid=oid), dataset_id) == []
    finally:
        await _cleanup_permission_records(db_session, dataset_id=dataset_id, user_id=user_id, oid=oid)


@pytest.mark.asyncio
@pytestmark_e2e
async def test_apply_column_rules_integration_applies_disable_mask_and_desensitize(db_session):
    dataset_id = stamp()
    user_id = stamp()
    oid = stamp()
    fixture = await _insert_permission_fixture_data(db_session, dataset_id=dataset_id, user_id=user_id, oid=oid)
    now = timestamp_ms()
    try:
        db_session.add_all(
            [
                CoreColumnPermission(
                    id=stamp(),
                    dataset_id=dataset_id,
                    field_id=fixture["field_email_id"],
                    target_type="org",
                    target_id=oid,
                    action="mask",
                    enabled=True,
                    create_time=now,
                    update_time=now,
                ),
                CoreColumnPermission(
                    id=stamp(),
                    dataset_id=dataset_id,
                    field_id=fixture["field_email_id"],
                    target_type="user",
                    target_id=user_id,
                    action="disable",
                    enabled=True,
                    create_time=now,
                    update_time=now,
                ),
                CoreColumnPermission(
                    id=stamp(),
                    dataset_id=dataset_id,
                    field_id=fixture["field_phone_id"],
                    target_type="role",
                    target_id=fixture["role_id"],
                    action="mask",
                    enabled=True,
                    create_time=now,
                    update_time=now,
                ),
                CoreColumnPermission(
                    id=stamp(),
                    dataset_id=dataset_id,
                    field_id=fixture["field_ssn_id"],
                    target_type="org",
                    target_id=oid,
                    action="desensitize",
                    enabled=True,
                    create_time=now,
                    update_time=now,
                ),
            ]
        )
        await db_session.commit()

        service = DataPermissionService(db_session)
        fields = [{"name": "Email"}, {"name": "phone"}, {"name": "socialSecurity"}, {"name": "city"}]
        rows = [["alice@example.com", "13912345678", "123-45-6789", "Shanghai"]]

        new_fields, new_rows = await service.apply_column_rules(
            TokenUser(user_id=user_id, oid=oid), dataset_id, fields, rows
        )

        assert new_fields == [{"name": "phone"}, {"name": "socialSecurity"}, {"name": "city"}]
        assert new_rows == [["1*********8", "***", "Shanghai"]]
    finally:
        await _cleanup_permission_records(db_session, dataset_id=dataset_id, user_id=user_id, oid=oid)
