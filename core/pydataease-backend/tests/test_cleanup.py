from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class FakeShareRepo:
    def __init__(self) -> None:
        self.deleted_expired_before: int | None = None
        self._rowcount = 0

    async def delete_expired(self, exp_before: int) -> int:
        self.deleted_expired_before = exp_before
        return self._rowcount


class FakeExportRepo:
    def __init__(self) -> None:
        self.deleted_before_ms: int | None = None
        self._rowcount = 0

    async def delete_old_completed(self, before_ms: int) -> int:
        self.deleted_before_ms = before_ms
        return self._rowcount


@pytest.mark.asyncio
async def test_cleanup_expired_shares_deletes_expired() -> None:
    fake_repo = FakeShareRepo()
    fake_repo._rowcount = 5
    fake_session = AsyncMock()
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("app.tasks.cleanup.async_session", return_value=fake_session),
        patch("app.tasks.cleanup.ShareRepository", return_value=fake_repo),
    ):
        from app.tasks.cleanup import cleanup_expired_shares

        await cleanup_expired_shares()

    assert fake_repo.deleted_expired_before is not None
    assert fake_repo._rowcount == 5


@pytest.mark.asyncio
async def test_cleanup_expired_shares_nothing_to_delete() -> None:
    fake_repo = FakeShareRepo()
    fake_session = AsyncMock()
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("app.tasks.cleanup.async_session", return_value=fake_session),
        patch("app.tasks.cleanup.ShareRepository", return_value=fake_repo),
    ):
        from app.tasks.cleanup import cleanup_expired_shares

        await cleanup_expired_shares()

    assert fake_repo.deleted_expired_before is not None
    assert fake_repo._rowcount == 0


@pytest.mark.asyncio
async def test_cleanup_old_export_tasks_deletes_completed() -> None:
    fake_repo = FakeExportRepo()
    fake_repo._rowcount = 3
    fake_session = AsyncMock()
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("app.tasks.cleanup.async_session", return_value=fake_session),
        patch("app.tasks.cleanup.ExportTaskRepository", return_value=fake_repo),
    ):
        from app.tasks.cleanup import cleanup_old_export_tasks

        await cleanup_old_export_tasks()

    assert fake_repo.deleted_before_ms is not None
    assert fake_repo._rowcount == 3


@pytest.mark.asyncio
async def test_cleanup_old_export_tasks_respects_retention_env() -> None:
    fake_repo = FakeExportRepo()
    fake_session = AsyncMock()
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=False)

    retention_ms = 86_400_000  # 1 day
    with (
        patch("app.tasks.cleanup.async_session", return_value=fake_session),
        patch("app.tasks.cleanup.ExportTaskRepository", return_value=fake_repo),
        patch.dict("os.environ", {"DE_EXPORT_RETENTION_MS": str(retention_ms)}),
    ):
        from app.tasks.cleanup import cleanup_old_export_tasks

        await cleanup_old_export_tasks()

    assert fake_repo.deleted_before_ms is not None


@pytest.mark.asyncio
async def test_cleanup_old_export_tasks_nothing_to_delete() -> None:
    fake_repo = FakeExportRepo()
    fake_session = AsyncMock()
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("app.tasks.cleanup.async_session", return_value=fake_session),
        patch("app.tasks.cleanup.ExportTaskRepository", return_value=fake_repo),
    ):
        from app.tasks.cleanup import cleanup_old_export_tasks

        await cleanup_old_export_tasks()

    assert fake_repo.deleted_before_ms is not None
    assert fake_repo._rowcount == 0
