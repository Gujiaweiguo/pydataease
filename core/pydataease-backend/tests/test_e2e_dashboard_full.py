"""E2E dashboard lifecycle — create, saveCanvas, update, share, linkage, cleanup."""
from __future__ import annotations

import json
import time
from typing import Any, cast

import httpx
import pytest

from tests.fixtures.e2e_helpers import (  # pyright: ignore[reportImplicitRelativeImport]
    BASE_URL,
    E2E_GATE,
    assert_ok,
    data_dict,
    data_list,
    find_component_by_id,
    find_node_by_id,
    login,
)


@E2E_GATE
@pytest.mark.asyncio
async def test_e2e_dashboard_full() -> None:
    ids: dict[str, int | str] = {}
    headers: dict[str, str] = {}
    stamp = int(time.time() * 1000)
    folder_name = f"E2E Dashboard Folder {stamp}"
    dashboard_name = f"E2E Dashboard {stamp}"
    updated_dashboard_name = f"{dashboard_name} Updated"
    renamed_dashboard_name = f"{dashboard_name} Renamed"
    watermark_content = json.dumps({"type": "custom", "content": f"e2e-{stamp}", "enable": True})

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as api_client:
        try:
            # === Step 1: Login ===
            headers = await login(api_client)
            print("Step 1: Login - OK")

            # === Step 2: Create Folder ===
            folder_response = await api_client.post(
                "/de2api/dataVisualization/save",
                headers=headers,
                json={"name": folder_name, "nodeType": "folder", "pid": 0, "type": "panel"},
            )
            folder_body = assert_ok(folder_response)
            folder_data = data_dict(folder_body)
            ids["folder"] = int(folder_data["id"])
            assert folder_data["name"] == folder_name
            print(f"Step 2: Create Folder - OK (id={ids['folder']})")

            # === Step 3: Create Dashboard ===
            dashboard_response = await api_client.post(
                "/de2api/dataVisualization/save",
                headers=headers,
                json={"name": dashboard_name, "nodeType": "leaf", "pid": ids["folder"], "type": "panel"},
            )
            dashboard_body = assert_ok(dashboard_response)
            dashboard_data = data_dict(dashboard_body)
            ids["dashboard"] = int(dashboard_data["id"])
            assert dashboard_data["name"] == dashboard_name
            print(f"Step 3: Create Dashboard - OK (id={ids['dashboard']})")

            # === Step 4: Tree Browse ===
            tree_response = await api_client.post(
                "/de2api/dataVisualization/tree",
                headers=headers,
                json={"busiFlag": "dashboard"},
            )
            tree_body = assert_ok(tree_response)
            tree_node = find_node_by_id(tree_body["data"], int(ids["dashboard"]))
            assert tree_node is not None
            assert tree_node["name"] == dashboard_name
            print(f"Step 4: Tree Browse - OK (id={ids['dashboard']})")

            # === Step 5: Find By ID ===
            find_response = await api_client.post(
                "/de2api/dataVisualization/findById",
                headers=headers,
                json={"id": ids["dashboard"], "busiFlag": "dashboard"},
            )
            find_body = assert_ok(find_response)
            find_data = data_dict(find_body)
            assert str(find_data["id"]) == str(ids["dashboard"])
            assert find_data["name"] == dashboard_name
            print(f"Step 5: Find By ID - OK (id={ids['dashboard']})")

            # === Step 6: Name Check ===
            name_check_new = await api_client.post(
                "/de2api/dataVisualization/nameCheck",
                headers=headers,
                json={"name": f"{dashboard_name} Unique", "pid": ids["folder"], "type": "panel", "nodeType": "leaf", "opt": "new"},
            )
            name_check_new_body = assert_ok(name_check_new)
            assert name_check_new_body["data"] is True
            name_check_existing = await api_client.post(
                "/de2api/dataVisualization/nameCheck",
                headers=headers,
                json={"name": dashboard_name, "pid": ids["folder"], "type": "panel", "nodeType": "leaf", "opt": "new"},
            )
            name_check_existing_body = assert_ok(name_check_existing)
            assert name_check_existing_body["data"] is False
            print(f"Step 6: Name Check - OK (id={ids['dashboard']})")

            chart_ids = {
                "indicator": int(time.time_ns()),
                "tab_chart": int(time.time_ns()) + 1,
                "group_chart": int(time.time_ns()) + 2,
            }
            chart_dataset_id = str(int(time.time_ns()) + 3)
            component_data: list[dict[str, Any]] = [
                {
                    "id": "text-1",
                    "component": "VText",
                    "label": "Overview",
                    "propValue": "Revenue Overview",
                    "rect": {"x": 16, "y": 20, "w": 12, "h": 4},
                },
                {
                    "id": "view-indicator-1",
                    "component": "UserView",
                    "innerType": "indicator",
                    "datasetId": chart_dataset_id,
                    "label": "指标卡",
                    "name": "指标卡",
                    "canvasId": "canvas-main",
                    "rect": {"x": 16, "y": 28, "w": 12, "h": 8},
                },
                {
                    "id": "query-1",
                    "component": "VQuery",
                    "innerType": "VQuery",
                    "canvasId": "canvas-main",
                    "propValue": [],
                    "rect": {"x": 2, "y": 2, "w": 8, "h": 3},
                },
                {
                    "id": "picture-1",
                    "component": "Picture",
                    "innerType": "Picture",
                    "canvasId": "canvas-main",
                    "propValue": {"url": "https://example.com/pic.png"},
                    "rect": {"x": 30, "y": 20, "w": 8, "h": 6},
                },
                {
                    "id": "video-1",
                    "component": "DeVideo",
                    "innerType": "DeVideo",
                    "canvasId": "canvas-main",
                    "propValue": {"url": "https://example.com/video.mp4"},
                    "rect": {"x": 40, "y": 20, "w": 8, "h": 6},
                },
                {
                    "id": "stream-1",
                    "component": "DeStreamMedia",
                    "innerType": "DeStreamMedia",
                    "canvasId": "canvas-main",
                    "streamMediaLinks": {
                        "videoType": "mp4",
                        "mp4": {"url": "https://example.com/live.mp4", "loop": True, "isLive": False},
                    },
                    "rect": {"x": 50, "y": 20, "w": 8, "h": 6},
                },
                {
                    "id": "tabs-1",
                    "component": "DeTabs",
                    "innerType": "DeTabs",
                    "canvasId": "canvas-main",
                    "editableTabsValue": "tab-a",
                    "propValue": [
                        {
                            "name": "tab-a",
                            "title": "Tab A",
                            "componentData": [
                                {
                                    "id": "tab-chart-1",
                                    "component": "UserView",
                                    "innerType": "bar",
                                    "datasetId": chart_dataset_id,
                                    "canvasId": "tabs-1--tab-a",
                                },
                                {
                                    "id": "tab-query-1",
                                    "component": "VQuery",
                                    "innerType": "VQuery",
                                    "canvasId": "tabs-1--tab-a",
                                    "propValue": [],
                                },
                            ],
                        }
                    ],
                    "rect": {"x": 16, "y": 40, "w": 20, "h": 10},
                },
                {
                    "id": "group-1",
                    "component": "Group",
                    "innerType": "Group",
                    "canvasId": "canvas-main",
                    "propValue": [
                        {
                            "id": "group-chart-1",
                            "component": "UserView",
                            "innerType": "line",
                            "datasetId": chart_dataset_id,
                            "canvasId": "group-1",
                        }
                    ],
                    "rect": {"x": 40, "y": 40, "w": 16, "h": 10},
                },
                {
                    "id": "rich-text-1",
                    "component": "UserView",
                    "innerType": "rich-text",
                    "canvasId": "canvas-main",
                    "propValue": {"textValue": "<p>Dashboard Note</p>"},
                    "rect": {"x": 16, "y": 54, "w": 20, "h": 6},
                },
            ]
            canvas_view_info = {
                str(chart_ids["indicator"]): {
                    "id": str(chart_ids["indicator"]),
                    "title": "指标卡",
                    "type": "indicator",
                    "render": "custom",
                    "tableId": chart_dataset_id,
                    "resultCount": "1000",
                    "resultMode": "custom",
                    "xAxis": [],
                    "xAxisExt": [],
                    "yAxis": [],
                    "yAxisExt": [],
                    "customAttr": {"basicStyle": {"alpha": 100}},
                    "customStyle": {},
                    "customFilter": {},
                    "drillFields": [],
                    "senior": {},
                    "viewFields": [],
                },
                str(chart_ids["tab_chart"]): {
                    "id": str(chart_ids["tab_chart"]),
                    "title": "Tab Chart",
                    "type": "bar",
                    "render": "antv",
                    "tableId": chart_dataset_id,
                    "resultCount": "500",
                    "resultMode": "custom",
                    "xAxis": [],
                    "xAxisExt": [],
                    "yAxis": [],
                    "yAxisExt": [],
                    "customAttr": {"label": {"show": True}},
                    "customStyle": {},
                    "customFilter": {},
                    "drillFields": [],
                    "senior": {},
                    "viewFields": [],
                },
                str(chart_ids["group_chart"]): {
                    "id": str(chart_ids["group_chart"]),
                    "title": "Group Chart",
                    "type": "line",
                    "render": "antv",
                    "tableId": chart_dataset_id,
                    "resultCount": "250",
                    "resultMode": "custom",
                    "xAxis": [],
                    "xAxisExt": [],
                    "yAxis": [],
                    "yAxisExt": [],
                    "customAttr": {"basicStyle": {"lineWidth": 2}},
                    "customStyle": {},
                    "customFilter": {},
                    "drillFields": [],
                    "senior": {},
                    "viewFields": [],
                },
            }
            canvas_style_data = {
                "width": 1920,
                "height": 1080,
                "backgroundColor": "#f5f6f7",
                "screenScale": {"x": 1, "y": 1},
            }

            # === Step 7: Save Canvas ===
            save_canvas_response = await api_client.post(
                "/de2api/dataVisualization/saveCanvas",
                headers=headers,
                json={
                    "id": ids["dashboard"],
                    "name": dashboard_name,
                    "pid": ids["folder"],
                    "type": "dashboard",
                    "componentData": json.dumps(component_data),
                    "canvasStyleData": json.dumps(canvas_style_data),
                    "canvasViewInfo": canvas_view_info,
                    "mobileLayout": False,
                },
            )
            save_canvas_body = assert_ok(save_canvas_response)
            save_canvas_data = data_dict(save_canvas_body)
            assert str(save_canvas_data["id"]) == str(ids["dashboard"])
            ids["content_id"] = str(save_canvas_data.get("contentId") or "")
            ids["check_version"] = str(save_canvas_data.get("checkVersion") or "")
            print(f"Step 7: Save Canvas - OK (id={ids['dashboard']})")

            # === Step 8: Update Canvas ===
            component_data[0]["propValue"] = "Revenue Overview Updated"
            component_data[1]["name"] = "指标卡更新"
            component_data[-1]["propValue"]["textValue"] = "<p>Dashboard Note Updated</p>"
            component_data.append(
                {
                    "id": "shape-1",
                    "component": "VShape",
                    "style": {"backgroundColor": "#1890ff"},
                    "rect": {"x": 40, "y": 20, "w": 10, "h": 6},
                }
            )
            update_canvas_response = await api_client.post(
                "/de2api/dataVisualization/updateCanvas",
                headers=headers,
                json={
                    "id": ids["dashboard"],
                    "name": dashboard_name,
                    "pid": ids["folder"],
                    "type": "dashboard",
                    "componentData": json.dumps(component_data),
                    "canvasStyleData": json.dumps({**canvas_style_data, "backgroundColor": "#ffffff"}),
                    "canvasViewInfo": {
                        **canvas_view_info,
                        str(chart_ids["indicator"]): {
                            **canvas_view_info[str(chart_ids["indicator"])],
                            "title": "指标卡更新",
                            "customAttr": {"basicStyle": {"alpha": 90}},
                        },
                    },
                    "contentId": ids["content_id"],
                    "checkVersion": ids["check_version"],
                    "mobileLayout": False,
                },
            )
            update_canvas_body = assert_ok(update_canvas_response)
            update_canvas_data = data_dict(update_canvas_body)
            assert update_canvas_data["status"] == 2
            print(f"Step 8: Update Canvas - OK (id={ids['dashboard']})")

            verify_canvas_response = await api_client.post(
                "/de2api/dataVisualization/findById",
                headers=headers,
                json={"id": ids["dashboard"], "busiFlag": "dashboard"},
            )
            verify_canvas_body = assert_ok(verify_canvas_response)
            verify_canvas_data = data_dict(verify_canvas_body)
            saved_component_data = json.loads(cast(str, verify_canvas_data["componentData"]))
            saved_canvas_view_info = cast(dict[str, Any], verify_canvas_data["canvasViewInfo"])
            assert find_component_by_id(saved_component_data, "view-indicator-1") is not None
            assert find_component_by_id(saved_component_data, "query-1") is not None
            assert find_component_by_id(saved_component_data, "picture-1") is not None
            assert find_component_by_id(saved_component_data, "video-1") is not None
            assert find_component_by_id(saved_component_data, "stream-1") is not None
            assert find_component_by_id(saved_component_data, "tabs-1") is not None
            assert find_component_by_id(saved_component_data, "group-1") is not None
            assert find_component_by_id(saved_component_data, "rich-text-1") is not None
            assert saved_canvas_view_info[str(chart_ids["indicator"])] ["title"] == "指标卡更新"
            assert saved_canvas_view_info[str(chart_ids["tab_chart"])] ["title"] == "Tab Chart"
            assert saved_canvas_view_info[str(chart_ids["group_chart"])] ["title"] == "Group Chart"

            # === Step 9: Update Base ===
            update_base_response = await api_client.post(
                "/de2api/dataVisualization/updateBase",
                headers=headers,
                json={"id": ids["dashboard"], "name": updated_dashboard_name, "pid": ids["folder"], "type": "dashboard", "mobileLayout": True},
            )
            update_base_body = assert_ok(update_base_response)
            update_base_data = data_dict(update_base_body)
            assert update_base_data["name"] == updated_dashboard_name
            print(f"Step 9: Update Base - OK (id={ids['dashboard']})")

            # === Step 10: Rename ===
            rename_response = await api_client.post(
                "/de2api/dataVisualization/reName",
                headers=headers,
                json={"id": ids["dashboard"], "name": renamed_dashboard_name},
            )
            rename_body = assert_ok(rename_response)
            rename_data = data_dict(rename_body)
            assert rename_data["name"] == renamed_dashboard_name
            print(f"Step 10: Rename - OK (id={ids['dashboard']})")

            # === Step 11: Find Recent ===
            recent_response = await api_client.post(
                "/de2api/dataVisualization/findRecent",
                headers=headers,
                json={"size": 10},
            )
            recent_body = assert_ok(recent_response)
            recent_data = data_list(recent_body)
            assert any(str(item.get("id")) == str(ids["dashboard"]) for item in recent_data)
            print(f"Step 11: Find Recent - OK (id={ids['dashboard']})")

            # === Step 12: Check Canvas Change ===
            canvas_change_response = await api_client.post(
                "/de2api/dataVisualization/checkCanvasChange",
                headers=headers,
                json={"id": ids["dashboard"], "contentId": ids["content_id"], "checkVersion": ids["check_version"]},
            )
            canvas_change_body = assert_ok(canvas_change_response)
            assert canvas_change_body["data"] in {"NoChange", "Repeat"}
            print(f"Step 12: Check Canvas Change - OK (id={ids['dashboard']})")

            # === Step 13: Update Publish Status ===
            publish_response = await api_client.post(
                "/de2api/dataVisualization/updatePublishStatus",
                headers=headers,
                json={"id": ids["dashboard"], "status": 2, "activeViewIds": []},
            )
            publish_body = assert_ok(publish_response)
            publish_data = data_dict(publish_body)
            assert str(publish_data["id"]) == str(ids["dashboard"])
            assert publish_data["status"] == 2
            print(f"Step 13: Update Publish Status - OK (id={ids['dashboard']})")

            # === Step 14: View Detail List ===
            view_detail_response = await api_client.get(
                f"/de2api/dataVisualization/viewDetailList/{ids['dashboard']}",
                headers=headers,
            )
            view_detail_body = assert_ok(view_detail_response)
            assert isinstance(view_detail_body["data"], list)
            assert len(cast(list[Any], view_detail_body["data"])) >= 3
            print(f"Step 14: View Detail List - OK (id={ids['dashboard']})")

            # === Step 15: Find Copy Resource ===
            copy_resource_response = await api_client.get(
                f"/de2api/dataVisualization/findCopyResource/{ids['dashboard']}/dashboard",
                headers=headers,
            )
            copy_resource_body = assert_ok(copy_resource_response)
            copy_resource_data = data_dict(copy_resource_body)
            assert str(copy_resource_data["id"]) == str(ids["dashboard"])
            print(f"Step 15: Find Copy Resource - OK (id={ids['dashboard']})")

            # === Step 16: Find DV Type ===
            dv_type_response = await api_client.get(
                f"/de2api/dataVisualization/findDvType/{ids['dashboard']}",
                headers=headers,
            )
            dv_type_body = assert_ok(dv_type_response)
            assert dv_type_body["data"] == "dashboard"
            print(f"Step 16: Find DV Type - OK (id={ids['dashboard']})")

            # === Step 17: Update Check Version ===
            version_response = await api_client.get(
                f"/de2api/dataVisualization/updateCheckVersion/{ids['dashboard']}",
                headers=headers,
            )
            version_body = assert_ok(version_response)
            assert version_body["data"] == ""
            print(f"Step 17: Update Check Version - OK (id={ids['dashboard']})")

            # === Step 18: Favorites/Store ===
            add_store_response = await api_client.post(
                f"/de2api/store/{ids['dashboard']}",
                headers=headers,
                json={"resourceType": 0},
            )
            add_store_body = assert_ok(add_store_response)
            assert add_store_body["data"] is not None
            favorited_response = await api_client.post(
                "/de2api/store/favorited",
                headers=headers,
                json={"resourceId": ids["dashboard"], "resourceType": 0},
            )
            favorited_body = assert_ok(favorited_response)
            favorited_data = data_dict(favorited_body)
            assert str(favorited_data["resourceId"]) == str(ids["dashboard"])
            assert favorited_data["favorited"] is True
            remove_store_response = await api_client.post(
                f"/de2api/store/del/{ids['dashboard']}",
                headers=headers,
                json={"resourceType": 0},
            )
            remove_store_body = assert_ok(remove_store_response)
            assert remove_store_body["data"] is not None
            print(f"Step 18: Favorites/Store - OK (id={ids['dashboard']})")

            # === Step 19: Watermark ===
            save_watermark_response = await api_client.post(
                "/de2api/watermark/save",
                headers=headers,
                json={"settingContent": watermark_content},
            )
            assert_ok(save_watermark_response)  # save returns data=None on success
            find_watermark_response = await api_client.get("/de2api/watermark/find", headers=headers)
            find_watermark_body = assert_ok(find_watermark_response)
            find_watermark_data = data_dict(find_watermark_body)
            assert "settingContent" in find_watermark_data
            print("Step 19: Watermark - OK")

            # === Step 20: Subject/Theme ===
            subject_response = await api_client.post("/de2api/visualizationSubject/query", headers=headers)
            subject_body = assert_ok(subject_response)
            _ = data_list(subject_body)
            print("Step 20: Subject/Theme - OK")

            # === Step 21: Background ===
            background_response = await api_client.get("/de2api/visualizationBackground/findAll", headers=headers)
            background_body = assert_ok(background_response)
            assert isinstance(background_body["data"], (list, dict))
            print("Step 21: Background - OK")

            # === Step 22: Share ===
            share_save_response = await api_client.post(
                "/de2api/share/save",
                headers=headers,
                json={"resourceId": ids["dashboard"], "type": 0},
            )
            share_save_body = assert_ok(share_save_response)
            share_data = data_dict(share_save_body)
            ids["share_uuid"] = str(share_data["uuid"])
            assert str(share_data["resourceId"]) == str(ids["dashboard"])
            share_detail_response = await api_client.post(
                "/de2api/share/detail",
                headers=headers,
                json={"resourceId": ids["dashboard"]},
            )
            share_detail_body = assert_ok(share_detail_response)
            share_detail_data = data_dict(share_detail_body)
            assert str(share_detail_data["resourceId"]) == str(ids["dashboard"])
            share_proxy_response = await api_client.post(
                "/de2api/share/proxyInfo",
                json={"uuid": ids["share_uuid"], "inIframe": False},
            )
            share_proxy_body = assert_ok(share_proxy_response)
            share_proxy_data = data_dict(share_proxy_body)
            assert share_proxy_data["uuid"] == ids["share_uuid"]
            enable_ticket_response = await api_client.post(
                "/de2api/share/enableTicket",
                headers=headers,
                json={"resourceId": str(ids["dashboard"]), "require": True},
            )
            assert enable_ticket_response.status_code == 200, enable_ticket_response.text
            ticket_limit_response = await api_client.get("/de2api/share/ticketLimit", headers=headers)
            ticket_limit_body = assert_ok(ticket_limit_response)
            assert ticket_limit_body["data"] == 0
            print(f"Step 22: Share - OK (id={ids['dashboard']})")

            # === Step 23: Linkage ===
            linkage_response = await api_client.post(
                "/de2api/linkage/getViewLinkageGather",
                headers=headers,
                json={"dvId": ids["dashboard"], "viewId": 0},
            )
            linkage_body = assert_ok(linkage_response)
            assert isinstance(linkage_body["data"], (list, dict))
            print(f"Step 23: Linkage - OK (id={ids['dashboard']})")

            # === Step 24: Link Jump ===
            jump_response = await api_client.get(
                f"/de2api/linkJump/queryVisualizationJumpInfo/{ids['dashboard']}/core",
                headers=headers,
            )
            assert jump_response.status_code == 200, f"Link Jump failed: {jump_response.status_code}"
            jump_body = jump_response.json()
            assert isinstance(jump_body["data"], (list, dict, type(None)))
            print(f"Step 24: Link Jump - OK (id={ids['dashboard']})")

            # === Step 25: Outer Params ===
            outer_params_response = await api_client.get(
                f"/de2api/outerParams/queryWithVisualizationId/{ids['dashboard']}",
                headers=headers,
            )
            assert outer_params_response.status_code == 200, f"Outer Params failed: {outer_params_response.status_code}"
            outer_params_body = outer_params_response.json()
            assert outer_params_body["data"] is None or isinstance(outer_params_body["data"], (list, dict))
            print(f"Step 25: Outer Params - OK (id={ids['dashboard']})")

            # === Step 26: Export ===
            export_response = await api_client.post("/de2api/exportCenter/exportTasks/1", headers=headers)
            export_body = assert_ok(export_response)
            assert isinstance(export_body["data"], list)
            print("Step 26: Export - OK")

            # === Step 27: Template ===
            template_response = await api_client.post("/de2api/templateManage/tree", headers=headers)
            template_body = assert_ok(template_response)
            assert isinstance(template_body["data"], list)
            print("Step 27: Template - OK")

            # === Step 28: Delete Logic ===
            delete_logic_response = await api_client.post(
                f"/de2api/dataVisualization/deleteLogic/{ids['dashboard']}/dashboard",
                headers=headers,
            )
            delete_logic_body = assert_ok(delete_logic_response)
            _ = data_dict(delete_logic_body)
            print(f"Step 28: Delete Logic - OK (id={ids['dashboard']})")
        finally:
            # === Step 29: Cleanup ===
            if headers and ids.get("share_uuid"):
                await api_client.post(
                    "/de2api/share/delete",
                    headers=headers,
                    json={"resourceId": ids["dashboard"]},
                )
            if headers and ids.get("dashboard"):
                await api_client.post(
                    "/de2api/dataVisualization/delete",
                    headers=headers,
                    json={"id": ids["dashboard"]},
                )
            if headers and ids.get("folder"):
                await api_client.post(
                    "/de2api/dataVisualization/delete",
                    headers=headers,
                    json={"id": ids["folder"]},
                )
            print(
                f"Step 29: Cleanup - OK (dashboard={ids.get('dashboard')}, folder={ids.get('folder')}, share={ids.get('share_uuid')})"
            )
