from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repositories.export_repo import ExportTaskRepository


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def repo(mock_session):
    return ExportTaskRepository(mock_session)


def _mock_scalars_all(items):
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    return result


def _make_task(**overrides):
    defaults = {
        "id": "task-1",
        "user_id": 42,
        "export_from": 1,
        "export_status": "SUCCESS",
        "export_time": 1700000000,
        "file_name": "test.xlsx",
    }
    defaults.update(overrides)
    obj = MagicMock()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


@pytest.mark.asyncio
async def test_get_by_id_found(repo, mock_session):
    task = _make_task()
    mock_session.get.return_value = task
    result = await repo.get_by_id("task-1")
    mock_session.get.assert_awaited_once()
    assert result is task


@pytest.mark.asyncio
async def test_get_by_id_not_found(repo, mock_session):
    mock_session.get.return_value = None
    result = await repo.get_by_id("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_list_by_user_and_from(repo, mock_session):
    tasks = [_make_task(id="t1"), _make_task(id="t2")]
    mock_session.execute.return_value = _mock_scalars_all(tasks)
    result = await repo.list_by_user_and_from(user_id=42, export_from=1)
    assert result == tasks
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_by_user_and_from_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_scalars_all([])
    result = await repo.list_by_user_and_from(user_id=42, export_from=1)
    assert result == []


@pytest.mark.asyncio
async def test_list_by_user(repo, mock_session):
    tasks = [_make_task(id="t1"), _make_task(id="t2")]
    mock_session.execute.return_value = _mock_scalars_all(tasks)
    result = await repo.list_by_user(user_id=42)
    assert result == tasks
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_by_user_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_scalars_all([])
    result = await repo.list_by_user(user_id=42)
    assert result == []


@pytest.mark.asyncio
async def test_count_by_user_grouped_by_status(repo, mock_session):
    result = MagicMock()
    result.all.return_value = [("RUNNING", 2), ("SUCCESS", 5), ("FAILED", 1)]
    mock_session.execute.return_value = result
    out = await repo.count_by_user_grouped_by_status(user_id=42)
    assert out["ALL"] == 8
    assert out["IN_PROGRESS"] == 2
    assert out["SUCCESS"] == 5
    assert out["FAILED"] == 1
    assert out["PENDING"] == 0


@pytest.mark.asyncio
async def test_count_by_user_grouped_by_status_empty(repo, mock_session):
    result = MagicMock()
    result.all.return_value = []
    mock_session.execute.return_value = result
    out = await repo.count_by_user_grouped_by_status(user_id=42)
    assert out["ALL"] == 0
    assert out["IN_PROGRESS"] == 0
    assert out["SUCCESS"] == 0
    assert out["FAILED"] == 0
    assert out["PENDING"] == 0


@pytest.mark.asyncio
async def test_count_by_user_initiated_status(repo, mock_session):
    result = MagicMock()
    result.all.return_value = [("INITIATED", 3)]
    mock_session.execute.return_value = result
    out = await repo.count_by_user_grouped_by_status(user_id=42)
    assert out["ALL"] == 3
    assert out["IN_PROGRESS"] == 3
    assert out["PENDING"] == 3


@pytest.mark.asyncio
async def test_list_paginated_success_status(repo, mock_session):
    tasks = [_make_task(id="t1")]
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    data_result = _mock_scalars_all(tasks)
    mock_session.execute.side_effect = [count_result, data_result]
    total, items = await repo.list_paginated_by_user_and_status(
        user_id=42, status="success", offset=0, limit=10
    )
    assert total == 1
    assert items == tasks


@pytest.mark.asyncio
async def test_list_paginated_failed_status(repo, mock_session):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 2
    data_result = _mock_scalars_all([_make_task(id="t1"), _make_task(id="t2")])
    mock_session.execute.side_effect = [count_result, data_result]
    total, items = await repo.list_paginated_by_user_and_status(
        user_id=42, status="FAILED", offset=0, limit=10
    )
    assert total == 2
    assert len(items) == 2


@pytest.mark.asyncio
async def test_list_paginated_pending_status(repo, mock_session):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 0
    data_result = _mock_scalars_all([])
    mock_session.execute.side_effect = [count_result, data_result]
    total, items = await repo.list_paginated_by_user_and_status(
        user_id=42, status="PENDING", offset=0, limit=10
    )
    assert total == 0
    assert items == []


@pytest.mark.asyncio
async def test_list_paginated_in_progress_status(repo, mock_session):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 3
    data_result = _mock_scalars_all([_make_task(id="t1")])
    mock_session.execute.side_effect = [count_result, data_result]
    total, _items = await repo.list_paginated_by_user_and_status(
        user_id=42, status="IN_PROGRESS", offset=5, limit=5
    )
    assert total == 3


@pytest.mark.asyncio
async def test_list_paginated_all_status_no_filter(repo, mock_session):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 10
    data_result = _mock_scalars_all([_make_task(id="t1")])
    mock_session.execute.side_effect = [count_result, data_result]
    total, _items = await repo.list_paginated_by_user_and_status(
        user_id=42, status="ALL", offset=0, limit=5
    )
    assert total == 10


@pytest.mark.asyncio
async def test_list_paginated_count_none_defaults_to_zero(repo, mock_session):
    count_result = MagicMock()
    count_result.scalar_one.return_value = None
    data_result = _mock_scalars_all([])
    mock_session.execute.side_effect = [count_result, data_result]
    total, _items = await repo.list_paginated_by_user_and_status(
        user_id=42, status="SUCCESS", offset=0, limit=10
    )
    assert total == 0


@pytest.mark.asyncio
async def test_create(repo, mock_session):
    payload = {"id": "new-task", "user_id": 42}
    expected = _make_task()
    with patch.object(repo._base, "create", new_callable=AsyncMock, return_value=expected):
        result = await repo.create(payload)
        assert result is expected


@pytest.mark.asyncio
async def test_delete_by_id(repo, mock_session):
    await repo.delete_by_id("task-1")
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_by_user_and_from(repo, mock_session):
    await repo.delete_all_by_user_and_from(user_id=42, export_from=1)
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_by_user_and_status_success(repo, mock_session):
    await repo.delete_all_by_user_and_status(user_id=42, status="SUCCESS")
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_by_user_and_status_failed(repo, mock_session):
    await repo.delete_all_by_user_and_status(user_id=42, status="FAILED")
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_by_user_and_status_pending(repo, mock_session):
    await repo.delete_all_by_user_and_status(user_id=42, status="PENDING")
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_by_user_and_status_in_progress(repo, mock_session):
    await repo.delete_all_by_user_and_status(user_id=42, status="IN_PROGRESS")
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_by_user_and_status_all(repo, mock_session):
    await repo.delete_all_by_user_and_status(user_id=42, status="ALL")
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_ids(repo, mock_session):
    await repo.delete_by_ids(user_id=42, ids=["t1", "t2"])
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_by_ids_empty_list_early_return(repo, mock_session):
    await repo.delete_by_ids(user_id=42, ids=[])
    mock_session.execute.assert_not_awaited()
    mock_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_old_completed(repo, mock_session):
    result_mock = MagicMock()
    result_mock.rowcount = 7
    mock_session.execute.return_value = result_mock
    count = await repo.delete_old_completed(before_ms=1700000000)
    assert count == 7
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_old_completed_zero_deleted(repo, mock_session):
    result_mock = MagicMock()
    result_mock.rowcount = 0
    mock_session.execute.return_value = result_mock
    count = await repo.delete_old_completed(before_ms=1700000000)
    assert count == 0
