"""E2E full module coverage — datasource, dataset, dashboard, chart, org, role, user, template, system."""
from __future__ import annotations

import base64
import os
import time
from typing import Any, cast

import asyncpg  # pyright: ignore[reportMissingImports]
import httpx
import pytest

from tests.fixtures.e2e_helpers import (  # pyright: ignore[reportImplicitRelativeImport]
    BASE_URL,
    E2E_GATE,
    encrypt,
    find_node_by_id,
)

PG_DSN = os.environ.get(
    "E2E_PG_DSN",
    os.environ.get("DE_DATABASE_URL", "postgresql://dataease:dataease@127.0.0.1:5432/dataease")
    .replace("postgresql+asyncpg://", "postgresql://")
    .replace("postgresql+psycopg://", "postgresql://"),
)
MYSQL_PASSWORD = os.environ.get("E2E_MYSQL_PASSWORD", "")


def _assert_ok(response: httpx.Response, step: str) -> dict[str, Any]:
    assert response.status_code == 200, f"{step} failed: {response.text}"
    body = response.json()
    assert body["code"] == 0, f"{step} failed: {body}"
    assert "data" in body, f"{step} failed: {body}"
    return cast(dict[str, Any], body)


def _data_dict(body: dict[str, Any], step: str) -> dict[str, Any]:
    data = body["data"]
    assert isinstance(data, dict), f"{step} expected dict data: {body}"
    return cast(dict[str, Any], data)


def _data_list(body: dict[str, Any], step: str) -> list[Any]:
    data = body["data"]
    assert isinstance(data, list), f"{step} expected list data: {body}"
    return cast(list[Any], data)


def _build_mysql_datasource_payload(name: str, pid: int, database: str, password: str) -> dict[str, Any]:
    return {
        "name": name,
        "type": "mysql",
        "pid": pid,
        "configuration": {
            "host": "127.0.0.1",
            "port": "3306",
            "username": "root",
            "password": password,
            "dataBase": database,
            "database": database,
        },
    }


async def _pg_fetchrow(query: str, *args: object) -> asyncpg.Record | None:
    conn = await asyncpg.connect(PG_DSN)
    try:
        return await conn.fetchrow(query, *args)
    finally:
        await conn.close()


async def _pg_execute(query: str, *args: object) -> str:
    conn = await asyncpg.connect(PG_DSN)
    try:
        return await conn.execute(query, *args)
    finally:
        await conn.close()


@E2E_GATE
@pytest.mark.asyncio
async def test_e2e_modules_full() -> None:
    ids: dict[str, Any] = {}
    headers: dict[str, str] = {}
    org_headers: dict[str, str] = {}
    stamp = int(time.time() * 1000)
    mysql_db = os.environ.get("E2E_MYSQL_DATABASE", "mysql")
    ds_folder_name = f"E2E DS Folder {stamp}"
    ds_name = f"E2E MySQL DS {stamp}"
    ds_renamed = f"E2E MySQL DS Renamed {stamp}"
    dataset_folder_name = f"E2E Dataset Folder {stamp}"
    dataset_name = f"E2E Dataset {stamp}"
    dataset_saved_name = f"E2E Dataset Saved {stamp}"
    dashboard_name = f"E2E Dashboard {stamp}"
    dashboard_folder_name = f"E2E Dashboard Folder {stamp}"
    chart_name = f"E2E Chart {stamp}"
    chart_updated_name = f"E2E Chart Updated {stamp}"
    org_name = f"E2E Org {stamp}"
    org_renamed = f"E2E Org Renamed {stamp}"
    role_name = f"E2E Role {stamp}"
    role_renamed = f"E2E Role Renamed {stamp}"
    user_account = f"e2e_user_{stamp}"
    user_name = f"E2E User {stamp}"
    user_updated_name = f"E2E User Updated {stamp}"
    template_category_id = str(time.time_ns())
    template_category_name = f"E2E Template Category {stamp}"
    template_name = f"E2E Template {stamp}"

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        try:
            print("Step 1: Login")
            dekey_resp = await client.get("/de2api/dekey")
            dekey_body = _assert_ok(dekey_resp, "Step 1a")
            dekey = dekey_body["data"]
            assert isinstance(dekey, str) and dekey, f"Step 1a failed: {dekey_body}"
            login_resp = await client.post(
                "/de2api/login/localLogin",
                json={"name": encrypt("admin", dekey), "pwd": encrypt(os.environ.get("E2E_PASSWORD", "DataEase@123456"), dekey), "origin": 0},
            )
            login_body = _assert_ok(login_resp, "Step 1b")
            token = _data_dict(login_body, "Step 1b")["token"]
            assert isinstance(token, str) and token, f"Step 1b failed: {login_body}"
            headers = {"X-DE-TOKEN": token}

            print("Step 2: Login auth endpoints")
            user_info_resp = await client.get("/de2api/user/info", headers=headers)
            user_info_body = _assert_ok(user_info_resp, "Step 2a")
            user_info = _data_dict(user_info_body, "Step 2a")
            assert user_info["account"] == "admin", f"Step 2a failed: {user_info}"
            refresh_resp = await client.get("/de2api/login/refresh", headers=headers)
            refresh_body = _assert_ok(refresh_resp, "Step 2b")
            refresh_data = _data_dict(refresh_body, "Step 2b")
            refreshed_token = refresh_data["token"]
            assert isinstance(refreshed_token, str) and refreshed_token, f"Step 2b failed: {refresh_body}"
            refresh_headers = {"X-DE-TOKEN": refreshed_token}
            logout_resp = await client.get("/de2api/logout", headers=refresh_headers)
            logout_body = _assert_ok(logout_resp, "Step 2c")
            assert logout_body["data"] is None, f"Step 2c failed: {logout_body}"

            print("Step 3: Datasource create folder")
            ds_folder_resp = await client.post(
                "/de2api/datasource/createFolder",
                headers=headers,
                json={"name": ds_folder_name, "pid": 0},
            )
            ds_folder_body = _assert_ok(ds_folder_resp, "Step 3")
            ids["ds_folder"] = int(_data_dict(ds_folder_body, "Step 3")["id"])

            print("Step 4: Datasource save")
            ds_payload: dict[str, Any] | None = None
            validate_errors: list[str] = []
            for password in dict.fromkeys(["", MYSQL_PASSWORD, "Admin168"]):
                candidate_payload = _build_mysql_datasource_payload(ds_name, ids["ds_folder"], mysql_db, password)
                validate_candidate_resp = await client.post(
                    "/de2api/datasource/validate",
                    headers=headers,
                    json=candidate_payload,
                )
                if validate_candidate_resp.status_code == 200:
                    validate_candidate_body = validate_candidate_resp.json()
                    if validate_candidate_body.get("code") == 0:
                        validate_candidate_data = validate_candidate_body.get("data")
                        if isinstance(validate_candidate_data, dict) and validate_candidate_data.get("success") is True:
                            ds_payload = candidate_payload
                            break
                validate_errors.append(validate_candidate_resp.text)
            assert ds_payload is not None, f"Step 4 failed: could not validate MySQL datasource with configured passwords: {validate_errors}"
            ds_resp = await client.post("/de2api/datasource/save", headers=headers, json=ds_payload)
            ds_body = _assert_ok(ds_resp, "Step 4")
            ds_data = _data_dict(ds_body, "Step 4")
            ids["datasource"] = int(ds_data["id"])
            assert ds_data["name"] == ds_name, f"Step 4 failed: {ds_data}"

            print("Step 5: Datasource validate")
            validate_resp = await client.post("/de2api/datasource/validate", headers=headers, json=ds_payload)
            validate_body = _assert_ok(validate_resp, "Step 5")
            validate_data = _data_dict(validate_body, "Step 5")
            assert validate_data["success"] is True, f"Step 5 failed: {validate_data}"

            print("Step 6: Datasource tree")
            ds_tree_resp = await client.post("/de2api/datasource/tree", headers=headers, json={})
            ds_tree_body = _assert_ok(ds_tree_resp, "Step 6")
            assert find_node_by_id(ds_tree_body["data"], ids["datasource"]) is not None, f"Step 6 failed: {ds_tree_body}"

            print("Step 7: Datasource schema")
            schema_resp = await client.get(f"/de2api/datasource/getSchema/{ids['datasource']}", headers=headers)
            schema_body = _assert_ok(schema_resp, "Step 7")
            schema_data = _data_list(schema_body, "Step 7")
            assert len(schema_data) > 0, f"Step 7 failed: {schema_body}"
            table_name = str(schema_data[0].get("tableName") or schema_data[0]["name"])

            print("Step 8: Datasource table field")
            field_resp = await client.get(
                f"/de2api/datasource/getTableField/{ids['datasource']}/{table_name}",
                headers=headers,
            )
            field_body = _assert_ok(field_resp, "Step 8")
            field_data = _data_list(field_body, "Step 8")
            assert len(field_data) > 0, f"Step 8 failed: {field_body}"
            # Convert datasource fields to allFields format for dataset save
            ds_fields = []
            for idx, f in enumerate(field_data):
                ds_fields.append({
                    "originName": f.get("originName", f.get("name", "")),
                    "name": f.get("name", ""),
                    "dataeaseName": f.get("name", ""),
                    "fieldShortName": f.get("name", ""),
                    "groupType": "d",
                    "type": f.get("type", "varchar"),
                    "deType": f.get("deType", 0),
                    "deExtractType": 0,
                    "extField": 0,
                    "checked": True,
                    "columnIndex": idx,
                    "datasourceId": ids["datasource"],
                })

            print("Step 9: Datasource types")
            types_resp = await client.get("/de2api/datasource/types", headers=headers)
            types_body = _assert_ok(types_resp, "Step 9")
            types_data = _data_list(types_body, "Step 9")
            assert any(item.get("type") == "mysql" for item in types_data if isinstance(item, dict)), f"Step 9 failed: {types_data}"

            print("Step 10: Datasource rename")
            rename_resp = await client.post(
                "/de2api/datasource/reName",
                headers=headers,
                json={"id": ids["datasource"], "name": ds_renamed},
            )
            rename_body = _assert_ok(rename_resp, "Step 10")
            assert rename_body["data"] is None, f"Step 10 failed: {rename_body}"

            print("Step 11: Datasource latest use")
            latest_resp = await client.post("/de2api/datasource/latestUse", headers=headers)
            latest_body = _assert_ok(latest_resp, "Step 11")
            latest_data = _data_list(latest_body, "Step 11")
            assert "mysql" in latest_data, f"Step 11 failed: {latest_data}"

            print("Step 13: Dataset create folder")
            dataset_folder_resp = await client.post(
                "/de2api/datasetTree/create",
                headers=headers,
                json={"name": dataset_folder_name, "pid": 0, "nodeType": "folder"},
            )
            dataset_folder_body = _assert_ok(dataset_folder_resp, "Step 13")
            ids["dataset_folder"] = int(_data_dict(dataset_folder_body, "Step 13")["id"])

            print("Step 14: Dataset create")
            dataset_resp = await client.post(
                "/de2api/datasetTree/create",
                headers=headers,
                json={
                    "name": dataset_name,
                    "pid": ids["dataset_folder"],
                    "nodeType": "dataset",
                    "type": "sql",
                    "mode": 0,
                    "datasourceId": ids["datasource"],
                    "tableName": table_name,
                    "info": {"datasourceId": ids["datasource"], "table": table_name, "sql": f"SELECT * FROM {table_name}"},
                    "allFields": [],
                },
            )
            dataset_body = _assert_ok(dataset_resp, "Step 14")
            dataset_data = _data_dict(dataset_body, "Step 14")
            ids["dataset"] = int(dataset_data["id"])
            assert dataset_data["name"] == dataset_name, f"Step 14 failed: {dataset_data}"

            print("Step 15: Dataset save")
            dataset_save_resp = await client.post(
                "/de2api/datasetTree/save",
                headers=headers,
                json={
                    "id": ids["dataset"],
                    "name": dataset_saved_name,
                    "pid": ids["dataset_folder"],
                    "nodeType": "dataset",
                    "type": "sql",
                    "mode": 0,
                    "datasourceId": ids["datasource"],
                    "tableName": table_name,
                    "info": {"datasourceId": ids["datasource"], "table": table_name, "sql": f"SELECT * FROM {table_name}"},
                    "allFields": ds_fields,
                },
            )
            dataset_save_body = _assert_ok(dataset_save_resp, "Step 15")
            assert _data_dict(dataset_save_body, "Step 15")["name"] == dataset_saved_name, f"Step 15 failed: {dataset_save_body}"

            print("Step 16: Dataset tree")
            dataset_tree_resp = await client.post("/de2api/datasetTree/tree", headers=headers, json={"busiFlag": "dataset"})
            dataset_tree_body = _assert_ok(dataset_tree_resp, "Step 16")
            assert find_node_by_id(dataset_tree_body["data"], ids["dataset"]) is not None, f"Step 16 failed: {dataset_tree_body}"

            print("Step 17: Dataset bar info")
            bar_resp = await client.get(f"/de2api/datasetTree/barInfo/{ids['dataset']}", headers=headers)
            bar_body = _assert_ok(bar_resp, "Step 17")
            bar_data = _data_dict(bar_body, "Step 17")
            assert str(bar_data["id"]) == str(ids["dataset"]), f"Step 17 failed: {bar_data}"

            print("Step 18: Dataset get")
            dataset_get_resp = await client.post(f"/de2api/datasetTree/get/{ids['dataset']}", headers=headers)
            dataset_get_body = _assert_ok(dataset_get_resp, "Step 18")
            dataset_get_data = _data_dict(dataset_get_body, "Step 18")
            assert str(dataset_get_data["id"]) == str(ids["dataset"]), f"Step 18 failed: {dataset_get_data}"

            print("Step 19: Dataset details")
            details_resp = await client.post(f"/de2api/datasetTree/details/{ids['dataset']}", headers=headers)
            details_body = _assert_ok(details_resp, "Step 19")
            details_data = _data_dict(details_body, "Step 19")
            assert str(details_data["id"]) == str(ids["dataset"]), f"Step 19 failed: {details_data}"
            all_fields = cast(list[dict[str, Any]], details_data["allFields"])
            assert len(all_fields) > 0, f"Step 19 failed: {details_data}"
            dataset_field = all_fields[0]

            print("Step 20: Dataset table field")
            table_field_resp = await client.post(
                "/de2api/datasetData/tableField",
                headers=headers,
                json={"datasetGroupId": ids["dataset"]},
            )
            table_field_body = _assert_ok(table_field_resp, "Step 20")
            table_field_data = _data_list(table_field_body, "Step 20")
            assert len(table_field_data) > 0, f"Step 20 failed: {table_field_body}"

            print("Step 21: Dataset preview sql")
            preview_sql_resp = await client.post(
                "/de2api/datasetData/previewSql",
                headers=headers,
                json={
                    "datasourceId": ids["datasource"],
                    "sql": base64.b64encode(f"SELECT * FROM {table_name}".encode("utf-8")).decode("utf-8"),
                },
            )
            preview_sql_body = _assert_ok(preview_sql_resp, "Step 21")
            preview_sql_data = _data_dict(preview_sql_body, "Step 21")
            assert preview_sql_data["total"] >= 0, f"Step 21 failed: {preview_sql_data}"

            print("Step 22: Dashboard create folder")
            dashboard_folder_resp = await client.post(
                "/de2api/dataVisualization/save",
                headers=headers,
                json={"name": dashboard_folder_name, "nodeType": "folder", "pid": 0, "type": "dashboard"},
            )
            dashboard_folder_body = _assert_ok(dashboard_folder_resp, "Step 22")
            ids["dashboard_folder"] = int(_data_dict(dashboard_folder_body, "Step 22")["id"])

            print("Step 23: Dashboard create")
            dashboard_resp = await client.post(
                "/de2api/dataVisualization/save",
                headers=headers,
                json={"name": dashboard_name, "nodeType": "leaf", "pid": ids["dashboard_folder"], "type": "dashboard"},
            )
            dashboard_body = _assert_ok(dashboard_resp, "Step 23")
            ids["dashboard"] = int(_data_dict(dashboard_body, "Step 23")["id"])

            print("Step 24: Chart save")
            x_axis = [{
                "id": dataset_field.get("id"),
                "name": dataset_field.get("name") or dataset_field.get("originName"),
                "dataeaseName": dataset_field.get("dataeaseName") or dataset_field.get("originName"),
                "summary": "none",
            }]
            chart_payload = {
                "title": chart_name,
                "sceneId": ids["dashboard"],
                "tableId": ids["dataset"],
                "type": "bar",
                "chartType": "bar",
                "render": "antv",
                "xAxis": x_axis,
                "yAxis": [],
                "viewFields": x_axis,
                "customAttr": {},
                "customStyle": {},
            }
            chart_resp = await client.post("/de2api/chart/save", headers=headers, json=chart_payload)
            chart_body = _assert_ok(chart_resp, "Step 24")
            chart_data = _data_dict(chart_body, "Step 24")
            ids["chart"] = int(chart_data["id"])
            assert chart_data["title"] == chart_name, f"Step 24 failed: {chart_data}"

            print("Step 25: Chart get")
            chart_get_resp = await client.get(f"/de2api/chart/{ids['chart']}", headers=headers)
            chart_get_body = _assert_ok(chart_get_resp, "Step 25")
            chart_get_data = _data_dict(chart_get_body, "Step 25")
            assert str(chart_get_data["id"]) == str(ids["chart"]), f"Step 25 failed: {chart_get_data}"

            print("Step 26: Chart detail")
            chart_detail_resp = await client.get(f"/de2api/chart/getDetail/{ids['chart']}", headers=headers)
            chart_detail_body = _assert_ok(chart_detail_resp, "Step 26")
            chart_detail_data = _data_dict(chart_detail_body, "Step 26")
            assert str(chart_detail_data["chart"]["id"]) == str(ids["chart"]), f"Step 26 failed: {chart_detail_data}"

            print("Step 27: Chart data")
            chart_data_resp = await client.post(
                "/de2api/chart/getData",
                headers=headers,
                json={"id": ids["chart"], "sceneId": ids["dashboard"], "tableId": ids["dataset"], "xAxis": x_axis},
            )
            chart_data_body = _assert_ok(chart_data_resp, "Step 27")
            chart_data_payload = _data_dict(chart_data_body, "Step 27")
            assert str(chart_data_payload["chartId"]) == str(ids["chart"]), f"Step 27 failed: {chart_data_payload}"

            print("Step 28: Chart update")
            chart_update_resp = await client.post(
                "/de2api/chart/update",
                headers=headers,
                json={**chart_payload, "id": ids["chart"], "title": chart_updated_name},
            )
            chart_update_body = _assert_ok(chart_update_resp, "Step 28")
            assert _data_dict(chart_update_body, "Step 28")["title"] == chart_updated_name, f"Step 28 failed: {chart_update_body}"

            print("Step 29: Chart view detail list")
            chart_list_resp = await client.post(
                "/de2api/chart/viewDetailList",
                headers=headers,
                json={"sceneId": ids["dashboard"]},
            )
            chart_list_body = _assert_ok(chart_list_resp, "Step 29")
            chart_list_data = _data_list(chart_list_body, "Step 29")
            assert any(str(item.get("id")) == str(ids["chart"]) for item in chart_list_data if isinstance(item, dict)), f"Step 29 failed: {chart_list_data}"

            print("Step 30: Org create")
            org_resp = await client.post("/de2api/org/page/create", headers=headers, json={"name": org_name, "pid": 0})
            org_body = _assert_ok(org_resp, "Step 30")
            org_data = _data_dict(org_body, "Step 30")
            ids["org"] = int(org_data["id"])
            assert org_data["name"] == org_name, f"Step 30 failed: {org_data}"

            print("Step 31: Org tree")
            org_tree_resp = await client.post("/de2api/org/page/tree", headers=headers, json={})
            org_tree_body = _assert_ok(org_tree_resp, "Step 31")
            assert find_node_by_id(org_tree_body["data"], ids["org"]) is not None, f"Step 31 failed: {org_tree_body}"

            print("Step 32: Org edit")
            org_edit_resp = await client.post(
                "/de2api/org/page/edit",
                headers=headers,
                json={"id": ids["org"], "name": org_renamed},
            )
            org_edit_body = _assert_ok(org_edit_resp, "Step 32")
            assert _data_dict(org_edit_body, "Step 32")["name"] == org_renamed, f"Step 32 failed: {org_edit_body}"

            print("Step 33: Org mounted/resource exist")
            org_mounted_resp = await client.post("/de2api/org/mounted", headers=headers, json={"keyword": org_renamed})
            org_mounted_body = _assert_ok(org_mounted_resp, "Step 33a")
            org_mounted_data = _data_list(org_mounted_body, "Step 33a")
            assert any(str(item.get("id")) == str(ids["org"]) for item in org_mounted_data if isinstance(item, dict)), f"Step 33a failed: {org_mounted_data}"
            org_exist_resp = await client.get(f"/de2api/org/resourceExist/{ids['org']}", headers=headers)
            org_exist_body = _assert_ok(org_exist_resp, "Step 33b")
            assert org_exist_body["data"] is False, f"Step 33b failed: {org_exist_body}"

            print("Step 33c: Switch to test org")
            switch_org_resp = await client.post(f"/de2api/user/switch/{ids['org']}", headers=headers)
            switch_org_body = _assert_ok(switch_org_resp, "Step 33c")
            switch_org_data = _data_dict(switch_org_body, "Step 33c")
            switched_token = switch_org_data["token"]
            assert isinstance(switched_token, str) and switched_token, f"Step 33c failed: {switch_org_body}"
            org_headers = {"X-DE-TOKEN": switched_token}

            print("Step 34: Role create")
            role_resp = await client.post(
                "/de2api/role/create",
                headers=org_headers,
                json={"name": role_name, "description": "e2e role"},
            )
            role_body = _assert_ok(role_resp, "Step 34")
            role_data = _data_dict(role_body, "Step 34")
            ids["role"] = int(role_data["id"])
            assert role_data["name"] == role_name, f"Step 34 failed: {role_data}"

            print("Step 35: Role query/detail/edit")
            role_query_resp = await client.post("/de2api/role/query", headers=org_headers, json={"keyword": role_name})
            role_query_body = _assert_ok(role_query_resp, "Step 35a")
            role_query_data = _data_list(role_query_body, "Step 35a")
            assert any(str(item.get("id")) == str(ids["role"]) for item in role_query_data if isinstance(item, dict)), f"Step 35a failed: {role_query_data}"
            role_detail_resp = await client.get(f"/de2api/role/detail/{ids['role']}", headers=org_headers)
            role_detail_body = _assert_ok(role_detail_resp, "Step 35b")
            assert _data_dict(role_detail_body, "Step 35b")["name"] == role_name, f"Step 35b failed: {role_detail_body}"
            role_edit_resp = await client.post(
                "/de2api/role/edit",
                headers=org_headers,
                json={"id": ids["role"], "name": role_renamed, "description": "e2e role updated"},
            )
            role_edit_body = _assert_ok(role_edit_resp, "Step 35c")
            assert _data_dict(role_edit_body, "Step 35c")["name"] == role_renamed, f"Step 35c failed: {role_edit_body}"

            print("Step 36: User create")
            user_resp = await client.post(
                "/de2api/user/create",
                headers=org_headers,
                json={
                    "account": user_account,
                    "name": user_name,
                    "email": f"{user_account}@example.com",
                    "phone": "13800000000",
                    "roleIds": [ids["role"]],
                },
            )
            user_body = _assert_ok(user_resp, "Step 36")
            user_data = _data_dict(user_body, "Step 36")
            ids["user"] = int(user_data["id"])
            assert user_data["account"] == user_account, f"Step 36 failed: {user_data}"

            print("Step 37: User pager/edit/query")
            user_pager_resp = await client.post("/de2api/user/pager/1/10", headers=org_headers, json={"keyword": user_account})
            user_pager_body = _assert_ok(user_pager_resp, "Step 37a")
            user_pager_data = _data_dict(user_pager_body, "Step 37a")
            assert any(str(item.get("id")) == str(ids["user"]) for item in user_pager_data["items"]), f"Step 37a failed: {user_pager_data}"
            user_edit_resp = await client.post(
                "/de2api/user/edit",
                headers=org_headers,
                json={"id": ids["user"], "name": user_updated_name, "email": f"updated_{user_account}@example.com", "phone": "13900000000", "roleIds": [ids["role"]]},
            )
            user_edit_body = _assert_ok(user_edit_resp, "Step 37b")
            assert _data_dict(user_edit_body, "Step 37b")["name"] == user_updated_name, f"Step 37b failed: {user_edit_body}"
            user_query_resp = await client.get(f"/de2api/user/queryById/{ids['user']}", headers=org_headers)
            user_query_body = _assert_ok(user_query_resp, "Step 37c")
            user_query_data = _data_dict(user_query_body, "Step 37c")
            assert user_query_data["account"] == user_account, f"Step 37c failed: {user_query_data}"

            print("Step 38: Role mount/query selected/unmount")
            role_mount_resp = await client.post(
                "/de2api/role/mountUser",
                headers=org_headers,
                json={"roleId": ids["role"], "userIds": [ids["user"]]},
            )
            role_mount_body = _assert_ok(role_mount_resp, "Step 38a")
            assert role_mount_body["data"] is None, f"Step 38a failed: {role_mount_body}"
            role_selected_resp = await client.post(
                "/de2api/user/role/selected/1/10",
                headers=org_headers,
                json={"roleId": ids["role"]},
            )
            role_selected_body = _assert_ok(role_selected_resp, "Step 38b")
            role_selected_data = _data_dict(role_selected_body, "Step 38b")
            assert any(str(item.get("id")) == str(ids["user"]) for item in role_selected_data["items"]), f"Step 38b failed: {role_selected_data}"
            role_unmount_resp = await client.post(
                "/de2api/role/unMountUser",
                headers=org_headers,
                json={"roleId": ids["role"], "userIds": [ids["user"]]},
            )
            role_unmount_body = _assert_ok(role_unmount_resp, "Step 38c")
            assert role_unmount_body["data"] is None, f"Step 38c failed: {role_unmount_body}"
            role_unmount_query_resp = await client.get(f"/de2api/user/queryById/{ids['user']}", headers=org_headers)
            if role_unmount_query_resp.status_code == 404:
                ids["user_deleted"] = True
            else:
                role_unmount_query_body = _assert_ok(role_unmount_query_resp, "Step 38d")
                assert _data_dict(role_unmount_query_body, "Step 38d")["id"] == ids["user"], f"Step 38d failed: {role_unmount_query_body}"

            print("Step 39: Template category seed")
            category_row = await _pg_fetchrow(
                "SELECT id FROM visualization_template_category WHERE id = $1",
                template_category_id,
            )
            assert category_row is None, f"Step 39 failed: category already exists {template_category_id}"
            await _pg_execute(
                """
                INSERT INTO visualization_template_category
                (id, name, pid, level, dv_type, node_type, create_by, create_time, snapshot, template_type)
                VALUES ($1, $2, '0', 0, 'dashboard', 'folder', '1', $3, NULL, 'self')
                """,
                template_category_id,
                template_category_name,
                int(time.time() * 1000),
            )
            ids["template_category"] = template_category_id

            print("Step 40: Template category CRUD via HTTP reads")
            template_categories_resp = await client.post("/de2api/templateManage/categories", headers=headers)
            template_categories_body = _assert_ok(template_categories_resp, "Step 40a")
            template_categories = _data_list(template_categories_body, "Step 40a")
            assert any(str(item.get("id")) == template_category_id for item in template_categories if isinstance(item, dict)), f"Step 40a failed: {template_categories}"
            category_form_resp = await client.post(
                "/de2api/templateManage/categoryForm",
                headers=headers,
                json={"categoryId": template_category_id},
            )
            category_form_body = _assert_ok(category_form_resp, "Step 40b")
            category_form_data = _data_dict(category_form_body, "Step 40b")
            assert category_form_data["category"]["name"] == template_category_name, f"Step 40b failed: {category_form_data}"

            print("Step 41: Template save")
            template_resp = await client.post(
                "/de2api/templateManage/save",
                headers=headers,
                json={
                    "name": template_name,
                    "pid": "0",
                    "dvType": "dashboard",
                    "nodeType": "panel",
                    "templateType": "self",
                    "snapshot": "{}",
                    "templateStyle": {},
                    "templateData": {},
                    "dynamicData": {},
                },
            )
            template_body = _assert_ok(template_resp, "Step 41")
            template_data = _data_dict(template_body, "Step 41")
            ids["template"] = str(template_data["id"])
            assert template_data["name"] == template_name, f"Step 41 failed: {template_data}"

            print("Step 42: Template name checks/list/find")
            name_check_resp = await client.post(
                "/de2api/templateManage/nameCheck",
                headers=headers,
                json={"name": template_name, "optType": "new"},
            )
            name_check_body = _assert_ok(name_check_resp, "Step 42a")
            assert name_check_body["data"] == "exist_all", f"Step 42a failed: {name_check_body}"
            batch_update_resp = await client.post(
                "/de2api/templateManage/batchUpdate",
                headers=headers,
                json={"templateIds": [ids["template"]], "categories": [template_category_id]},
            )
            batch_update_body = _assert_ok(batch_update_resp, "Step 42b")
            assert batch_update_body["data"] is None, f"Step 42b failed: {batch_update_body}"
            template_find_resp = await client.post(
                "/de2api/templateManage/find",
                headers=headers,
                json={"templateId": ids["template"]},
            )
            template_find_body = _assert_ok(template_find_resp, "Step 42c")
            template_find_data = _data_list(template_find_body, "Step 42c")
            assert len(template_find_data) == 1 and template_find_data[0]["id"] == ids["template"], f"Step 42c failed: {template_find_data}"
            template_find_one_resp = await client.get(f"/de2api/templateManage/findOne/{ids['template']}", headers=headers)
            template_find_one_body = _assert_ok(template_find_one_resp, "Step 42d")
            assert _data_dict(template_find_one_body, "Step 42d")["id"] == ids["template"], f"Step 42d failed: {template_find_one_body}"
            template_list_resp = await client.post("/de2api/templateManage/list", headers=headers, json={"keyword": template_name})
            template_list_body = _assert_ok(template_list_resp, "Step 42e")
            template_list_data = _data_list(template_list_body, "Step 42e")
            assert any(item.get("id") == ids["template"] for item in template_list_data if isinstance(item, dict)), f"Step 42e failed: {template_list_data}"
            category_name_check_resp = await client.post(
                "/de2api/templateManage/categoryTemplateNameCheck",
                headers=headers,
                json={"name": template_name, "categories": [template_category_id]},
            )
            category_name_check_body = _assert_ok(category_name_check_resp, "Step 42f")
            assert category_name_check_body["data"] == "none", f"Step 42f failed: {category_name_check_body}"

            print("Step 43: System")
            menu_resp = await client.get("/de2api/menu/query", headers=headers)
            menu_body = _assert_ok(menu_resp, "Step 43a")
            menu_data = _data_list(menu_body, "Step 43a")
            assert isinstance(menu_data, list), f"Step 43a failed: {menu_body}"
            font_resp = await client.get("/de2api/font/listFont", headers=headers)
            font_body = _assert_ok(font_resp, "Step 43b")
            font_data = _data_list(font_body, "Step 43b")
            assert font_data == [], f"Step 43b failed: {font_data}"
            area_resp = await client.get("/de2api/map/areaEntitys/0", headers=headers)
            area_body = _assert_ok(area_resp, "Step 43c")
            area_data = _data_list(area_body, "Step 43c")
            assert area_data == [], f"Step 43c failed: {area_data}"

            print("Step 44: Log")
            log_pager_resp = await client.post(
                "/de2api/log/pager/1/10",
                headers=headers,
                json={"keyword": None, "timeDesc": True},
            )
            log_pager_body = _assert_ok(log_pager_resp, "Step 44a")
            log_pager_data = _data_dict(log_pager_body, "Step 44a")
            assert "pager" in log_pager_data and "data" in log_pager_data, f"Step 44a failed: {log_pager_data}"
            log_options_resp = await client.get("/de2api/log/options", headers=headers)
            log_options_body = _assert_ok(log_options_resp, "Step 44b")
            log_options_data = _data_list(log_options_body, "Step 44b")
            assert len(log_options_data) > 0, f"Step 44b failed: {log_options_data}"

            print("Step 45: API key")
            apikey_generate_resp = await client.post("/de2api/apiKey/generate", headers=headers)
            apikey_generate_body = _assert_ok(apikey_generate_resp, "Step 45a")
            apikey_generate_data = _data_dict(apikey_generate_body, "Step 45a")
            ids["api_key"] = int(apikey_generate_data["id"])
            assert isinstance(apikey_generate_data["accessKey"], str) and apikey_generate_data["accessKey"], f"Step 45a failed: {apikey_generate_data}"
            apikey_query_resp = await client.get("/de2api/apiKey/query", headers=headers)
            apikey_query_body = _assert_ok(apikey_query_resp, "Step 45b")
            apikey_query_data = _data_list(apikey_query_body, "Step 45b")
            assert any(str(item.get("id")) == str(ids["api_key"]) for item in apikey_query_data if isinstance(item, dict)), f"Step 45b failed: {apikey_query_data}"
            apikey_switch_resp = await client.post(
                "/de2api/apiKey/switch",
                headers=headers,
                json={"id": ids["api_key"], "enable": False},
            )
            apikey_switch_body = _assert_ok(apikey_switch_resp, "Step 45c")
            assert apikey_switch_body["data"] is None, f"Step 45c failed: {apikey_switch_body}"

            print("Step 46: Cleanup via module delete endpoints")
            template_batch_delete_resp = await client.post(
                "/de2api/templateManage/batchDelete",
                headers=headers,
                json={"templateIds": [ids["template"]], "categories": [template_category_id]},
            )
            template_batch_delete_body = _assert_ok(template_batch_delete_resp, "Step 46a")
            assert template_batch_delete_body["data"] is None, f"Step 46a failed: {template_batch_delete_body}"
            ids["template_deleted"] = True
            template_delete_category_resp = await client.post(
                f"/de2api/templateManage/deleteCategory/{template_category_id}",
                headers=headers,
            )
            template_delete_category_body = _assert_ok(template_delete_category_resp, "Step 46b")
            assert template_delete_category_body["data"] == "success", f"Step 46b failed: {template_delete_category_body}"
            ids["template_category_deleted"] = True
            user_delete_resp = await client.post(f"/de2api/user/delete/{ids['user']}", headers=org_headers)
            if user_delete_resp.status_code == 200:
                user_delete_body = _assert_ok(user_delete_resp, "Step 46c")
                assert user_delete_body["data"] is None, f"Step 46c failed: {user_delete_body}"
            else:
                assert user_delete_resp.status_code == 404, f"Step 46c failed: {user_delete_resp.text}"
            ids["user_deleted"] = True
            role_delete_resp = await client.post(f"/de2api/role/delete/{ids['role']}", headers=org_headers)
            role_delete_body = _assert_ok(role_delete_resp, "Step 46d")
            assert role_delete_body["data"] is None, f"Step 46d failed: {role_delete_body}"
            ids["role_deleted"] = True
            org_delete_resp = await client.post(f"/de2api/org/page/delete/{ids['org']}", headers=headers)
            org_delete_body = _assert_ok(org_delete_resp, "Step 46e")
            assert org_delete_body["data"] is None, f"Step 46e failed: {org_delete_body}"
            ids["org_deleted"] = True
            chart_delete_resp = await client.post(f"/de2api/chart/del/{ids['chart']}", headers=headers)
            chart_delete_body = _assert_ok(chart_delete_resp, "Step 46f")
            assert chart_delete_body["data"] is None, f"Step 46f failed: {chart_delete_body}"
            ids["chart_deleted"] = True
            dataset_delete_resp = await client.post(f"/de2api/datasetTree/delete/{ids['dataset']}", headers=headers)
            _assert_ok(dataset_delete_resp, "Step 46g")
            ids["dataset_deleted"] = True
            dataset_folder_delete_resp = await client.post(f"/de2api/datasetTree/delete/{ids['dataset_folder']}", headers=headers)
            _assert_ok(dataset_folder_delete_resp, "Step 46h")
            ids["dataset_folder_deleted"] = True
            apikey_delete_resp = await client.post(f"/de2api/apiKey/delete/{ids['api_key']}", headers=headers)
            apikey_delete_body = _assert_ok(apikey_delete_resp, "Step 46i")
            assert apikey_delete_body["data"] is None, f"Step 46i failed: {apikey_delete_body}"
            ids["api_key_deleted"] = True
            dashboard_delete_resp = await client.post("/de2api/dataVisualization/delete", headers=headers, json={"id": ids["dashboard"]})
            dashboard_delete_body = _assert_ok(dashboard_delete_resp, "Step 46j")
            assert dashboard_delete_body["data"] is not None, f"Step 46j failed: {dashboard_delete_body}"
            ids["dashboard_deleted"] = True
            dashboard_folder_delete_resp = await client.post("/de2api/dataVisualization/delete", headers=headers, json={"id": ids["dashboard_folder"]})
            dashboard_folder_delete_body = _assert_ok(dashboard_folder_delete_resp, "Step 46k")
            assert dashboard_folder_delete_body["data"] is not None, f"Step 46k failed: {dashboard_folder_delete_body}"
            ids["dashboard_folder_deleted"] = True
            ds_delete_resp = await client.post(f"/de2api/datasource/delete/{ids['datasource']}", headers=headers)
            ds_delete_body = _assert_ok(ds_delete_resp, "Step 46l")
            assert ds_delete_body["data"] is None, f"Step 46l failed: {ds_delete_body}"
            ids["datasource_deleted"] = True
            ds_folder_delete_resp = await client.post(f"/de2api/datasource/delete/{ids['ds_folder']}", headers=headers)
            ds_folder_delete_body = _assert_ok(ds_folder_delete_resp, "Step 46m")
            assert ds_folder_delete_body["data"] is None, f"Step 46m failed: {ds_folder_delete_body}"
            ids["ds_folder_deleted"] = True

        finally:
            if headers and ids.get("chart") and not ids.get("chart_deleted"):
                await client.post(f"/de2api/chart/del/{ids['chart']}", headers=headers)
            if ids.get("dataset") and not ids.get("dataset_deleted"):
                await client.post(f"/de2api/datasetTree/delete/{ids['dataset']}", headers=headers)
            if ids.get("dataset_folder") and not ids.get("dataset_folder_deleted"):
                await client.post(f"/de2api/datasetTree/delete/{ids['dataset_folder']}", headers=headers)
            if headers and ids.get("dashboard") and not ids.get("dashboard_deleted"):
                await client.post("/de2api/dataVisualization/delete", headers=headers, json={"id": ids["dashboard"]})
            if headers and ids.get("dashboard_folder") and not ids.get("dashboard_folder_deleted"):
                await client.post("/de2api/dataVisualization/delete", headers=headers, json={"id": ids["dashboard_folder"]})
            if org_headers and ids.get("user") and not ids.get("user_deleted"):
                user_delete_resp = await client.post(f"/de2api/user/delete/{ids['user']}", headers=org_headers)
                assert user_delete_resp.status_code in (200, 404)
            if org_headers and ids.get("role") and not ids.get("role_deleted"):
                await client.post(f"/de2api/role/delete/{ids['role']}", headers=org_headers)
            if headers and ids.get("org") and not ids.get("org_deleted"):
                await client.post(f"/de2api/org/page/delete/{ids['org']}", headers=headers)
            if headers and ids.get("api_key") and not ids.get("api_key_deleted"):
                await client.post(f"/de2api/apiKey/delete/{ids['api_key']}", headers=headers)
            if headers and ids.get("datasource") and not ids.get("datasource_deleted"):
                await client.post(f"/de2api/datasource/delete/{ids['datasource']}", headers=headers)
            if headers and ids.get("ds_folder") and not ids.get("ds_folder_deleted"):
                await client.post(f"/de2api/datasource/delete/{ids['ds_folder']}", headers=headers)
            if ids.get("template") and not ids.get("template_deleted") and headers and ids.get("template_category"):
                await client.post(
                    "/de2api/templateManage/batchDelete",
                    headers=headers,
                    json={"templateIds": [ids["template"]], "categories": [ids["template_category"]]},
                )
            if ids.get("template_category") and not ids.get("template_category_deleted") and headers:
                await client.post(f"/de2api/templateManage/deleteCategory/{ids['template_category']}", headers=headers)
            if ids.get("template_category") and not ids.get("template_category_deleted"):
                await _pg_execute("DELETE FROM visualization_template_category WHERE id = $1", ids["template_category"])
