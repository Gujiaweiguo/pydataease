from __future__ import annotations

from collections.abc import Generator

import pytest
from httpx import AsyncClient

from app.main import app
from app.services.chart_service import get_chart_service
from app.services.datasource_service import get_datasource_service
from app.services.dataset_service import get_dataset_service
from app.services.export_service import get_export_service
from app.services.share_service import get_share_service
from app.services.system_service import get_system_service
from app.services.template_service import get_template_service
from app.services.visualization_service import get_visualization_service
from app.services.linkage_service import get_linkage_service
from tests.fixtures.auth_fixtures import _build_token


AUTH_HEADERS = {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


def _assert_result_message(body: dict, *, code: int = 0) -> None:
    assert "code" in body, f"Missing 'code' key in response: {list(body.keys())}"
    assert "data" in body, f"Missing 'data' key in response: {list(body.keys())}"
    assert "msg" in body, f"Missing 'msg' key in response: {list(body.keys())}"
    assert body["code"] == code, f"Expected code={code}, got {body['code']}: {body.get('msg')}"


class FakeDatasetService:
    async def tree(self): return [{"id": 1, "name": "root", "leaf": False, "children": []}]
    async def get_fields(self, payload): return [{"originName": "col_a", "name": "Column A"}]
    async def preview_sql(self, payload): return {"data": [], "fields": []}
    async def create(self, payload, user): return {"id": 100, "name": "new-ds"}
    async def save(self, payload, user): return {"id": 200, "name": "updated-ds"}
    async def delete(self, gid): pass
    async def per_delete(self, gid): return True
    async def get_bar_info(self, gid): return {"id": str(gid), "createBy": "7"}
    async def get_details(self, gid): return {"id": str(gid), "name": "detail-ds"}
    async def rename(self, payload, user): return {"name": "renamed"}
    async def move(self, payload, user): return {"pid": 5}
    async def export_dataset(self, payload): return {}
    async def ds_details(self, payload): return {}
    async def get_dataset_preview(self, gid): return {}
    async def get_dataset_total(self, gid): return 0


class FakeChartService:
    async def get_by_id(self, chart_id): return {"id": chart_id, "title": "chart", "sceneId": 1, "tableId": 1, "type": "bar", "render": "antv"}
    async def save(self, payload, user): return {"id": 9001, "title": "saved", "sceneId": 1, "tableId": 1, "type": "bar", "render": "antv"}
    async def update(self, payload, user): return {"id": 9002, "title": "updated", "sceneId": 1, "tableId": 1, "type": "line", "render": "antv"}
    async def delete(self, chart_id): pass
    async def get_data(self, payload): return {"fields": [], "data": [], "total": 0, "chartId": 1, "sceneId": 1}
    async def get_detail(self, chart_id): return {"chart": {"id": chart_id, "title": "detail"}, "fields": []}
    async def view_detail_list(self, scene_id): return [{"id": 1, "sceneId": scene_id}]
    async def export_details(self, payload): return {"file": "export.xlsx", "status": "SUCCESS"}


class FakeDatasourceService:
    async def tree(self): return [{"id": 1, "name": "ds-root", "type": "folder"}]
    async def query(self, keyword): return []
    async def save(self, payload, user): return {"id": 1, "name": "new-ds"}
    async def update(self, payload, user): return {"id": 1, "name": "updated-ds"}
    async def validate(self, payload): return {"status": "success"}
    async def validate_by_id(self, ds_id): return {"status": "success"}
    async def get_tables(self, ds_id): return []
    async def get_fields(self, ds_id, table_name): return []
    async def delete(self, ds_id): pass
    async def latest_use(self): return []
    async def move(self, ds_id, pid): pass
    async def rename(self, ds_id, name): pass
    async def get_schemas_from_config(self, config, ds_type): return []
    async def upload_file(self, file, id, edit_type): return {}
    async def load_remote_file(self, payload): return {}
    async def get_full(self, ds_id): return {"id": ds_id, "name": "ds-full"}
    async def get_hide_pw(self, ds_id): return {"id": ds_id}
    async def create_folder(self, name, pid, user): return {"id": 1, "name": name}
    async def check_in_use(self, ds_id): return False
    async def check_repeat(self, payload): return False
    async def preview_data(self, payload): return {}
    async def sync_api_table(self, payload): pass
    async def sync_api_datasource(self, payload): pass
    async def list_sync_record(self, ds_id, page, limit): return {"data": [], "total": 0}
    async def check_api_datasource(self, payload): return {}
    async def get_simple(self, ds_id): return {"id": ds_id}
    async def get_engine_info(self): return {"id": 0, "name": "engine"}
    async def get_table_status(self, ds_id): return {}


class FakeVisualizationService:
    async def tree(self, payload): return [{"id": 1, "name": "panel-root"}]
    async def find_by_id(self, payload): return {"id": 1, "name": "panel"}
    async def save(self, payload, user): return {"id": 1, "name": "new-panel"}
    async def update(self, payload, user): return {"id": 1, "name": "updated-panel"}
    async def delete(self, dv_id, user): return {"id": dv_id}
    async def delete_logic(self, payload, user): return {}
    async def move(self, payload, user): return {}
    async def rename(self, payload, user): return {}
    async def find_recent(self, payload): return []
    async def find_copy_resource(self, dv_id, busi_flag): return {}
    async def save_canvas(self, payload, user): return {}
    async def update_canvas(self, payload, user): return {}
    async def update_base(self, payload, user): return {}
    async def update_publish_status(self, payload, user): return {}
    async def name_check(self, payload): return {}
    async def check_canvas_change(self, payload): return {}
    async def recover_to_published(self, payload): return {}
    async def app_canvas_name_check(self, payload): return {}
    async def decompression(self, payload): return {}
    async def find_dv_type(self, dv_id): return "panel"
    async def update_check_version(self, dv_id): return {}
    async def per_resource(self, vid): return {}
    async def view_detail_list(self, vid): return []
    async def favorited(self, resource_id, resource_type, user): return {}
    async def query_stores(self, user, **kw): return []
    async def add_store(self, resource_id, resource_type, user): return {}
    async def remove_store(self, resource_id, resource_type, user): return {}
    async def get_view_linkage_gather(self, payload): return {}
    async def get_view_linkage_gather_array(self, payload): return {}
    async def get_table_field_with_view_id(self, view_id): return []
    async def query_with_view_id(self, dv_id, view_id): return {}
    async def update_jump_set(self, payload): return {}
    async def query_target_visualization_jump_info(self, payload): return {}
    async def query_visualization_jump_info(self, dv_id, rt): return {}
    async def update_jump_set_active(self, payload): return {}
    async def remove_jump_set(self, payload): return {}
    async def query_with_visualization_id(self, dv_id): return {}
    async def update_outer_params_set(self, payload): return {}
    async def get_outer_params_info(self, dv_id): return {}
    async def save_watermark(self, payload): return {}
    async def query_ds_with_visualization_id(self, dv_id): return {}


class FakeShareService:
    async def get_status(self, rid): return {"active": True}
    async def validate_password(self, payload): return {"valid": True}
    async def proxy_info(self, payload): return None
    async def save(self, payload, user): return {"id": 1, "uuid": "abc"}
    async def detail(self, payload): return {"id": 1}
    async def delete(self, payload): pass
    async def view_detail(self, payload, **kw): return {}
    async def get_by_id(self, rid): return {"id": rid}
    async def save_ticket(self, payload): return {"id": 1}
    async def delete_ticket(self, payload): pass
    async def detail_tickets(self, payload): return {}
    async def proxy(self, uuid): return {}
    async def resolve(self, uuid, **kw): return {"id": 1}
    async def get_resource_data(self, share): return {}
    async def generate_embed_token(self, uuid): return "token123"
    async def switcher(self, rid, user): return {}
    async def edit_exp(self, rid, exp): return {}
    async def edit_pwd(self, rid, pwd, auto_pwd): return {}
    async def edit_uuid(self, rid, uuid): return {}
    async def query_shares(self): return []
    async def query_relation_by_user(self, uid): return []
    async def enable_ticket(self, rid, require): pass
    @staticmethod
    def generate_temp_ticket(): return "ticket123"


class FakeTemplateService:
    async def tree(self): return [{"id": 1, "name": "tmpl-root"}]
    async def save(self, payload, user): return {"id": 1, "name": "new-tmpl"}
    async def name_list(self): return []
    async def categories(self): return []
    async def find_categories(self, payload): return []
    async def category_form(self, cid): return {}
    async def delete(self, tid, cid): pass
    async def find_one(self, tid): return {"id": tid}
    async def find_by_body(self, payload): return {}
    async def list_templates(self, keyword): return []
    async def template_list(self, payload): return []
    async def update(self, payload): return {}
    async def name_check(self, payload): return {}
    async def category_template_name_check(self, payload): return {}
    async def delete_category(self, cid): return {}
    async def batch_delete(self, payload): return {}
    async def batch_update(self, payload): return {}
    async def find_categories_by_template_ids(self, payload): return []
    async def check_category_template(self, cid): return False
    async def toggle_favorite(self, rid, uid, rtype): return {}
    async def list_favorites(self, uid): return []


class FakeSystemService:
    async def query_online_map(self): return {"key": "map-key"}
    async def save_online_map(self, key): return {"key": key}
    async def request_timeout(self): return 30
    async def list_fonts(self): return []
    async def default_font(self): return {"name": "default"}
    async def get_area_entities(self, pcode): return {}


class FakeExportService:
    async def create_task(self, payload, user): return {"id": "task-1", "status": "pending"}
    async def list_task_records(self, user): return []
    async def list_tasks_paginated(self, status, page, limit, user): return []
    async def list_tasks(self, export_from, user): return []
    async def delete_task(self, tid): pass
    async def delete_tasks(self, ids, user): pass
    async def delete_all_by_status(self, status, ids, user): pass
    async def generate_download_uri(self, tid): return {"uri": f"/download/{tid}"}
    async def export_limit(self): return True
    async def delete_all(self, export_from, user): pass
    async def retry_task(self, tid): return {"id": tid, "status": "running"}
    async def download(self, tid): return {"detail": "not found"}


class FakeLinkageService:
    async def save_linkage(self, payload): pass
    async def get_visualization_all_linkage_info(self, dv_id, rt): return {}
    async def update_linkage_active(self, payload): return {}
    async def remove_linkage(self, payload): pass


@pytest.fixture
def _override_all_services() -> Generator[None, None, None]:
    overrides = {
        get_dataset_service: lambda: FakeDatasetService(),
        get_chart_service: lambda: FakeChartService(),
        get_datasource_service: lambda: FakeDatasourceService(),
        get_visualization_service: lambda: FakeVisualizationService(),
        get_share_service: lambda: FakeShareService(),
        get_template_service: lambda: FakeTemplateService(),
        get_system_service: lambda: FakeSystemService(),
        get_export_service: lambda: FakeExportService(),
        get_linkage_service: lambda: FakeLinkageService(),
    }
    for dep, factory in overrides.items():
        app.dependency_overrides[dep] = factory
    yield
    for dep in overrides:
        _ = app.dependency_overrides.pop(dep, None)


@pytest.mark.asyncio
async def test_dataset_tree_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.post("/de2api/datasetTree/tree", headers=AUTH_HEADERS, json={"busiFlag": "dataset"})
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_chart_get_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.get("/de2api/chart/123", headers=AUTH_HEADERS)
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_chart_get_data_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.post("/de2api/chart/getData", headers=AUTH_HEADERS, json={"id": 1})
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_datasource_tree_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.post("/de2api/datasource/tree", headers=AUTH_HEADERS)
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_datasource_types_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.get("/de2api/datasource/types", headers=AUTH_HEADERS)
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_visualization_tree_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.post("/de2api/dataVisualization/tree", headers=AUTH_HEADERS, json={"busiFlag": "panel"})
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_share_status_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.get("/de2api/share/status/1", headers=AUTH_HEADERS)
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_share_query_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.post("/de2api/share/query", headers=AUTH_HEADERS, json={})
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_template_tree_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.post("/de2api/templateManage/tree", headers=AUTH_HEADERS)
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_template_list_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.post("/de2api/templateManage/list", headers=AUTH_HEADERS, json={})
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_engine_info_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.get("/de2api/engine/info", headers=AUTH_HEADERS)
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_export_limit_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.post("/de2api/exportCenter/exportLimit", headers=AUTH_HEADERS)
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_export_task_records_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.post("/de2api/exportCenter/exportTasks/records", headers=AUTH_HEADERS)
    assert response.status_code == 200
    _assert_result_message(response.json())


@pytest.mark.asyncio
async def test_health_not_wrapped(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok"}


@pytest.mark.asyncio
async def test_unauthenticated_returns_401(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.post("/de2api/datasetTree/tree", json={"busiFlag": "dataset"})
    assert response.status_code == 401
    _assert_result_message(response.json(), code=401)


@pytest.mark.asyncio
async def test_system_query_online_map_result_message(client: AsyncClient, _override_all_services: None) -> None:
    response = await client.get("/de2api/sysParameter/queryOnlineMap", headers=AUTH_HEADERS)
    assert response.status_code == 200
    _assert_result_message(response.json())
