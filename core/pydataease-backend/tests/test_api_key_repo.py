"""Unit tests for ApiKeyRepository."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.api_key_repo import ApiKeyRepository

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def repo(mock_session):
    return ApiKeyRepository(mock_session)


def _make_scalar_result(items: list):
    """Build a mock that supports result.scalars().all() chain."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    return result


# -- list_by_creator --


async def test_list_by_creator_returns_keys(repo, mock_session):
    key1 = MagicMock()
    key2 = MagicMock()
    mock_session.execute.return_value = _make_scalar_result([key1, key2])

    result = await repo.list_by_creator(creator=42)

    assert len(result) == 2
    mock_session.execute.assert_awaited_once()


async def test_list_by_creator_empty(repo, mock_session):
    mock_session.execute.return_value = _make_scalar_result([])

    result = await repo.list_by_creator(creator=99)

    assert result == []


# -- get_by_id (delegates to base) --


async def test_get_by_id_found(repo, mock_session):
    entity = MagicMock()
    mock_session.get.return_value = entity

    result = await repo.get_by_id(123)

    assert result is entity


async def test_get_by_id_not_found(repo, mock_session):
    mock_session.get.return_value = None

    result = await repo.get_by_id(999)

    assert result is None


# -- create (delegates to base) --


async def test_create(repo, mock_session):
    entity = MagicMock()
    mock_session.refresh.return_value = entity

    payload = {"access_key": "ak-123", "access_secret": "sk-456", "creator": 1}
    await repo.create(payload)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


# -- update (delegates to base) --


async def test_update(repo, mock_session):
    entity = MagicMock()
    mock_session.refresh.return_value = entity

    payload = {"name": "updated-key"}
    await repo.update(entity, payload)

    mock_session.commit.assert_awaited_once()


# -- delete (delegates to base) --


async def test_delete(repo, mock_session):
    entity = MagicMock()

    await repo.delete(entity)

    mock_session.delete.assert_awaited_once_with(entity)
    mock_session.commit.assert_awaited_once()
