"""Unit tests for VisualizationSubjectRepository."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.visualization_subject_repo import VisualizationSubjectRepository

pytestmark = [pytest.mark.asyncio]


def _make_scalar_result(items: list):
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    return result


def _make_scalar_one_or_none(item=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = item
    return result


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def repo(mock_session):
    return VisualizationSubjectRepository(mock_session)


# -- list_active --


async def test_list_active_returns_active_subjects(repo, mock_session):
    s1 = MagicMock()
    mock_session.execute.return_value = _make_scalar_result([s1])

    result = await repo.list_active()

    assert len(result) == 1


async def test_list_active_empty(repo, mock_session):
    mock_session.execute.return_value = _make_scalar_result([])

    result = await repo.list_active()

    assert result == []


# -- get_by_id --


async def test_get_by_id_found(repo, mock_session):
    entity = MagicMock()
    mock_session.get.return_value = entity

    result = await repo.get_by_id("subj-1")

    assert result is entity


async def test_get_by_id_not_found(repo, mock_session):
    mock_session.get.return_value = None

    result = await repo.get_by_id("missing")

    assert result is None


# -- get_by_name --


async def test_get_by_name_found(repo, mock_session):
    entity = MagicMock()
    mock_session.execute.return_value = _make_scalar_one_or_none(entity)

    result = await repo.get_by_name("Dark Theme")

    assert result is entity


async def test_get_by_name_not_found(repo, mock_session):
    mock_session.execute.return_value = _make_scalar_one_or_none(None)

    result = await repo.get_by_name("Nonexistent")

    assert result is None


# -- create (delegates to base) --


async def test_create(repo, mock_session):
    entity = MagicMock()
    mock_session.refresh.return_value = entity

    payload = {"name": "New Theme"}
    await repo.create(payload)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


# -- update (delegates to base) --


async def test_update(repo, mock_session):
    entity = MagicMock()
    mock_session.refresh.return_value = entity

    payload = {"name": "Updated Theme"}
    await repo.update(entity, payload)

    mock_session.commit.assert_awaited_once()


# -- delete (delegates to base) --


async def test_delete(repo, mock_session):
    entity = MagicMock()

    await repo.delete(entity)

    mock_session.delete.assert_awaited_once_with(entity)
    mock_session.commit.assert_awaited_once()
