"""Unit tests for MenuRepository (system_repo)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.system_repo import MenuRepository

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
    return MenuRepository(mock_session)


# -- list_all --


async def test_list_all_returns_menus(repo, mock_session):
    m1, m2, m3 = MagicMock(), MagicMock(), MagicMock()
    mock_session.execute.return_value = _make_scalar_result([m1, m2, m3])

    result = await repo.list_all()

    assert len(result) == 3
    mock_session.execute.assert_awaited_once()


async def test_list_all_empty(repo, mock_session):
    mock_session.execute.return_value = _make_scalar_result([])

    result = await repo.list_all()

    assert result == []
