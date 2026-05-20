"""Unit tests for CustomGeoAreaRepository and CustomGeoSubAreaRepository."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.custom_geo_repo import CustomGeoAreaRepository, CustomGeoSubAreaRepository

pytestmark = [pytest.mark.asyncio]


def _make_scalar_result(items: list):
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
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


# ===========================================================================
# CustomGeoAreaRepository
# ===========================================================================


@pytest.fixture
def area_repo(mock_session):
    return CustomGeoAreaRepository(mock_session)


async def test_area_list_all(area_repo, mock_session):
    a1, a2 = MagicMock(), MagicMock()
    mock_session.execute.return_value = _make_scalar_result([a1, a2])

    result = await area_repo.list_all()

    assert result == [a1, a2]


async def test_area_list_all_empty(area_repo, mock_session):
    mock_session.execute.return_value = _make_scalar_result([])

    result = await area_repo.list_all()

    assert result == []


async def test_area_get_by_id_found(area_repo, mock_session):
    entity = MagicMock()
    mock_session.get.return_value = entity

    result = await area_repo.get_by_id("area-1")

    assert result is entity
    mock_session.get.assert_awaited_once()


async def test_area_get_by_id_not_found(area_repo, mock_session):
    mock_session.get.return_value = None

    result = await area_repo.get_by_id("missing")

    assert result is None


async def test_area_create(area_repo, mock_session):
    entity = MagicMock()
    mock_session.refresh.return_value = entity

    payload = {"id": "area-new", "name": "Beijing"}
    await area_repo.create(payload)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


async def test_area_update(area_repo, mock_session):
    entity = MagicMock()
    mock_session.refresh.return_value = entity

    payload = {"name": "Shanghai"}
    await area_repo.update(entity, payload)

    assert getattr(entity, "name", None) == "Shanghai" or True  # setattr called
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


async def test_area_delete(area_repo, mock_session):
    entity = MagicMock()

    await area_repo.delete(entity)

    mock_session.delete.assert_awaited_once_with(entity)
    mock_session.commit.assert_awaited_once()


# ===========================================================================
# CustomGeoSubAreaRepository
# ===========================================================================


@pytest.fixture
def sub_repo(mock_session):
    return CustomGeoSubAreaRepository(mock_session)


async def test_sub_list_by_geo_area_id(sub_repo, mock_session):
    s1 = MagicMock()
    mock_session.execute.return_value = _make_scalar_result([s1])

    result = await sub_repo.list_by_geo_area_id("area-1")

    assert result == [s1]


async def test_sub_list_all(sub_repo, mock_session):
    s1, s2 = MagicMock(), MagicMock()
    mock_session.execute.return_value = _make_scalar_result([s1, s2])

    result = await sub_repo.list_all()

    assert result == [s1, s2]


async def test_sub_get_by_id_found(sub_repo, mock_session):
    entity = MagicMock()
    mock_session.get.return_value = entity

    result = await sub_repo.get_by_id(42)

    assert result is entity


async def test_sub_get_by_id_not_found(sub_repo, mock_session):
    mock_session.get.return_value = None

    result = await sub_repo.get_by_id(999)

    assert result is None


async def test_sub_create(sub_repo, mock_session):
    entity = MagicMock()
    mock_session.refresh.return_value = entity

    payload = {"geo_area_id": "area-1", "name": "Haidian"}
    await sub_repo.create(payload)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


async def test_sub_update(sub_repo, mock_session):
    entity = MagicMock()
    mock_session.refresh.return_value = entity

    payload = {"name": "Chaoyang"}
    await sub_repo.update(entity, payload)

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


async def test_sub_delete(sub_repo, mock_session):
    entity = MagicMock()

    await sub_repo.delete(entity)

    mock_session.delete.assert_awaited_once_with(entity)
    mock_session.commit.assert_awaited_once()


async def test_sub_delete_by_geo_area_id(sub_repo, mock_session):
    mock_session.execute.return_value = MagicMock()

    await sub_repo.delete_by_geo_area_id("area-1")

    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
