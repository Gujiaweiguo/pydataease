# pyright: reportPrivateUsage=false, reportMissingTypeArgument=false

"""Coverage tests for api_key, system, static_resource, watermark, task, template_market services."""

from __future__ import annotations

import os
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.api_key import ApiKeyEnableEditor
from app.schemas.auth import TokenUser
from app.schemas.static_resource import StaticResourceUploadRequest
from app.schemas.watermark import WatermarkSaveRequest
from app.services.api_key_service import ApiKeyService
from app.services.static_resource_service import StaticResourceService, _resource_to_dict
from app.services.system_service import SystemService, _build_menu_tree
from app.services.task_service import TaskService
from app.services.template_market_service import TemplateMarketService
from app.services.watermark_service import WatermarkService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

pytestmark = [pytest.mark.asyncio]

_SKIP_DB = os.getenv("DE_E2E") != "1"


def _user(uid: int = 7) -> TokenUser:
    return TokenUser(user_id=uid, oid=9)


# ===========================================================================
# ApiKeyService - unit tests
# ===========================================================================


def _api_key_svc(
    *,
    get_by_id: Any | None = "UNSET",
    list_by_creator: list[Any] | None = None,
    create: Any | None = "UNSET",
    update: Any | None = "UNSET",
    delete: AsyncMock | None = None,
) -> ApiKeyService:
    session = cast(AsyncSession, SimpleNamespace())
    svc = ApiKeyService(session)
    if get_by_id != "UNSET":
        svc.repo.get_by_id = AsyncMock(return_value=get_by_id)  # type: ignore[attr-defined]
    if list_by_creator is not None:
        svc.repo.list_by_creator = AsyncMock(return_value=list_by_creator)  # type: ignore[attr-defined]
    if create != "UNSET":
        svc.repo.create = AsyncMock(return_value=create)  # type: ignore[attr-defined]
    if update != "UNSET":
        svc.repo.update = AsyncMock(return_value=update)  # type: ignore[attr-defined]
    if delete is not None:
        svc.repo.delete = delete  # type: ignore[attr-defined]
    return svc


async def test_api_key_generate():
    created = SimpleNamespace(
        id=12345, access_key="ak123", access_secret="sk456",
        enable=True, create_time=1000,
    )
    svc = _api_key_svc(create=created)
    result = await svc.generate(_user())
    assert result["accessKey"] == "ak123"
    assert result["enable"] is True
    svc.repo.create.assert_awaited_once()  # type: ignore[attr-defined]


async def test_api_key_query():
    keys = [
        SimpleNamespace(id=1, access_key="ak1", access_secret="sk1", enable=True, create_time=100),
        SimpleNamespace(id=2, access_key="ak2", access_secret="sk2", enable=False, create_time=200),
    ]
    svc = _api_key_svc(list_by_creator=keys)
    result = await svc.query(_user())
    assert len(result) == 2
    assert result[0]["accessKey"] == "ak1"


async def test_api_key_query_empty():
    svc = _api_key_svc(list_by_creator=[])
    result = await svc.query(_user())
    assert result == []


async def test_api_key_switch_enable():
    key_entity = SimpleNamespace(id=1, creator=7, access_key="ak", access_secret="sk", enable=True)
    updated = SimpleNamespace(id=1, creator=7, access_key="ak", access_secret="sk", enable=False)
    svc = _api_key_svc(get_by_id=key_entity, update=updated)
    payload = ApiKeyEnableEditor(id=1, enable=False)
    await svc.switch_enable(payload, _user())
    svc.repo.update.assert_awaited_once()  # type: ignore[attr-defined]


async def test_api_key_switch_enable_not_found():
    svc = _api_key_svc(get_by_id=None)
    payload = ApiKeyEnableEditor(id=999, enable=False)
    with pytest.raises(HTTPException) as exc_info:
        await svc.switch_enable(payload, _user())
    assert exc_info.value.status_code == 404


async def test_api_key_switch_enable_wrong_user():
    key_entity = SimpleNamespace(id=1, creator=99, access_key="ak", access_secret="sk", enable=True)
    svc = _api_key_svc(get_by_id=key_entity)
    payload = ApiKeyEnableEditor(id=1, enable=False)
    with pytest.raises(HTTPException) as exc_info:
        await svc.switch_enable(payload, _user(uid=7))
    assert exc_info.value.status_code == 403


async def test_api_key_delete():
    key_entity = SimpleNamespace(id=1, creator=7)
    mock_del = AsyncMock()
    svc = _api_key_svc(get_by_id=key_entity, delete=mock_del)
    await svc.delete_key(1, _user())
    mock_del.assert_awaited_once_with(key_entity)


async def test_api_key_delete_not_found():
    svc = _api_key_svc(get_by_id=None)
    with pytest.raises(HTTPException) as exc_info:
        await svc.delete_key(999, _user())
    assert exc_info.value.status_code == 404


async def test_api_key_delete_wrong_user():
    key_entity = SimpleNamespace(id=1, creator=99)
    svc = _api_key_svc(get_by_id=key_entity)
    with pytest.raises(HTTPException) as exc_info:
        await svc.delete_key(1, _user(uid=7))
    assert exc_info.value.status_code == 403


# ===========================================================================
# SystemService - unit tests
# ===========================================================================


async def test_system_query_online_map_default():
    session = cast(AsyncSession, SimpleNamespace())
    svc = SystemService(session)
    result = await svc.query_online_map()
    assert result.key == ""


async def test_system_save_online_map():
    session = cast(AsyncSession, SimpleNamespace())
    svc = SystemService(session)
    result = await svc.save_online_map("my-test-key")
    assert result.key == "my-test-key"


async def test_system_save_online_map_none():
    session = cast(AsyncSession, SimpleNamespace())
    svc = SystemService(session)
    result = await svc.save_online_map(None)
    assert result.key == ""


async def test_system_request_timeout_default():
    session = cast(AsyncSession, SimpleNamespace())
    svc = SystemService(session)
    result = await svc.request_timeout()
    assert isinstance(result, int)
    assert result == 120


async def test_system_list_fonts():
    session = cast(AsyncSession, SimpleNamespace())
    svc = SystemService(session)
    result = await svc.list_fonts()
    assert result == []


async def test_system_default_font():
    session = cast(AsyncSession, SimpleNamespace())
    svc = SystemService(session)
    result = await svc.default_font()
    assert result is None


async def test_system_get_area_entities():
    session = cast(AsyncSession, SimpleNamespace())
    svc = SystemService(session)
    result = await svc.get_area_entities("110000")
    assert result == []


async def test_build_menu_tree_simple():
    m1 = SimpleNamespace(id=1, pid=0, type=1, name="root", component=None,
                         menu_sort=0, icon=None, path="/", hidden=False, in_layout=True, auth=False)
    m2 = SimpleNamespace(id=2, pid=1, type=1, name="child", component="C",
                         menu_sort=1, icon=None, path="/c", hidden=False, in_layout=True, auth=False)
    result = _build_menu_tree([m1, m2])
    assert len(result) == 1
    assert result[0].name == "root"
    assert len(result[0].children) == 1
    assert result[0].children[0].name == "child"


async def test_build_menu_tree_orphan():
    m = SimpleNamespace(id=99, pid=50, type=1, name="orphan", component=None,
                        menu_sort=0, icon=None, path="/", hidden=False, in_layout=True, auth=False)
    result = _build_menu_tree([m])
    assert len(result) == 1
    assert result[0].name == "orphan"


# ===========================================================================
# StaticResourceService - unit tests
# ===========================================================================


async def test_static_resource_upload_new():
    created = SimpleNamespace(id="r1", name=None, content="base64data")
    session = cast(AsyncSession, SimpleNamespace())
    svc = StaticResourceService(session)
    svc.resource_repo.get_by_id = AsyncMock(return_value=None)  # type: ignore[attr-defined]
    svc.resource_repo.create = AsyncMock(return_value=created)  # type: ignore[attr-defined]
    payload = StaticResourceUploadRequest(content="base64data")
    result = await svc.upload("r1", payload)
    assert result["id"] == "r1"
    assert result["content"] == "base64data"


async def test_static_resource_upload_existing():
    existing = SimpleNamespace(id="r1", name="old", content="old-data")
    updated = SimpleNamespace(id="r1", name="old", content="new-data")
    session = cast(AsyncSession, SimpleNamespace())
    svc = StaticResourceService(session)
    svc.resource_repo.get_by_id = AsyncMock(return_value=existing)  # type: ignore[attr-defined]
    svc.resource_repo.update = AsyncMock(return_value=updated)  # type: ignore[attr-defined]
    payload = StaticResourceUploadRequest(content="new-data")
    result = await svc.upload("r1", payload)
    assert result["content"] == "new-data"


async def test_static_resource_find_as_base64():
    resource = SimpleNamespace(id="r1", content="c3RhdGlj")
    session = cast(AsyncSession, SimpleNamespace())
    svc = StaticResourceService(session)
    svc.resource_repo.get_by_id = AsyncMock(return_value=resource)  # type: ignore[attr-defined]
    result = await svc.find_as_base64("r1")
    assert result["resourceId"] == "r1"
    assert result["content"] == "c3RhdGlj"


async def test_static_resource_find_not_found():
    session = cast(AsyncSession, SimpleNamespace())
    svc = StaticResourceService(session)
    svc.resource_repo.get_by_id = AsyncMock(return_value=None)  # type: ignore[attr-defined]
    with pytest.raises(HTTPException) as exc_info:
        await svc.find_as_base64("missing")
    assert exc_info.value.status_code == 404


def test_resource_to_dict():
    r = SimpleNamespace(id="r1", name="pic.png", content="data")
    result = _resource_to_dict(r)
    assert result == {"id": "r1", "name": "pic.png", "content": "data"}


# ===========================================================================
# WatermarkService - unit tests
# ===========================================================================


async def test_watermark_get_info_found():
    entity = SimpleNamespace(
        id="system_default", version="1.0", setting_content='{"text":"watermark"}',
        create_by="admin", create_time=1000,
    )
    session = cast(AsyncSession, SimpleNamespace())
    svc = WatermarkService(session)
    svc.repo.get = AsyncMock(return_value=entity)  # type: ignore[attr-defined]
    result = await svc.get_watermark_info()
    assert result is not None
    assert result.version == "1.0"


async def test_watermark_get_info_not_found():
    session = cast(AsyncSession, SimpleNamespace())
    svc = WatermarkService(session)
    svc.repo.get = AsyncMock(return_value=None)  # type: ignore[attr-defined]
    result = await svc.get_watermark_info()
    assert result is None


async def test_watermark_save_info():
    session = cast(AsyncSession, SimpleNamespace())
    svc = WatermarkService(session)
    svc.repo.update = AsyncMock()  # type: ignore[attr-defined]
    payload = WatermarkSaveRequest(version="2.0", setting_content='{"text":"new"}')
    await svc.save_watermark_info(payload)
    svc.repo.update.assert_awaited_once()  # type: ignore[attr-defined]


async def test_watermark_save_info_no_data():
    session = cast(AsyncSession, SimpleNamespace())
    svc = WatermarkService(session)
    svc.repo.update = AsyncMock()  # type: ignore[attr-defined]
    payload = WatermarkSaveRequest()
    await svc.save_watermark_info(payload)
    svc.repo.update.assert_not_awaited()  # type: ignore[attr-defined]


# ===========================================================================
# TaskService - unit tests
# ===========================================================================


def _task_svc(
    *,
    get_by_id: Any | None = "UNSET",
) -> TaskService:
    session = cast(AsyncSession, SimpleNamespace())
    scheduler = MagicMock()
    worker = MagicMock()
    svc = TaskService(session, scheduler, worker)
    if get_by_id != "UNSET":
        svc.task_repo.get_by_id = AsyncMock(return_value=get_by_id)  # type: ignore[attr-defined]
    return svc


async def test_task_get_status():
    task = SimpleNamespace(
        id="t1", user_id=7, file_name="f.xlsx", export_status="SUCCESS",
        export_progress="100", export_from=1, export_from_type="chart",
        export_time=1000, msg=None, params={},
    )
    svc = _task_svc(get_by_id=task)
    result = await svc.get_status("t1", _user())
    assert result.id == "t1"


async def test_task_get_status_not_found():
    svc = _task_svc(get_by_id=None)
    with pytest.raises(HTTPException) as exc_info:
        await svc.get_status("missing", _user())
    assert exc_info.value.status_code == 404


async def test_task_get_status_wrong_user():
    task = SimpleNamespace(id="t1", user_id=99)
    svc = _task_svc(get_by_id=task)
    with pytest.raises(HTTPException) as exc_info:
        await svc.get_status("t1", _user(uid=7))
    assert exc_info.value.status_code == 404


async def test_task_retry_success():
    task = SimpleNamespace(
        id="t1", user_id=7, export_status="FAILED",
        file_name=None, export_progress=None, export_from=None,
        export_from_type=None, export_time=None, msg=None, params={},
    )
    svc = _task_svc(get_by_id=task)
    result = await svc.retry_task("t1", _user())
    assert result.status == "INITIATED"
    svc.scheduler.add_job.assert_called_once()  # type: ignore[attr-defined]


async def test_task_retry_non_failed():
    task = SimpleNamespace(
        id="t1", user_id=7, export_status="SUCCESS",
        file_name=None, export_progress=None, export_from=None,
        export_from_type=None, export_time=None, msg=None, params={},
    )
    svc = _task_svc(get_by_id=task)
    with pytest.raises(HTTPException) as exc_info:
        await svc.retry_task("t1", _user())
    assert exc_info.value.status_code == 400


# ===========================================================================
# TemplateMarketService - unit tests
# ===========================================================================


async def test_template_market_search_recommend():
    session = cast(AsyncSession, SimpleNamespace())
    svc = TemplateMarketService(session)
    # Mock the inner SysSettingService to avoid DB
    svc.settings.get_setting = AsyncMock(return_value="http://tpl.local")  # type: ignore[attr-defined]
    result = await svc.search_recommend()
    assert result["baseUrl"] == "http://tpl.local"
    assert result["contents"] == []


async def test_template_market_search():
    session = cast(AsyncSession, SimpleNamespace())
    svc = TemplateMarketService(session)
    svc.settings.get_setting = AsyncMock(return_value="")  # type: ignore[attr-defined]
    result = await svc.search()
    assert result["baseUrl"] == ""
    assert result["categories"] == []
    assert result["contents"] == []


async def test_template_market_search_preview():
    session = cast(AsyncSession, SimpleNamespace())
    svc = TemplateMarketService(session)
    svc.settings.get_setting = AsyncMock(return_value="http://preview")  # type: ignore[attr-defined]
    result = await svc.search_preview()
    assert result["baseUrl"] == "http://preview"


async def test_template_market_get_categories():
    session = cast(AsyncSession, SimpleNamespace())
    svc = TemplateMarketService(session)
    result = await svc.get_categories()
    assert result == []


async def test_template_market_get_categories_object():
    session = cast(AsyncSession, SimpleNamespace())
    svc = TemplateMarketService(session)
    result = await svc.get_categories_object()
    assert len(result) == 2
    assert result[0]["value"] == "recent"
    assert result[1]["value"] == "suggest"


async def test_template_market_get_base_url_error():
    session = cast(AsyncSession, SimpleNamespace())
    svc = TemplateMarketService(session)
    svc.settings.get_setting = AsyncMock(side_effect=Exception("db error"))  # type: ignore[attr-defined]
    result = await svc.search_recommend()
    assert result["baseUrl"] == ""


# ===========================================================================
# Integration tests (require PostgreSQL)
# ===========================================================================


@pytest.mark.skipif(_SKIP_DB, reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_system_query_menus_db(db_session: AsyncSession):
    svc = SystemService(db_session)
    result = await svc.query_menus()
    assert isinstance(result, list)


@pytest.mark.skipif(_SKIP_DB, reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_task_list_recent_db(db_session: AsyncSession):
    scheduler = MagicMock()
    worker = MagicMock()
    svc = TaskService(db_session, scheduler, worker)
    result = await svc.list_recent_tasks(_user(), limit=5)
    assert isinstance(result, list)
