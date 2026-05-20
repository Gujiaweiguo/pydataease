from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.outer_params_repo import OuterParamsRepository


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def repo(mock_session):
    return OuterParamsRepository(mock_session)


def _mock_row_mapping(data):
    row = MagicMock()
    row._mapping = data
    return row


def _mock_fetchall(rows):
    result = MagicMock()
    result.fetchall.return_value = rows
    return result


def _mock_fetchone(row):
    result = MagicMock()
    result.fetchone.return_value = row
    return result


@pytest.mark.asyncio
async def test_query_with_visualization_id_found(repo, mock_session):
    row = _mock_row_mapping({"visualization_id": 100, "checked": True})
    mock_session.execute.return_value = _mock_fetchone(row)
    result = await repo.query_with_visualization_id("100")
    assert result is not None
    assert result["visualization_id"] == 100


@pytest.mark.asyncio
async def test_query_with_visualization_id_not_found(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchone(None)
    result = await repo.query_with_visualization_id("999")
    assert result is None


@pytest.mark.asyncio
async def test_query_outer_params_info_snapshot(repo, mock_session):
    row1 = _mock_row_mapping({"params_info_id": "p1", "param_name": "x"})
    row2 = _mock_row_mapping({"params_info_id": "p2", "param_name": "y"})
    mock_session.execute.return_value = _mock_fetchall([row1, row2])
    result = await repo.query_outer_params_info_snapshot(visualization_id="100")
    assert len(result) == 2


@pytest.mark.asyncio
async def test_query_outer_params_info_snapshot_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await repo.query_outer_params_info_snapshot(visualization_id="100")
    assert result == []


@pytest.mark.asyncio
async def test_get_outer_params_info(repo, mock_session):
    row = _mock_row_mapping({"sourceInfo": "param1", "targetInfo": "10#20#1"})
    mock_session.execute.return_value = _mock_fetchall([row])
    result = await repo.get_outer_params_info(visualization_id="100")
    assert len(result) == 1
    assert result[0]["sourceInfo"] == "param1"


@pytest.mark.asyncio
async def test_get_outer_params_info_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await repo.get_outer_params_info(visualization_id="100")
    assert result == []


@pytest.mark.asyncio
async def test_get_outer_params_info_base(repo, mock_session):
    row = _mock_row_mapping({"param_name": "p1", "params_info_id": "info1"})
    mock_session.execute.return_value = _mock_fetchall([row])
    result = await repo.get_outer_params_info_base(visualization_id="100")
    assert len(result) == 1
    assert result[0]["param_name"] == "p1"


@pytest.mark.asyncio
async def test_get_outer_params_info_base_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await repo.get_outer_params_info_base(visualization_id="100")
    assert result == []


@pytest.mark.asyncio
async def test_query_ds_with_visualization_id(repo, mock_session):
    row = _mock_row_mapping({"id": 1, "name": "ds1", "visualizationId": "100"})
    mock_session.execute.return_value = _mock_fetchall([row])
    result = await repo.query_ds_with_visualization_id(visualization_id="100")
    assert len(result) == 1
    assert result[0]["name"] == "ds1"


@pytest.mark.asyncio
async def test_query_ds_with_visualization_id_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await repo.query_ds_with_visualization_id(visualization_id="100")
    assert result == []


@pytest.mark.asyncio
async def test_query_ds_fields(repo, mock_session):
    row = _mock_row_mapping({"id": 1, "attachId": 1, "name": "field1"})
    mock_session.execute.return_value = _mock_fetchall([row])
    result = await repo.query_ds_fields(dataset_group_id=50)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_query_ds_fields_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await repo.query_ds_fields(dataset_group_id=999)
    assert result == []


@pytest.mark.asyncio
async def test_query_ds_views(repo, mock_session):
    row = _mock_row_mapping({"chartId": 1, "chartName": "Chart 1", "chartType": "bar"})
    mock_session.execute.return_value = _mock_fetchall([row])
    result = await repo.query_ds_views(dataset_group_id=50, visualization_id="100")
    assert len(result) == 1
    assert result[0]["chartType"] == "bar"


@pytest.mark.asyncio
async def test_query_ds_views_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await repo.query_ds_views(dataset_group_id=50, visualization_id="100")
    assert result == []


@pytest.mark.asyncio
async def test_delete_target_view_info_snapshot(repo, mock_session):
    await repo.delete_target_view_info_snapshot(visualization_id="100")
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_params_info_snapshot(repo, mock_session):
    await repo.delete_params_info_snapshot(visualization_id="100")
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_outer_params_snapshot(repo, mock_session):
    await repo.delete_outer_params_snapshot(visualization_id="100")
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_insert_outer_params_snapshot(repo, mock_session):
    payload = {"params_id": "p1", "visualization_id": "100", "checked": True}
    await repo.insert_outer_params_snapshot(payload)
    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_insert_params_info_snapshot(repo, mock_session):
    payload = {"params_info_id": "pi1", "params_id": "p1", "param_name": "x"}
    await repo.insert_params_info_snapshot(payload)
    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_insert_target_view_info_snapshot(repo, mock_session):
    payload = {"target_id": "t1", "params_info_id": "pi1", "target_view_id": "v1"}
    await repo.insert_target_view_info_snapshot(payload)
    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()
