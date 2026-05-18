from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tests.fixtures.db_fixtures import PG_URL  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import cleanup_groups as _cleanup_groups  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import stamp as _stamp  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import timestamp_ms as _timestamp_ms  # pyright: ignore[reportImplicitRelativeImport]

from app.repositories.dataset_repo import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetFieldRepository,
    DatasetGroupRepository,
    DatasetTableRepository,
)
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.dataset import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetGroupCreate,
    DatasetGroupMove,
    DatasetGroupRename,
)
from app.services.dataset_service import DatasetService  # pyright: ignore[reportImplicitRelativeImport]

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        os.getenv("DE_E2E") != "1",
        reason="Requires PostgreSQL (set DE_E2E=1)",
    ),
]


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(PG_URL)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield factory
    await engine.dispose()


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


def _service(session: AsyncSession) -> DatasetService:
    return DatasetService(
        session=session,
        group_repo=DatasetGroupRepository(session),
        table_repo=DatasetTableRepository(session),
        field_repo=DatasetFieldRepository(session),
    )


def _group_payload(stamp: int, *, name_prefix: str, pid: int | None = None, level: int = 0) -> dict[str, object]:
    now = _timestamp_ms()
    return {
        "id": _stamp(),
        "name": f"{name_prefix}-{stamp}",
        "pid": pid,
        "level": level,
        "node_type": "folder",
        "type": None,
        "mode": None,
        "info": None,
        "create_by": "7",
        "create_time": now,
        "update_by": "7",
        "last_update_time": now,
        "is_cross": None,
    }


class TestDatasetConcurrency:
    async def test_create_dataset_from_two_concurrent_tasks(self, db_session: AsyncSession, session_factory: async_sessionmaker[AsyncSession]) -> None:
        created_ids: list[int] = []

        async def create_one(index: int) -> int:
            async with session_factory() as session:
                response = await _service(session).create(
                    DatasetGroupCreate(
                        name=f"concurrent-create-{_stamp()}-{index}",
                        pid=0,
                        node_type="dataset",
                    ),
                    _user(),
                )
                return response.id

        try:
            results = await asyncio.gather(create_one(1), create_one(2), return_exceptions=True)

            assert all(not isinstance(result, Exception) for result in results)
            created_ids.extend([result for result in results if isinstance(result, int)])
            assert len(created_ids) == 2
            repo = DatasetGroupRepository(db_session)
            for group_id in created_ids:
                assert await repo.get_by_id(group_id) is not None
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_rename_same_dataset_last_write_wins(self, db_session: AsyncSession, session_factory: async_sessionmaker[AsyncSession]) -> None:
        group_repo = DatasetGroupRepository(db_session)
        stamp = _stamp()
        created = await group_repo.create(_group_payload(stamp, name_prefix="concurrent-rename"))
        try:
            first_name = f"rename-first-{stamp}"
            second_name = f"rename-second-{stamp}"

            async def rename_to(name: str, delay: float) -> str:
                await asyncio.sleep(delay)
                async with session_factory() as session:
                    response = await _service(session).rename(
                        DatasetGroupRename(id=created.id, name=name),
                        _user(),
                    )
                    return response.name or ""

            results = await asyncio.gather(
                rename_to(first_name, 0.0),
                rename_to(second_name, 0.05),
                return_exceptions=True,
            )
            async with session_factory() as verify_session:
                stored = await DatasetGroupRepository(verify_session).get_by_id(created.id)

            assert results == [first_name, second_name]
            assert stored is not None
            assert stored.name == second_name
        finally:
            await _cleanup_groups(db_session, [created.id])

    async def test_delete_while_reading_returns_404_without_crash(self, db_session: AsyncSession, session_factory: async_sessionmaker[AsyncSession]) -> None:
        group_repo = DatasetGroupRepository(db_session)
        stamp = _stamp()
        created = await group_repo.create(_group_payload(stamp, name_prefix="concurrent-delete-read"))

        async def delete_group() -> None:
            async with session_factory() as session:
                await _service(session).delete(created.id)

        async def read_group() -> str:
            await asyncio.sleep(0.05)
            async with session_factory() as session:
                try:
                    await _service(session).get_details(created.id)
                    return "read"
                except HTTPException as exc:
                    assert exc.status_code == 404
                    return "404"

        results = await asyncio.gather(delete_group(), read_group(), return_exceptions=True)

        assert results[0] is None
        assert results[1] == "404"
        async with session_factory() as verify_session:
            assert await DatasetGroupRepository(verify_session).get_by_id(created.id) is None

    async def test_move_two_datasets_to_same_parent_concurrently(self, db_session: AsyncSession, session_factory: async_sessionmaker[AsyncSession]) -> None:
        group_repo = DatasetGroupRepository(db_session)
        stamp = _stamp()
        destination = await group_repo.create(_group_payload(stamp, name_prefix="concurrent-dest"))
        first = await group_repo.create(_group_payload(stamp, name_prefix="concurrent-move-a"))
        second = await group_repo.create(_group_payload(stamp, name_prefix="concurrent-move-b"))
        created_ids = [destination.id, first.id, second.id]
        try:
            async def move_one(group_id: int) -> int:
                async with session_factory() as session:
                    response = await _service(session).move(
                        DatasetGroupMove(id=group_id, pid=destination.id),
                        _user(),
                    )
                    return response.id

            results = await asyncio.gather(move_one(first.id), move_one(second.id), return_exceptions=True)
            async with session_factory() as verify_session:
                verify_repo = DatasetGroupRepository(verify_session)
                first_stored = await verify_repo.get_by_id(first.id)
                second_stored = await verify_repo.get_by_id(second.id)

            assert results == [first.id, second.id]
            assert first_stored is not None and first_stored.pid == destination.id and first_stored.level == 1
            assert second_stored is not None and second_stored.pid == destination.id and second_stored.level == 1
        finally:
            await _cleanup_groups(db_session, created_ids)

    async def test_create_ten_datasets_in_parallel(self, db_session: AsyncSession, session_factory: async_sessionmaker[AsyncSession]) -> None:
        created_ids: list[int] = []

        async def create_one(index: int) -> int:
            async with session_factory() as session:
                response = await _service(session).create(
                    DatasetGroupCreate(
                        name=f"parallel-dataset-{index}-{_stamp()}",
                        pid=0,
                        node_type="dataset",
                    ),
                    _user(),
                )
                return response.id

        try:
            results = await asyncio.gather(*(create_one(index) for index in range(10)), return_exceptions=True)

            assert all(isinstance(result, int) for result in results)
            created_ids.extend(result for result in results if isinstance(result, int))
            assert len(created_ids) == 10
            repo = DatasetGroupRepository(db_session)
            stored = [await repo.get_by_id(group_id) for group_id in created_ids]
            assert all(row is not None and row.node_type == "dataset" for row in stored)
        finally:
            await _cleanup_groups(db_session, created_ids)
