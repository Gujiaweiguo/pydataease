# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false

"""Coverage tests for custom_geo_service and geo_service."""

from __future__ import annotations

import os
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import TokenUser
from app.schemas.custom_geo import CustomGeoAreaCreate, CustomGeoSubAreaCreate
from app.schemas.geo import GeoMappingRequest, GeoSaveRequest
from app.services.custom_geo_service import CustomGeoService
from app.services.geo_service import GeoService, _geo_to_dict

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

pytestmark = [pytest.mark.asyncio]

_SKIP_DB = os.getenv("DE_E2E") != "1"


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


# ===========================================================================
# CustomGeoService - unit tests
# ===========================================================================


def _custom_geo_svc(
    *,
    area_list_all: list[Any] | None = None,
    area_get_by_id: Any | None = "UNSET",
    area_create: Any | None = "UNSET",
    area_update: Any | None = "UNSET",
    area_delete: AsyncMock | None = None,
    sub_list_all: list[Any] | None = None,
    sub_get_by_id: Any | None = "UNSET",
    sub_create: Any | None = "UNSET",
    sub_delete: AsyncMock | None = None,
    sub_delete_by_geo_area_id: AsyncMock | None = None,
) -> CustomGeoService:
    session = cast(AsyncSession, SimpleNamespace())
    svc = CustomGeoService(session)
    if area_list_all is not None:
        svc.area_repo.list_all = AsyncMock(return_value=area_list_all)  # type: ignore[attr-defined]
    if area_get_by_id != "UNSET":
        svc.area_repo.get_by_id = AsyncMock(return_value=area_get_by_id)  # type: ignore[attr-defined]
    if area_create != "UNSET":
        svc.area_repo.create = AsyncMock(return_value=area_create)  # type: ignore[attr-defined]
    if area_update != "UNSET":
        svc.area_repo.update = AsyncMock(return_value=area_update)  # type: ignore[attr-defined]
    if area_delete is not None:
        svc.area_repo.delete = area_delete  # type: ignore[attr-defined]
    if sub_list_all is not None:
        svc.sub_area_repo.list_all = AsyncMock(return_value=sub_list_all)  # type: ignore[attr-defined]
    if sub_get_by_id != "UNSET":
        svc.sub_area_repo.get_by_id = AsyncMock(return_value=sub_get_by_id)  # type: ignore[attr-defined]
    if sub_create != "UNSET":
        svc.sub_area_repo.create = AsyncMock(return_value=sub_create)  # type: ignore[attr-defined]
    if sub_delete is not None:
        svc.sub_area_repo.delete = sub_delete  # type: ignore[attr-defined]
    if sub_delete_by_geo_area_id is not None:
        svc.sub_area_repo.delete_by_geo_area_id = sub_delete_by_geo_area_id  # type: ignore[attr-defined]
    return svc


# -- list_areas --


async def test_custom_geo_list_areas():
    areas = [
        SimpleNamespace(id="a1", name="Beijing", create_by="7", create_time=1000, update_by=None, update_time=None),
        SimpleNamespace(id="a2", name="Shanghai", create_by="8", create_time=2000, update_by=None, update_time=None),
    ]
    svc = _custom_geo_svc(area_list_all=areas)
    result = await svc.list_areas()
    assert len(result) == 2
    assert result[0].name == "Beijing"


async def test_custom_geo_list_areas_empty():
    svc = _custom_geo_svc(area_list_all=[])
    result = await svc.list_areas()
    assert result == []


# -- get_area --


async def test_custom_geo_get_area_found():
    area = SimpleNamespace(id="a1", name="Beijing", create_by="7", create_time=1000, update_by=None, update_time=None)
    svc = _custom_geo_svc(area_get_by_id=area)
    result = await svc.get_area("a1")
    assert result is not None
    assert result.name == "Beijing"


async def test_custom_geo_get_area_not_found():
    svc = _custom_geo_svc(area_get_by_id=None)
    result = await svc.get_area("missing")
    assert result is None


# -- save_area (create new, no id) --


async def test_custom_geo_save_area_create():
    created = SimpleNamespace(id="new-id", name="Shenzhen", create_by="7", create_time=9999, update_by=None, update_time=None)
    svc = _custom_geo_svc(area_create=created)
    payload = CustomGeoAreaCreate(name="Shenzhen")
    result = await svc.save_area(payload, _user())
    assert result.name == "Shenzhen"
    svc.area_repo.create.assert_awaited_once()  # type: ignore[attr-defined]


async def test_custom_geo_save_area_create_no_user():
    created = SimpleNamespace(id="sys-id", name="SystemArea", create_by="system", create_time=9999, update_by=None, update_time=None)
    svc = _custom_geo_svc(area_create=created)
    payload = CustomGeoAreaCreate(name="SystemArea")
    result = await svc.save_area(payload, None)
    assert result.name == "SystemArea"


# -- save_area (update existing, with id) --


async def test_custom_geo_save_area_update():
    existing = SimpleNamespace(id="a1", name="Old", create_by="7", create_time=1000, update_by=None, update_time=None)
    updated = SimpleNamespace(id="a1", name="New", create_by="7", create_time=1000, update_by="7", update_time=9999)
    svc = _custom_geo_svc(area_get_by_id=existing, area_update=updated)
    payload = CustomGeoAreaCreate(id="a1", name="New")
    result = await svc.save_area(payload, _user())
    assert result.name == "New"
    svc.area_repo.update.assert_awaited_once()  # type: ignore[attr-defined]


async def test_custom_geo_save_area_update_id_but_not_found_creates():
    created = SimpleNamespace(id="ghost", name="Ghost", create_by="7", create_time=9999, update_by=None, update_time=None)
    svc = _custom_geo_svc(area_get_by_id=None, area_create=created)
    payload = CustomGeoAreaCreate(id="ghost", name="Ghost")
    result = await svc.save_area(payload, _user())
    assert result.name == "Ghost"
    svc.area_repo.create.assert_awaited_once()  # type: ignore[attr-defined]


# -- delete_area --


async def test_custom_geo_delete_area():
    area = SimpleNamespace(id="a1", name="X")
    mock_del = AsyncMock()
    mock_del_sub = AsyncMock()
    svc = _custom_geo_svc(area_get_by_id=area, area_delete=mock_del, sub_delete_by_geo_area_id=mock_del_sub)
    await svc.delete_area("a1")
    mock_del_sub.assert_awaited_once_with("a1")
    mock_del.assert_awaited_once_with(area)


async def test_custom_geo_delete_area_not_found():
    mock_del = AsyncMock()
    svc = _custom_geo_svc(area_get_by_id=None, area_delete=mock_del)
    await svc.delete_area("missing")
    mock_del.assert_not_awaited()


# -- save_sub_area --


async def test_custom_geo_save_sub_area():
    created = SimpleNamespace(id=999, geo_area_id="a1", name="Haidian", geo_json={"type": "Polygon"})
    svc = _custom_geo_svc(sub_create=created)
    payload = CustomGeoSubAreaCreate(geo_area_id="a1", name="Haidian", geo_json={"type": "Polygon"})
    result = await svc.save_sub_area(payload)
    assert result.name == "Haidian"


# -- delete_sub_area --


async def test_custom_geo_delete_sub_area():
    sub = SimpleNamespace(id=999, geo_area_id="a1", name="Haidian")
    mock_del = AsyncMock()
    svc = _custom_geo_svc(sub_get_by_id=sub, sub_delete=mock_del)
    await svc.delete_sub_area(999)
    mock_del.assert_awaited_once_with(sub)


async def test_custom_geo_delete_sub_area_not_found():
    mock_del = AsyncMock()
    svc = _custom_geo_svc(sub_get_by_id=None, sub_delete=mock_del)
    await svc.delete_sub_area(999)
    mock_del.assert_not_awaited()


# -- list_sub_area_options --


async def test_custom_geo_list_sub_area_options():
    subs = [
        SimpleNamespace(id=1, geo_area_id="a1", name="X", geo_json=None),
        SimpleNamespace(id=2, geo_area_id="a1", name="Y", geo_json={"type": "Point"}),
    ]
    svc = _custom_geo_svc(sub_list_all=subs)
    result = await svc.list_sub_area_options()
    assert len(result) == 2
    assert result[1].name == "Y"


# ===========================================================================
# GeoService - unit tests
# ===========================================================================


def _geo_svc(
    *,
    get_by_id: Any | None = "UNSET",
    create: Any | None = "UNSET",
    update: Any | None = "UNSET",
    delete: AsyncMock | None = None,
) -> GeoService:
    session = cast(AsyncSession, SimpleNamespace())
    svc = GeoService(session)
    if get_by_id != "UNSET":
        svc.geo_repo.get_by_id = AsyncMock(return_value=get_by_id)  # type: ignore[attr-defined]
    if create != "UNSET":
        svc.geo_repo.create = AsyncMock(return_value=create)  # type: ignore[attr-defined]
    if update != "UNSET":
        svc.geo_repo.update = AsyncMock(return_value=update)  # type: ignore[attr-defined]
    if delete is not None:
        svc.geo_repo.delete = delete  # type: ignore[attr-defined]
    return svc


# -- save_geo (create new) --


async def test_geo_save_create():
    created = SimpleNamespace(id="g1", name="China", geo_json={"type": "Feature"})
    svc = _geo_svc(get_by_id=None, create=created)
    payload = GeoSaveRequest(id="g1", name="China", geo_json={"type": "Feature"})
    result = await svc.save_geo(payload)
    assert result["id"] == "g1"
    assert result["name"] == "China"
    assert result["geoJson"] == {"type": "Feature"}


# -- save_geo (update existing) --


async def test_geo_save_update():
    existing = SimpleNamespace(id="g1", name="Old", geo_json={})
    updated = SimpleNamespace(id="g1", name="New", geo_json={"type": "Point"})
    svc = _geo_svc(get_by_id=existing, update=updated)
    payload = GeoSaveRequest(id="g1", name="New", geo_json={"type": "Point"})
    result = await svc.save_geo(payload)
    assert result["name"] == "New"
    svc.geo_repo.update.assert_awaited_once()  # type: ignore[attr-defined]


async def test_geo_save_update_partial():
    existing = SimpleNamespace(id="g1", name="Old", geo_json={})
    updated = SimpleNamespace(id="g1", name="Old", geo_json={"type": "Polygon"})
    svc = _geo_svc(get_by_id=existing, update=updated)
    payload = GeoSaveRequest(id="g1", name=None, geo_json={"type": "Polygon"})
    result = await svc.save_geo(payload)
    assert result["geoJson"] == {"type": "Polygon"}


# -- delete_geo --


async def test_geo_delete():
    geo = SimpleNamespace(id="g1", name="X")
    mock_del = AsyncMock()
    svc = _geo_svc(get_by_id=geo, delete=mock_del)
    await svc.delete_geo("g1")
    mock_del.assert_awaited_once_with(geo)


async def test_geo_delete_not_found():
    svc = _geo_svc(get_by_id=None)
    with pytest.raises(HTTPException) as exc_info:
        await svc.delete_geo("missing")
    assert exc_info.value.status_code == 404


# -- mapping --


async def test_geo_mapping():
    geo = SimpleNamespace(id="g1", name="Beijing", geo_json={})
    svc = _geo_svc(get_by_id=geo)
    payload = GeoMappingRequest(mapping={"Beijing": "110000"})
    result = await svc.mapping("g1", payload)
    assert result["id"] == "g1"
    assert result["name"] == "Beijing"
    assert result["mapping"] == {"Beijing": "110000"}


async def test_geo_mapping_not_found():
    svc = _geo_svc(get_by_id=None)
    payload = GeoMappingRequest(mapping={})
    with pytest.raises(HTTPException) as exc_info:
        await svc.mapping("missing", payload)
    assert exc_info.value.status_code == 404


# -- _geo_to_dict --


def test_geo_to_dict():
    geo = SimpleNamespace(id="g1", name="Test", geo_json={"type": "Point"})
    result = _geo_to_dict(geo)
    assert result == {"id": "g1", "name": "Test", "geoJson": {"type": "Point"}}


# ===========================================================================
# Integration tests (require PostgreSQL)
# ===========================================================================


@pytest.mark.skipif(_SKIP_DB, reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_custom_geo_crud_db(db_session: AsyncSession):
    """Integration: create → get → delete a custom geo area."""
    from tests.fixtures.test_factories import stamp  # pyright: ignore[reportImplicitRelativeImport]

    svc = CustomGeoService(db_session)
    area_id = str(stamp())

    # Create
    payload = CustomGeoAreaCreate(id=area_id, name="IntegrationTest")
    created = await svc.save_area(payload, _user())
    assert created.name == "IntegrationTest"

    # Get
    found = await svc.get_area(area_id)
    assert found is not None
    assert found.name == "IntegrationTest"

    # List
    areas = await svc.list_areas()
    assert any(a.name == "IntegrationTest" for a in areas)

    # Delete
    await svc.delete_area(area_id)
    gone = await svc.get_area(area_id)
    assert gone is None


@pytest.mark.skipif(_SKIP_DB, reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_geo_save_and_delete_db(db_session: AsyncSession):
    """Integration: save → delete a geo record."""
    from tests.fixtures.test_factories import stamp  # pyright: ignore[reportImplicitRelativeImport]

    svc = GeoService(db_session)
    geo_id = f"test-geo-{stamp()}"

    # Create
    payload = GeoSaveRequest(id=geo_id, name="TestGeo", geo_json={"type": "Point"})
    result = await svc.save_geo(payload)
    assert result["name"] == "TestGeo"

    # Update
    payload2 = GeoSaveRequest(id=geo_id, name="UpdatedGeo", geo_json={"type": "Polygon"})
    result2 = await svc.save_geo(payload2)
    assert result2["name"] == "UpdatedGeo"

    # Delete
    await svc.delete_geo(geo_id)
