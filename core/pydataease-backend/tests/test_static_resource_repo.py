"""Unit tests for StaticResourceRepository."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.static_resource_repo import StaticResourceRepository

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.get = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def repo(mock_session):
    return StaticResourceRepository(mock_session)


# -- get_by_id --


async def test_get_by_id_found(repo, mock_session):
    entity = MagicMock()
    mock_session.get.return_value = entity

    result = await repo.get_by_id("res-1")

    assert result is entity


async def test_get_by_id_not_found(repo, mock_session):
    mock_session.get.return_value = None

    result = await repo.get_by_id("missing")

    assert result is None


# -- create (delegates to base) --


async def test_create(repo, mock_session):
    entity = MagicMock()
    mock_session.refresh.return_value = entity

    payload = {"name": "logo.png", "content": "base64data"}
    await repo.create(payload)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


# -- update (delegates to base) --


async def test_update(repo, mock_session):
    entity = MagicMock()
    mock_session.refresh.return_value = entity

    payload = {"content": "new-data"}
    await repo.update(entity, payload)

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()
