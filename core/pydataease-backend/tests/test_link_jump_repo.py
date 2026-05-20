from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.link_jump_repo import LinkJumpFieldRepository, LinkJumpRepository


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def repo(mock_session):
    return LinkJumpRepository(mock_session)


@pytest.fixture
def field_repo(mock_session):
    return LinkJumpFieldRepository(mock_session)


def _mock_scalars_all(items):
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    return result


def _mock_row_mapping(data: dict):
    row = MagicMock()
    row._mapping = data
    return row


def _mock_fetchall(rows):
    result = MagicMock()
    result.fetchall.return_value = rows
    return result


def _mock_scalar_one_or_none(item):
    result = MagicMock()
    result.scalar_one_or_none.return_value = item
    return result


def _mock_fetchone(row):
    result = MagicMock()
    result.fetchone.return_value = row
    return result


@pytest.mark.asyncio
async def test_get_jump_by_id_found(repo, mock_session):
    jump = MagicMock()
    mock_session.get.return_value = jump
    result = await repo.get_jump_by_id(100)
    assert result is jump


@pytest.mark.asyncio
async def test_get_jump_by_id_not_found(repo, mock_session):
    mock_session.get.return_value = None
    result = await repo.get_jump_by_id(999)
    assert result is None


@pytest.mark.asyncio
async def test_get_jump_info_by_id_found(repo, mock_session):
    info = MagicMock()
    mock_session.get.return_value = info
    result = await repo.get_jump_info_by_id(200)
    assert result is info


@pytest.mark.asyncio
async def test_get_jump_info_by_id_not_found(repo, mock_session):
    mock_session.get.return_value = None
    result = await repo.get_jump_info_by_id(999)
    assert result is None


@pytest.mark.asyncio
async def test_create_jump(repo, mock_session):
    payload = {"id": 1, "source_dv_id": 10, "source_view_id": 20}
    await repo.create_jump(payload)
    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_jump_info(repo, mock_session):
    payload = {"id": 2, "link_jump_id": 1, "link_type": "outer"}
    await repo.create_jump_info(payload)
    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_target_view_info(repo, mock_session):
    payload = {"target_id": 3, "link_jump_info_id": 2}
    await repo.create_target_view_info(payload)
    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_query_jumps_by_dv_id(repo, mock_session):
    jumps = [MagicMock(), MagicMock()]
    mock_session.execute.return_value = _mock_scalars_all(jumps)
    result = await repo.query_jumps_by_dv_id(dv_id=100)
    assert result == jumps
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_query_jumps_by_dv_id_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_scalars_all([])
    result = await repo.query_jumps_by_dv_id(dv_id=100)
    assert result == []


@pytest.mark.asyncio
async def test_query_jump_by_dv_and_view_found(repo, mock_session):
    jump = MagicMock()
    mock_session.execute.return_value = _mock_scalar_one_or_none(jump)
    result = await repo.query_jump_by_dv_and_view(dv_id=100, view_id=200)
    assert result is jump


@pytest.mark.asyncio
async def test_query_jump_by_dv_and_view_not_found(repo, mock_session):
    mock_session.execute.return_value = _mock_scalar_one_or_none(None)
    result = await repo.query_jump_by_dv_and_view(dv_id=100, view_id=200)
    assert result is None


@pytest.mark.asyncio
async def test_query_jump_infos_by_jump_id(repo, mock_session):
    infos = [MagicMock(), MagicMock()]
    mock_session.execute.return_value = _mock_scalars_all(infos)
    result = await repo.query_jump_infos_by_jump_id(jump_id=1)
    assert result == infos


@pytest.mark.asyncio
async def test_query_jump_infos_by_jump_id_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_scalars_all([])
    result = await repo.query_jump_infos_by_jump_id(jump_id=999)
    assert result == []


@pytest.mark.asyncio
async def test_query_target_view_infos_by_info_id(repo, mock_session):
    targets = [MagicMock()]
    mock_session.execute.return_value = _mock_scalars_all(targets)
    result = await repo.query_target_view_infos_by_info_id(info_id=5)
    assert result == targets


@pytest.mark.asyncio
async def test_query_target_view_infos_by_info_id_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_scalars_all([])
    result = await repo.query_target_view_infos_by_info_id(info_id=999)
    assert result == []


@pytest.mark.asyncio
async def test_query_jumps_with_active_flag_snapshot_tables(repo, mock_session):
    rows = [_mock_row_mapping({"source_view_id": 1, "id": 10, "checked": True})]
    mock_session.execute.return_value = _mock_fetchall(rows)
    result = await repo.query_jumps_with_active_flag(dv_id=100, table_name="snapshot")
    assert len(result) == 1
    assert result[0]["source_view_id"] == 1
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_query_jumps_with_active_flag_core_tables(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await repo.query_jumps_with_active_flag(dv_id=100, table_name="core")
    assert result == []
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_query_jump_detail_with_view_id_found(repo, mock_session):
    row = _mock_row_mapping({"source_view_id": 1, "id": 10, "checked": True})
    mock_session.execute.return_value = _mock_fetchone(row)
    result = await repo.query_jump_detail_with_view_id(
        dv_id=100, view_id=200, uid=1, table_name="snapshot"
    )
    assert result is not None
    assert result["source_view_id"] == 1


@pytest.mark.asyncio
async def test_query_jump_detail_with_view_id_not_found(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchone(None)
    result = await repo.query_jump_detail_with_view_id(
        dv_id=100, view_id=200, uid=1, table_name="core"
    )
    assert result is None


@pytest.mark.asyncio
async def test_query_link_jump_info_with_fields(repo, mock_session):
    row1 = _mock_row_mapping({"source_field_id": 1, "id": 10})
    row2 = _mock_row_mapping({"source_field_id": 2, "id": 20})
    mock_session.execute.return_value = _mock_fetchall([row1, row2])
    result = await repo.query_link_jump_info_with_fields(
        jump_id=1, source_view_id=100, uid=1, table_name="core"
    )
    assert len(result) == 2


@pytest.mark.asyncio
async def test_query_link_jump_info_with_fields_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await repo.query_link_jump_info_with_fields(
        jump_id=1, source_view_id=100, uid=1, table_name="snapshot"
    )
    assert result == []


@pytest.mark.asyncio
async def test_get_target_jump_info(repo, mock_session):
    row = _mock_row_mapping({"sourceInfo": "1#2#3", "targetInfo": "4#5"})
    mock_session.execute.return_value = _mock_fetchall([row])
    result = await repo.get_target_jump_info(
        source_dv_id=100, source_view_id=200, target_dv_id=300
    )
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_target_jump_info_with_source_field_id(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await repo.get_target_jump_info(
        source_dv_id=100, source_view_id=200, target_dv_id=300, source_field_id=50
    )
    assert result == []


@pytest.mark.asyncio
async def test_get_view_table_details(repo, mock_session):
    row = _mock_row_mapping({"id": 1, "title": "Chart 1", "field_id": 10})
    mock_session.execute.return_value = _mock_fetchall([row])
    result = await repo.get_view_table_details(dv_id=100)
    assert len(result) == 1
    assert result[0]["id"] == 1


@pytest.mark.asyncio
async def test_get_view_table_details_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await repo.get_view_table_details(dv_id=100)
    assert result == []


@pytest.mark.asyncio
async def test_query_out_params_target_with_dv_id(repo, mock_session):
    row = _mock_row_mapping({"id": 1, "name": "param1", "type": "outerParams"})
    mock_session.execute.return_value = _mock_fetchall([row])
    result = await repo.query_out_params_target_with_dv_id(dv_id=100)
    assert len(result) == 1
    assert result[0]["type"] == "outerParams"


@pytest.mark.asyncio
async def test_query_out_params_target_with_dv_id_empty(repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await repo.query_out_params_target_with_dv_id(dv_id=100)
    assert result == []


@pytest.mark.asyncio
async def test_delete_jump_target_view_info_snapshot(repo, mock_session):
    await repo.delete_jump_target_view_info(dv_id=100, view_id=200, table_name="snapshot")
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_jump_target_view_info_core(repo, mock_session):
    await repo.delete_jump_target_view_info(dv_id=100, view_id=200, table_name="core")
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_jump_info_snapshot(repo, mock_session):
    await repo.delete_jump_info(dv_id=100, view_id=200, table_name="snapshot")
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_jump_info_core(repo, mock_session):
    await repo.delete_jump_info(dv_id=100, view_id=200, table_name="core")
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_jump_snapshot(repo, mock_session):
    await repo.delete_jump(dv_id=100, view_id=200, table_name="snapshot")
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_jump_core(repo, mock_session):
    await repo.delete_jump(dv_id=100, view_id=200, table_name="core")
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_all_for_visualization_snapshot(repo, mock_session):
    await repo.delete_all_for_visualization(dv_id=100, table_name="snapshot")
    assert mock_session.execute.await_count == 4


@pytest.mark.asyncio
async def test_delete_all_for_visualization_core(repo, mock_session):
    await repo.delete_all_for_visualization(dv_id=100, table_name="core")
    assert mock_session.execute.await_count == 4


@pytest.mark.asyncio
async def test_query_table_field_with_view_id(field_repo, mock_session):
    row = _mock_row_mapping({"id": 1, "name": "field1", "de_type": 0})
    mock_session.execute.return_value = _mock_fetchall([row])
    result = await field_repo.query_table_field_with_view_id(view_id=100)
    assert len(result) == 1
    assert result[0]["name"] == "field1"


@pytest.mark.asyncio
async def test_query_table_field_with_view_id_empty(field_repo, mock_session):
    mock_session.execute.return_value = _mock_fetchall([])
    result = await field_repo.query_table_field_with_view_id(view_id=100)
    assert result == []
