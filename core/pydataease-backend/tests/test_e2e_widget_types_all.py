"""E2E tests for all non-chart widget types on mixed dashboards."""
from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from tests.fixtures.e2e_helpers import (  # pyright: ignore[reportImplicitRelativeImport]
    BASE_URL,
    E2E_GATE,
    assert_ok,
    create_dashboard,
    create_datasource,
    create_dataset,
    data_dict,
    find_component_by_id,
    login,
    ns_id,
)

WIDGET_TYPES: list[dict[str, Any]] = [
    {"component": "VText", "innerType": "VText", "propValue": "E2E Text Label", "label": "文本"},
    {"component": "VQuery", "innerType": "VQuery", "propValue": [], "label": "查询组件"},
    {"component": "Picture", "innerType": "Picture", "propValue": {"url": "https://example.com/e2e.png"}, "label": "图片"},
    {"component": "DeVideo", "innerType": "DeVideo", "propValue": {"url": "https://example.com/e2e.mp4"}, "label": "视频"},
    {"component": "DeStreamMedia", "innerType": "DeStreamMedia", "streamMediaLinks": {"videoType": "mp4", "mp4": {"url": "https://example.com/e2e-live.mp4", "loop": True, "isLive": False}}, "label": "流媒体"},
    {"component": "DeFrame", "innerType": "DeFrame", "propValue": {"url": "https://example.com"}, "label": "网页"},
    {"component": "DeTimeClock", "innerType": "DeTimeClock", "propValue": {"format": "yyyy-MM-dd HH:mm:ss"}, "label": "时间"},
    {"component": "CanvasIcon", "innerType": "icon-svg", "propValue": {"url": ""}, "label": "图标", "icon": "icon_svg_outlined"},
    {"component": "CanvasBoard", "innerType": "board_1", "propValue": {}, "label": "边框"},
    {"component": "DeDecoration", "innerType": "decoration_1", "propValue": {}, "label": "装饰"},
    {"component": "DynamicBackground", "innerType": "DynamicBackground", "propValue": {}, "label": "动态背景"},
    {"component": "RectShape", "innerType": "RectShape", "propValue": {}, "style": {"backgroundColor": "#1890ff"}, "label": "矩形"},
    {"component": "CircleShape", "innerType": "CircleShape", "propValue": {}, "style": {"backgroundColor": "#52c41a"}, "label": "圆形"},
    {"component": "SvgTriangle", "innerType": "SvgTriangle", "propValue": {}, "style": {"backgroundColor": "#faad14"}, "label": "三角形"},
    {"component": "ScrollText", "innerType": "ScrollText", "propValue": "E2E Scrolling Text", "label": "跑马灯"},
    {"component": "DeTabs", "innerType": "DeTabs", "propValue": [{"name": "tab-a", "title": "Tab A", "componentData": []}], "editableTabsValue": "tab-a", "label": "选项卡"},
    {"component": "Group", "innerType": "Group", "propValue": [], "label": "组合"},
    {"component": "GroupArea", "innerType": "GroupArea", "propValue": {}, "label": "组合区域"},
    {"component": "DeScreen", "innerType": "DeScreen", "propValue": [], "label": "大屏页签"},
    {"component": "PopArea", "innerType": "PopArea", "propValue": {}, "label": "弹窗区域"},
]


def _make_chart_component(component_id: str, chart_type: str, dataset_id: int, chart_id: int, y: int) -> dict[str, Any]:
    component: dict[str, Any] = {
        "id": component_id,
        "component": "UserView",
        "innerType": chart_type,
        "datasetId": str(dataset_id),
        "viewId": str(chart_id),
        "canvasId": "canvas-main",
        "label": f"Mixed {chart_type}",
        "name": f"Mixed {chart_type}",
        "rect": {"x": 30, "y": y, "w": 12, "h": 8},
    }
    if chart_type == "rich-text":
        component["propValue"] = {"textValue": "<p>Mixed rich text widget</p>"}
    return component


@E2E_GATE
@pytest.mark.asyncio
async def test_e2e_all_widget_types() -> None:
    ids: dict[str, int] = {}
    headers: dict[str, str] = {}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        try:
            headers = await login(client)
            print("Phase 1: Login - OK")
            ds_id, table_name, _ = await create_datasource(client, headers)
            ids["datasource"] = ds_id
            dataset_id = await create_dataset(client, headers, ds_id, table_name)
            ids["dataset"] = dataset_id
            dashboard_id = await create_dashboard(client, headers)
            ids["dashboard"] = dashboard_id
            print(f"Phase 1: Setup infrastructure - OK (ds={ds_id}, dataset={dataset_id}, dashboard={dashboard_id})")

            component_data: list[dict[str, Any]] = []
            expected_widget_ids: list[str] = []

            for idx, widget in enumerate(WIDGET_TYPES):
                component_id = f"widget-{idx}-{ns_id()}"
                expected_widget_ids.append(component_id)
                comp: dict[str, Any] = {
                    "id": component_id,
                    "component": widget["component"],
                    "innerType": widget["innerType"],
                    "canvasId": "canvas-main",
                    "label": widget["label"],
                    "name": f"{widget['label']}-{idx}",
                    "rect": {"x": 2 + (idx % 3) * 14, "y": (idx // 3) * 5, "w": 12, "h": 4},
                }
                if "propValue" in widget:
                    comp["propValue"] = widget["propValue"]
                if "streamMediaLinks" in widget:
                    comp["streamMediaLinks"] = widget["streamMediaLinks"]
                if "editableTabsValue" in widget:
                    comp["editableTabsValue"] = widget["editableTabsValue"]
                if "style" in widget:
                    comp["style"] = widget["style"]
                if "icon" in widget:
                    comp["icon"] = widget["icon"]
                component_data.append(comp)

            chart_types = ["indicator", "bar", "line", "rich-text"]
            chart_ids: dict[str, int] = {}
            canvas_view_info: dict[str, dict[str, Any]] = {}
            for idx, chart_type in enumerate(chart_types):
                chart_id = ns_id()
                chart_ids[chart_type] = chart_id
                component_data.append(
                    _make_chart_component(f"mixed-chart-{chart_type}", chart_type, dataset_id, chart_id, 40 + idx * 8)
                )
                canvas_view_info[str(chart_id)] = {
                    "id": str(chart_id),
                    "title": f"Mixed {chart_type}",
                    "type": chart_type,
                    "render": "custom" if chart_type in {"indicator", "rich-text"} else "antv",
                    "tableId": str(dataset_id),
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
                }

            save_resp = await client.post(
                "/de2api/dataVisualization/saveCanvas",
                headers=headers,
                json={
                    "id": dashboard_id,
                    "name": "E2E All Widget Types Dashboard",
                    "pid": 0,
                    "type": "dashboard",
                    "componentData": json.dumps(component_data),
                    "canvasStyleData": json.dumps({"width": 1920, "height": 2400}),
                    "canvasViewInfo": canvas_view_info,
                    "mobileLayout": False,
                },
            )
            save_body = data_dict(assert_ok(save_resp))
            content_id = str(save_body.get("contentId") or "")
            check_version = str(save_body.get("checkVersion") or "")
            print(f"Phase 2: saveCanvas - OK ({len(component_data)} components)")

            find_resp = await client.post(
                "/de2api/dataVisualization/findById",
                headers=headers,
                json={"id": dashboard_id, "busiFlag": "dashboard"},
            )
            find_data = data_dict(assert_ok(find_resp))
            saved_components = json.loads(find_data["componentData"])
            for component_id in expected_widget_ids:
                saved = find_component_by_id(saved_components, component_id)
                assert saved is not None, f"missing widget {component_id}"
            for chart_type in chart_types:
                assert find_component_by_id(saved_components, f"mixed-chart-{chart_type}") is not None
            print("Phase 3: Initial persistence verification - OK")

            updated_components = [
                comp for comp in component_data if comp["component"] not in {"DynamicBackground", "GroupArea"}
            ]
            updated_text = next(comp for comp in updated_components if comp["component"] == "VText")
            updated_text["propValue"] = "E2E Text Label Updated"
            updated_picture = next(comp for comp in updated_components if comp["component"] == "Picture")
            updated_picture["propValue"] = {"url": "https://example.com/e2e-updated.png"}
            updated_tabs = next(comp for comp in updated_components if comp["component"] == "DeTabs")
            updated_tabs["propValue"] = [
                {"name": "tab-a", "title": "Tab A", "componentData": []},
                {"name": "tab-b", "title": "Tab B", "componentData": []},
            ]
            new_widget_id = f"widget-added-{ns_id()}"
            updated_components.append(
                {
                    "id": new_widget_id,
                    "component": "VText",
                    "innerType": "VText",
                    "canvasId": "canvas-main",
                    "label": "新增文本",
                    "name": "新增文本",
                    "propValue": "E2E Added Widget",
                    "rect": {"x": 2, "y": 72, "w": 12, "h": 4},
                }
            )

            update_resp = await client.post(
                "/de2api/dataVisualization/updateCanvas",
                headers=headers,
                json={
                    "id": dashboard_id,
                    "name": "E2E All Widget Types Dashboard",
                    "pid": 0,
                    "type": "dashboard",
                    "componentData": json.dumps(updated_components),
                    "canvasStyleData": json.dumps({"width": 1920, "height": 2600, "backgroundColor": "#ffffff"}),
                    "canvasViewInfo": canvas_view_info,
                    "contentId": content_id,
                    "checkVersion": check_version,
                    "mobileLayout": False,
                },
            )
            update_body = data_dict(assert_ok(update_resp))
            assert update_body["status"] == 2
            print("Phase 4: updateCanvas - OK")

            verify_resp = await client.post(
                "/de2api/dataVisualization/findById",
                headers=headers,
                json={"id": dashboard_id, "busiFlag": "dashboard"},
            )
            verify_data = data_dict(assert_ok(verify_resp))
            verify_components = json.loads(verify_data["componentData"])
            assert find_component_by_id(verify_components, expected_widget_ids[10]) is None
            assert find_component_by_id(verify_components, expected_widget_ids[17]) is None
            added = find_component_by_id(verify_components, new_widget_id)
            assert added is not None
            assert added["propValue"] == "E2E Added Widget"
            text_saved = find_component_by_id(verify_components, expected_widget_ids[0])
            assert text_saved is not None
            assert text_saved["propValue"] == "E2E Text Label Updated"
            picture_saved = find_component_by_id(verify_components, expected_widget_ids[2])
            assert picture_saved is not None
            assert picture_saved["propValue"]["url"] == "https://example.com/e2e-updated.png"
            tabs_saved = find_component_by_id(verify_components, expected_widget_ids[15])
            assert tabs_saved is not None
            assert len(tabs_saved["propValue"]) == 2
            print("Phase 5: Updated persistence verification - OK")
        finally:
            if headers:
                if ids.get("dashboard"):
                    await client.post(
                        "/de2api/dataVisualization/delete",
                        headers=headers,
                        json={"id": ids["dashboard"]},
                    )
                if ids.get("dataset"):
                    await client.post(f"/de2api/datasetTree/delete/{ids['dataset']}", headers=headers)
                if ids.get("datasource"):
                    await client.post(f"/de2api/datasource/delete/{ids['datasource']}", headers=headers)
