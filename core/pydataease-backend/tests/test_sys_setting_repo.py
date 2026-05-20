"""Unit tests for SysSettingRepository."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.sys_setting_repo import SysSettingRepository

pytestmark = [pytest.mark.asyncio]


def _make_scalar_result(items: list, first=None):
    """Build a mock supporting scalars().all() and scalars().first()."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    result.scalars.return_value.first.return_value = first
    return result


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def repo(mock_session):
    return SysSettingRepository(mock_session)


# -- get_by_key --


async def test_get_by_key_found(repo, mock_session):
    entity = MagicMock()
    mock_session.execute.return_value = _make_scalar_result([], first=entity)

    result = await repo.get_by_key("theme")

    assert result is entity


async def test_get_by_key_not_found(repo, mock_session):
    mock_session.execute.return_value = _make_scalar_result([], first=None)

    result = await repo.get_by_key("nonexistent")

    assert result is None


# -- list_by_type --


async def test_list_by_type(repo, mock_session):
    s1, s2 = MagicMock(), MagicMock()
    mock_session.execute.return_value = _make_scalar_result([s1, s2])

    result = await repo.list_by_type("setting")

    assert len(result) == 2


async def test_list_by_type_empty(repo, mock_session):
    mock_session.execute.return_value = _make_scalar_result([])

    result = await repo.list_by_type("other")

    assert result == []


# -- list_all --


async def test_list_all(repo, mock_session):
    s1 = MagicMock()
    mock_session.execute.return_value = _make_scalar_result([s1])

    result = await repo.list_all()

    assert len(result) == 1


# -- upsert (create new) --


async def test_upsert_create_new(repo, mock_session):
    # get_by_key returns None → create new
    mock_session.execute.return_value = _make_scalar_result([], first=None)
    entity = MagicMock()
    mock_session.refresh.return_value = entity

    await repo.upsert("new-key", "value1")

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


async def test_upsert_update_existing(repo, mock_session):
    existing = MagicMock()
    mock_session.execute.return_value = _make_scalar_result([], first=existing)

    await repo.upsert("existing-key", "new-value")

    assert existing.setting_value == "new-value"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()
    mock_session.add.assert_not_called()
