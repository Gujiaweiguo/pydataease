# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false

"""Coverage tests for visualization_subject, visualization_bg, and interactive_tree services."""

from __future__ import annotations

import os
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import TokenUser
from app.schemas.visualization_subject import SubjectUpdateRequest
from app.services.visualization_bg_service import VisualizationBackgroundService
from app.services.visualization_subject_service import (
    VisualizationSubjectService,
    _subject_to_dict,
)
from app.services.interactive_tree_service import InteractiveTreeService, _build_tree

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

pytestmark = [pytest.mark.asyncio]

_SKIP_DB = os.getenv("DE_E2E") != "1"


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


# ===========================================================================
# Unit tests - _subject_to_dict
# ===========================================================================


async def test_subject_to_dict_maps_all_fields():
    ns = SimpleNamespace(
        id="s1",
        name="theme-light",
        type="self",
        details={"color": "#fff"},
        delete_flag=False,
        cover_url="http://img/cover.png",
        create_num=3,
        create_time=1000,
        create_by="7",
        update_time=2000,
        update_by="7",
    )
    result = _subject_to_dict(ns)
    assert result["id"] == "s1"
    assert result["name"] == "theme-light"
    assert result["type"] == "self"
    assert result["details"] == {"color": "#fff"}
    assert result["deleteFlag"] is False
    assert result["coverUrl"] == "http://img/cover.png"
    assert result["createNum"] == 3
    assert result["createTime"] == 1000
    assert result["createBy"] == "7"
    assert result["updateTime"] == 2000
    assert result["updateBy"] == "7"


# ===========================================================================
# VisualizationSubjectService - unit (mock repo)
# ===========================================================================


def _mock_subject_service(
    *,
    list_active: list[Any] | None = None,
    get_by_id: Any | None = "UNSET",
    get_by_name: Any | None = "UNSET",
    create: Any | None = "UNSET",
    update: Any | None = "UNSET",
    delete: AsyncMock | None = None,
) -> VisualizationSubjectService:
    """Build service with mocked repo methods."""
    session = cast(AsyncSession, SimpleNamespace())
    svc = VisualizationSubjectService(session)

    if list_active is not None:
        svc.repo.list_active = AsyncMock(return_value=list_active)  # type: ignore[attr-defined]
    if get_by_id != "UNSET":
        svc.repo.get_by_id = AsyncMock(return_value=get_by_id)  # type: ignore[attr-defined]
    if get_by_name != "UNSET":
        svc.repo.get_by_name = AsyncMock(return_value=get_by_name)  # type: ignore[attr-defined]
    if create != "UNSET":
        svc.repo.create = AsyncMock(return_value=create)  # type: ignore[attr-defined]
    if update != "UNSET":
        svc.repo.update = AsyncMock(return_value=update)  # type: ignore[attr-defined]
    if delete is not None:
        svc.repo.delete = delete  # type: ignore[attr-defined]

    return svc


async def test_subject_query_returns_dicts():
    ns = SimpleNamespace(
        id="s1", name="t", type="self", details=None,
        delete_flag=False, cover_url=None, create_num=0,
        create_time=0, create_by="1", update_time=0, update_by="1",
    )
    svc = _mock_subject_service(list_active=[ns])
    result = await svc.query()
    assert len(result) == 1
    assert result[0]["id"] == "s1"


async def test_subject_query_empty():
    svc = _mock_subject_service(list_active=[])
    result = await svc.query()
    assert result == []


async def test_subject_query_with_group_groups_of_4():
    items = []
    for i in range(6):
        items.append(SimpleNamespace(
            id=f"s{i}", name=f"n{i}", type="self", details=None,
            delete_flag=False, cover_url=None, create_num=0,
            create_time=0, create_by="1", update_time=0, update_by="1",
        ))
    svc = _mock_subject_service(list_active=items)
    result = await svc.query_subject_with_group()
    assert len(result) == 2  # [4, 2]
    assert len(result[0]) == 4
    assert len(result[1]) == 2


async def test_subject_query_with_group_exact_4():
    items = [SimpleNamespace(
        id=f"s{i}", name=f"n{i}", type="self", details=None,
        delete_flag=False, cover_url=None, create_num=0,
        create_time=0, create_by="1", update_time=0, update_by="1",
    ) for i in range(4)]
    svc = _mock_subject_service(list_active=items)
    result = await svc.query_subject_with_group()
    assert len(result) == 1
    assert len(result[0]) == 4


async def test_subject_query_with_group_empty():
    svc = _mock_subject_service(list_active=[])
    result = await svc.query_subject_with_group()
    assert result == []


async def test_subject_update_existing():
    existing = SimpleNamespace(
        id="s1", name="old", type="self", details=None,
        delete_flag=False, cover_url=None, create_num=0,
        create_time=0, create_by="1", update_time=0, update_by="1",
    )
    updated = SimpleNamespace(
        id="s1", name="new-name", type="self", details={"k": "v"},
        delete_flag=False, cover_url="url", create_num=0,
        create_time=0, create_by="1", update_time=9999, update_by="7",
    )
    svc = _mock_subject_service(get_by_id=existing, update=updated)
    payload = SubjectUpdateRequest(id="s1", name="new-name", details={"k": "v"}, cover_url="url")
    result = await svc.update_subject(payload, _user())
    assert result["name"] == "new-name"
    svc.repo.update.assert_awaited_once()  # type: ignore[attr-defined]


async def test_subject_update_not_found():
    svc = _mock_subject_service(get_by_id=None)
    payload = SubjectUpdateRequest(id="missing", name="x")
    with pytest.raises(HTTPException) as exc_info:
        await svc.update_subject(payload, _user())
    assert exc_info.value.status_code == 404


async def test_subject_create_new():
    created = SimpleNamespace(
        id="new-id", name="fresh", type="self", details=None,
        delete_flag=False, cover_url=None, create_num=0,
        create_time=1000, create_by="7", update_time=None, update_by=None,
    )
    svc = _mock_subject_service(get_by_name=None, create=created)
    payload = SubjectUpdateRequest(name="fresh")
    result = await svc.update_subject(payload, _user())
    assert result["name"] == "fresh"
    svc.repo.create.assert_awaited_once()  # type: ignore[attr-defined]


async def test_subject_create_duplicate_name():
    existing = SimpleNamespace(
        id="s1", name="dup", type="self", details=None,
        delete_flag=False, cover_url=None, create_num=0,
        create_time=0, create_by="1", update_time=0, update_by="1",
    )
    svc = _mock_subject_service(get_by_name=existing)
    payload = SubjectUpdateRequest(name="dup")
    with pytest.raises(HTTPException) as exc_info:
        await svc.update_subject(payload, _user())
    assert exc_info.value.status_code == 400


async def test_subject_delete_success():
    entity = SimpleNamespace(id="s1", name="x")
    mock_delete = AsyncMock()
    svc = _mock_subject_service(get_by_id=entity, delete=mock_delete)
    await svc.delete_subject("s1")
    mock_delete.assert_awaited_once_with(entity)


async def test_subject_delete_not_found():
    svc = _mock_subject_service(get_by_id=None)
    with pytest.raises(HTTPException) as exc_info:
        await svc.delete_subject("missing")
    assert exc_info.value.status_code == 404


# ===========================================================================
# VisualizationBackgroundService - unit (mock repo)
# ===========================================================================


async def test_bg_find_all_grouped_with_classification():
    rows = [
        SimpleNamespace(id="b1", name="bg1", classification="dark", content="c1",
                        remark=None, sort=1, upload_time=1000, base_url=None, url=None),
        SimpleNamespace(id="b2", name="bg2", classification="dark", content="c2",
                        remark=None, sort=2, upload_time=2000, base_url=None, url=None),
        SimpleNamespace(id="b3", name="bg3", classification="light", content="c3",
                        remark=None, sort=3, upload_time=3000, base_url=None, url=None),
    ]
    session = cast(AsyncSession, SimpleNamespace())
    svc = VisualizationBackgroundService(session)
    svc.repo.list_all = AsyncMock(return_value=rows)  # type: ignore[attr-defined]
    result = await svc.find_all_grouped()
    assert "dark" in result
    assert "light" in result
    assert len(result["dark"]) == 2
    assert len(result["light"]) == 1


async def test_bg_find_all_grouped_null_classification_uses_default():
    rows = [
        SimpleNamespace(id="b1", name="bg1", classification=None, content="c",
                        remark=None, sort=1, upload_time=1000, base_url=None, url=None),
    ]
    session = cast(AsyncSession, SimpleNamespace())
    svc = VisualizationBackgroundService(session)
    svc.repo.list_all = AsyncMock(return_value=rows)  # type: ignore[attr-defined]
    result = await svc.find_all_grouped()
    assert "default" in result
    assert result["default"][0]["id"] == "b1"


async def test_bg_find_all_grouped_empty():
    session = cast(AsyncSession, SimpleNamespace())
    svc = VisualizationBackgroundService(session)
    svc.repo.list_all = AsyncMock(return_value=[])  # type: ignore[attr-defined]
    result = await svc.find_all_grouped()
    assert result == {}


async def test_bg_find_all_dict_keys():
    rows = [
        SimpleNamespace(id="b1", name="bg1", classification="c", content="data",
                        remark="r", sort=5, upload_time=999, base_url="base", url="full"),
    ]
    session = cast(AsyncSession, SimpleNamespace())
    svc = VisualizationBackgroundService(session)
    svc.repo.list_all = AsyncMock(return_value=rows)  # type: ignore[attr-defined]
    result = await svc.find_all_grouped()
    item = result["c"][0]
    assert item["uploadTime"] == 999
    assert item["baseUrl"] == "base"
    assert item["url"] == "full"


# ===========================================================================
# InteractiveTreeService - _build_tree unit tests
# ===========================================================================


def test_build_tree_flat_nodes():
    nodes = [
        {"id": "1", "pid": "0", "name": "root-child"},
        {"id": "2", "pid": "1", "name": "nested"},
    ]
    result = _build_tree(nodes, pid="0")
    assert len(result) == 1
    assert result[0]["id"] == "1"
    assert len(result[0]["children"]) == 1
    assert result[0]["children"][0]["id"] == "2"


def test_build_tree_empty():
    result = _build_tree([], pid="0")
    assert result == []


def test_build_tree_multiple_roots():
    nodes = [
        {"id": "a", "pid": "0"},
        {"id": "b", "pid": "0"},
    ]
    result = _build_tree(nodes, pid="0")
    assert len(result) == 2


def test_build_tree_deep_nesting():
    nodes = [
        {"id": "1", "pid": "0"},
        {"id": "2", "pid": "1"},
        {"id": "3", "pid": "2"},
    ]
    result = _build_tree(nodes, pid="0")
    assert result[0]["children"][0]["children"][0]["id"] == "3"


def test_build_tree_no_match_pid():
    nodes = [{"id": "x", "pid": "99"}]
    result = _build_tree(nodes, pid="0")
    assert result == []


# ===========================================================================
# InteractiveTreeService - get_tree integration (requires DB)
# ===========================================================================


@pytest.mark.skipif(_SKIP_DB, reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_interactive_tree_get_tree(db_session: AsyncSession):
    svc = InteractiveTreeService(db_session)
    result = await svc.get_tree()
    assert "dashboard" in result
    assert "dataV" in result
    assert "dataset" in result
    assert "datasource" in result
    for key in ("dashboard", "dataV", "dataset", "datasource"):
        assert isinstance(result[key], list)
