from __future__ import annotations

import os
import time
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.test_factories import cleanup_groups as _cleanup_groups  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import stamp as _stamp  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import timestamp_ms as _timestamp_ms  # pyright: ignore[reportImplicitRelativeImport]

from app.repositories.dataset_repo import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetFieldRepository,
    DatasetGroupRepository,
    DatasetTableRepository,
)
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.dataset import DatasetGroupCreate  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_service import DatasetService  # pyright: ignore[reportImplicitRelativeImport]

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        os.getenv("DE_E2E") != "1",
        reason="Requires PostgreSQL (set DE_E2E=1)",
    ),
]


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


def _service(session: AsyncSession) -> DatasetService:
    return DatasetService(
        session=session,
        group_repo=DatasetGroupRepository(session),
        table_repo=DatasetTableRepository(session),
        field_repo=DatasetFieldRepository(session),
    )


def _group_payload(
    stamp: int,
    *,
    name_prefix: str,
    pid: int | None = None,
    level: int = 0,
    node_type: str = "folder",
) -> dict[str, object]:
    now = _timestamp_ms()
    return {
        "id": _stamp(),
        "name": f"{name_prefix}-{stamp}",
        "pid": pid,
        "level": level,
        "node_type": node_type,
        "type": None,
        "mode": None,
        "info": None,
        "create_by": "7",
        "create_time": now,
        "update_by": "7",
        "last_update_time": now,
        "is_cross": None,
    }


def _table_payload(stamp: int, *, group_id: int, name_prefix: str) -> dict[str, object]:
    return {
        "id": _stamp(),
        "name": f"{name_prefix}-{stamp}",
        "table_name": f"table_{name_prefix}_{stamp}",
        "datasource_id": None,
        "dataset_group_id": group_id,
        "type": "db",
        "info": None,
    }


def _field_payload(*, group_id: int, table_id: int | None, origin_name: str, column_index: int) -> dict[str, object]:
    return {
        "id": _stamp(),
        "datasource_id": None,
        "dataset_table_id": table_id,
        "dataset_group_id": group_id,
        "chart_id": None,
        "origin_name": origin_name,
        "name": origin_name,
        "dataease_name": origin_name,
        "field_short_name": origin_name,
        "group_type": "d",
        "type": "VARCHAR",
        "size": 255,
        "de_type": 0,
        "de_extract_type": 0,
        "ext_field": 0,
        "checked": True,
        "column_index": column_index,
    }


class TestDatasetPerformance:
    async def test_tree_time_with_hundred_groups_under_two_seconds(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        svc = _service(db_session)
        created_ids: list[int] = []
        try:
            stamp = _stamp()
            for index in range(100):
                created = await group_repo.create(_group_payload(stamp + index, name_prefix=f"perf-tree-{index}"))
                created_ids.append(created.id)

            start = time.monotonic()
            tree = await svc.tree()
            elapsed = time.monotonic() - start

            assert elapsed < 2.0, f"Operation took {elapsed:.3f}s, expected < 2.0s"
            assert len(tree) == 1
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_get_details_time_with_fifty_fields_under_one_second(self, db_session: AsyncSession) -> None:
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        svc = _service(db_session)
        created_ids: list[int] = []
        try:
            stamp = _stamp()
            dataset = await svc.create(
                DatasetGroupCreate(name=f"perf-details-{stamp}", pid=0, node_type="dataset"),
                _user(),
            )
            created_ids.append(dataset.id)
            table = await table_repo.create(_table_payload(stamp, group_id=dataset.id, name_prefix="perf-details"))
            for index in range(50):
                await field_repo.create(
                    _field_payload(
                        group_id=dataset.id,
                        table_id=table.id,
                        origin_name=f"field_{index}",
                        column_index=index,
                    )
                )

            start = time.monotonic()
            payload = cast(dict[str, Any], await svc.get_details(dataset.id))
            elapsed = time.monotonic() - start

            assert elapsed < 1.0, f"Operation took {elapsed:.3f}s, expected < 1.0s"
            assert len(payload["allFields"]) == 50
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_delete_cascade_time_for_five_level_hierarchy_under_two_seconds(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        created_ids: list[int] = []
        stamp = _stamp()
        current = await group_repo.create(_group_payload(stamp, name_prefix="perf-delete-root"))
        created_ids.append(current.id)
        try:
            for level in range(1, 5):
                current = await group_repo.create(
                    _group_payload(stamp + level, name_prefix=f"perf-delete-level-{level}", pid=current.id, level=level)
                )

            start = time.monotonic()
            await group_repo.delete_cascade(created_ids[0])
            elapsed = time.monotonic() - start

            assert elapsed < 2.0, f"Operation took {elapsed:.3f}s, expected < 2.0s"
            assert await group_repo.get_by_id(created_ids[0]) is None
            created_ids.clear()
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_list_all_ordered_time_with_twenty_groups_under_one_second(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        created_ids: list[int] = []
        try:
            stamp = _stamp()
            for index in range(20):
                created = await group_repo.create(_group_payload(stamp + index, name_prefix=f"perf-list-{index}"))
                created_ids.append(created.id)

            start = time.monotonic()
            rows = await group_repo.list_all_ordered()
            elapsed = time.monotonic() - start

            assert elapsed < 1.0, f"Operation took {elapsed:.3f}s, expected < 1.0s"
            assert len(rows) >= 20
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_list_by_group_time_after_bulk_save_field_under_half_second(self, db_session: AsyncSession) -> None:
        group_repo = DatasetGroupRepository(db_session)
        table_repo = DatasetTableRepository(db_session)
        field_repo = DatasetFieldRepository(db_session)
        created_ids: list[int] = []
        try:
            stamp = _stamp()
            dataset = await group_repo.create(
                _group_payload(stamp, name_prefix="perf-field-dataset", node_type="dataset")
            )
            created_ids.append(dataset.id)
            table = await table_repo.create(_table_payload(stamp, group_id=dataset.id, name_prefix="perf-field"))
            for index in range(10):
                await field_repo.save_field(
                    _field_payload(
                        group_id=dataset.id,
                        table_id=table.id,
                        origin_name=f"bulk_field_{index}",
                        column_index=index,
                    )
                )

            start = time.monotonic()
            rows = await field_repo.list_by_group(dataset.id)
            elapsed = time.monotonic() - start

            assert elapsed < 0.5, f"Operation took {elapsed:.3f}s, expected < 0.5s"
            assert len(rows) == 10
        finally:
            await _cleanup_groups(db_session, created_ids)
