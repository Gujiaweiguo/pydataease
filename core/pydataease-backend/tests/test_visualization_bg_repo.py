"""Unit tests for VisualizationBackgroundRepository."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.visualization_bg_repo import VisualizationBackgroundRepository

pytestmark = [pytest.mark.asyncio]


def _make_scalar_result(items: list):
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    return result


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def repo(mock_session):
    return VisualizationBackgroundRepository(mock_session)


# -- list_all --


async def test_list_all_returns_backgrounds(repo, mock_session):
    bg1, bg2 = MagicMock(), MagicMock()
    mock_session.execute.return_value = _make_scalar_result([bg1, bg2])

    result = await repo.list_all()

    assert len(result) == 2
    mock_session.execute.assert_awaited_once()


async def test_list_all_empty(repo, mock_session):
    mock_session.execute.return_value = _make_scalar_result([])

    result = await repo.list_all()

    assert result == []
