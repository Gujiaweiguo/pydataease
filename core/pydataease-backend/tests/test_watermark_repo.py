"""Unit tests for WatermarkRepository."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.watermark_repo import DEFAULT_ID, WatermarkRepository

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
    return WatermarkRepository(mock_session)


# -- get --


async def test_get_found(repo, mock_session):
    entity = MagicMock()
    mock_session.get.return_value = entity

    result = await repo.get()

    assert result is entity
    mock_session.get.assert_awaited_once()


async def test_get_not_found(repo, mock_session):
    mock_session.get.return_value = None

    result = await repo.get()

    assert result is None


# -- update (entity exists) --


async def test_update_existing(repo, mock_session):
    entity = MagicMock()
    entity.version = "1.0"
    mock_session.get.return_value = entity

    payload = {"version": "2.0", "setting_content": '{"opacity": 0.5}'}
    await repo.update(payload)

    assert entity.version == "2.0"
    assert entity.setting_content == '{"opacity": 0.5}'
    mock_session.add.assert_not_called()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


async def test_update_creates_new_when_not_found(repo, mock_session):
    mock_session.get.return_value = None

    payload = {"version": "1.0", "setting_content": "{}"}
    await repo.update(payload)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


async def test_default_id_constant():
    assert DEFAULT_ID == "system_default"
