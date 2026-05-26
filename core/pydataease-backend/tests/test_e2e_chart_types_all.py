"""E2E tests for ALL chart types — creation, getData, canvas persistence."""
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

CHART_TYPES: list[dict[str, str]] = [
    {"value": "gauge", "render": "antv", "category": "quota"},
    {"value": "liquid", "render": "antv", "category": "quota"},
    {"value": "indicator", "render": "custom", "category": "quota"},
    {"value": "table-info", "render": "antv", "category": "table"},
    {"value": "table-normal", "render": "antv", "category": "table"},
    {"value": "table-pivot", "render": "antv", "category": "table"},
    {"value": "t-heatmap", "render": "antv", "category": "table"},
    {"value": "line", "render": "antv", "category": "trend"},
    {"value": "area", "render": "antv", "category": "trend"},
    {"value": "area-stack", "render": "antv", "category": "trend"},
    {"value": "bar", "render": "antv", "category": "compare"},
    {"value": "bar-stack", "render": "antv", "category": "compare"},
    {"value": "percentage-bar-stack", "render": "antv", "category": "compare"},
    {"value": "bar-group", "render": "antv", "category": "compare"},
    {"value": "bar-group-stack", "render": "antv", "category": "compare"},
    {"value": "waterfall", "render": "antv", "category": "compare"},
    {"value": "bar-horizontal", "render": "antv", "category": "compare"},
    {"value": "bar-stack-horizontal", "render": "antv", "category": "compare"},
    {"value": "percentage-bar-stack-horizontal", "render": "antv", "category": "compare"},
    {"value": "bar-range", "render": "antv", "category": "compare"},
    {"value": "bidirectional-bar", "render": "antv", "category": "compare"},
    {"value": "progress-bar", "render": "antv", "category": "compare"},
    {"value": "stock-line", "render": "antv", "category": "trend"},
    {"value": "bullet-graph", "render": "antv", "category": "compare"},
    {"value": "pie", "render": "antv", "category": "distribute"},
    {"value": "pie-donut", "render": "antv", "category": "distribute"},
    {"value": "pie-rose", "render": "antv", "category": "distribute"},
    {"value": "pie-donut-rose", "render": "antv", "category": "distribute"},
    {"value": "radar", "render": "antv", "category": "distribute"},
    {"value": "treemap", "render": "antv", "category": "distribute"},
    {"value": "word-cloud", "render": "antv", "category": "distribute"},
    {"value": "map", "render": "antv", "category": "map"},
    {"value": "bubble-map", "render": "antv", "category": "map"},
    {"value": "flow-map", "render": "antv", "category": "map"},
    {"value": "heat-map", "render": "antv", "category": "map"},
    {"value": "symbolic-map", "render": "antv", "category": "map"},
    {"value": "scatter", "render": "antv", "category": "relation"},
    {"value": "quadrant", "render": "antv", "category": "relation"},
    {"value": "funnel", "render": "antv", "category": "relation"},
    {"value": "sankey", "render": "antv", "category": "relation"},
    {"value": "circle-packing", "render": "antv", "category": "relation"},
    {"value": "multi-scatter", "render": "antv", "category": "relation"},
    {"value": "chart-mix", "render": "antv", "category": "dual_axes"},
    {"value": "chart-mix-group", "render": "antv", "category": "dual_axes"},
    {"value": "chart-mix-stack", "render": "antv", "category": "dual_axes"},
    {"value": "chart-mix-dual-line", "render": "antv", "category": "dual_axes"},
    {"value": "rich-text", "render": "custom", "category": "other"},
    {"value": "picture-group", "render": "custom", "category": "other"},
]


@E2E_GATE
@pytest.mark.asyncio
async def test_e2e_all_chart_types() -> None:
    ids: dict[str, int] = {}
    headers: dict[str, str] = {}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        try:
            headers = await login(client)
            print("Phase 1: Login - OK")
            ds_id, table_name, table_fields = await create_datasource(client, headers)
            ids["datasource"] = ds_id
            dataset_id = await create_dataset(client, headers, ds_id, table_name)
            ids["dataset"] = dataset_id
            dashboard_id = await create_dashboard(client, headers)
            ids["dashboard"] = dashboard_id
            print(f"Phase 1: Setup infrastructure - OK (ds={ds_id}, dataset={dataset_id}, dashboard={dashboard_id})")

            text_field = next((f for f in table_fields if f.get("deType") == 0), table_fields[0])
            num_field = next((f for f in table_fields if f.get("deType") in (2, 3)), table_fields[0])

            def make_field(field: dict[str, Any], summary: str = "none") -> dict[str, Any]:
                return {
                    "id": field["name"],
                    "name": field["name"],
                    "dataeaseName": field["name"],
                    "summary": summary,
                    "groupType": "d" if field.get("deType") == 0 else "q",
                    "deType": field.get("deType", 0),
                    "extField": 0,
                    "sort": "none",
                }

            dim_field = make_field(text_field)
            metric_field = make_field(num_field, "sum")

            chart_ids: dict[str, int] = {}
            component_data: list[dict[str, Any]] = []
            canvas_view_info: dict[str, dict[str, Any]] = {}
            success_count = 0
            fail_details: list[str] = []

            for index, ct in enumerate(CHART_TYPES):
                chart_type = ct["value"]
                render = ct["render"]
                category = ct["category"]
                chart_id = ns_id()
                while chart_id in chart_ids.values():
                    chart_id = ns_id()

                try:
                    if category == "quota":
                        x_axis: list[dict[str, Any]] = []
                        y_axis = [metric_field]
                    elif category == "table":
                        x_axis = [dim_field]
                        y_axis = []
                    elif category == "map":
                        x_axis = [dim_field]
                        y_axis = [metric_field]
                    elif category == "other":
                        x_axis = []
                        y_axis = []
                    else:
                        x_axis = [dim_field]
                        y_axis = [metric_field]

                    view_info = {
                        "id": str(chart_id),
                        "title": f"E2E {chart_type}",
                        "type": chart_type,
                        "render": render,
                        "tableId": str(dataset_id),
                        "resultCount": "1000",
                        "resultMode": "custom",
                        "xAxis": x_axis,
                        "xAxisExt": [],
                        "yAxis": y_axis,
                        "yAxisExt": [],
                        "extStack": [],
                        "extBubble": [],
                        "extLabel": [],
                        "extTooltip": [],
                        "customAttr": {"basicStyle": {"alpha": 100}},
                        "customStyle": {},
                        "customFilter": {},
                        "drillFields": [],
                        "senior": {},
                        "viewFields": [],
                    }

                    comp: dict[str, Any] = {
                        "id": f"chart-{chart_id}",
                        "component": "UserView",
                        "innerType": chart_type,
                        "datasetId": str(dataset_id),
                        "viewId": str(chart_id),
                        "label": f"E2E {chart_type}",
                        "name": f"E2E {chart_type}",
                        "canvasId": "canvas-main",
                        "rect": {"x": 16, "y": index * 8, "w": 12, "h": 8},
                    }
                    if chart_type == "rich-text":
                        comp["propValue"] = {"textValue": f"<p>E2E rich-text for {chart_type}</p>"}

                    component_data.append(comp)
                    canvas_view_info[str(chart_id)] = view_info
                    chart_ids[chart_type] = chart_id
                    success_count += 1
                except Exception as exc:  # pragma: no cover - defensive for live e2e diagnostics
                    fail_details.append(f"{chart_type}: build error - {exc}")

            print(f"Phase 2: Built {success_count}/{len(CHART_TYPES)} chart component entries")
            assert not fail_details, fail_details

            save_resp = await client.post(
                "/de2api/dataVisualization/saveCanvas",
                headers=headers,
                json={
                    "id": dashboard_id,
                    "name": "E2E All Chart Types Dashboard",
                    "pid": 0,
                    "type": "dashboard",
                    "componentData": json.dumps(component_data),
                    "canvasStyleData": json.dumps({"width": 1920, "height": 10800}),
                    "canvasViewInfo": canvas_view_info,
                    "mobileLayout": False,
                },
            )
            assert_ok(save_resp)
            print(f"Phase 3: Save canvas - OK ({len(component_data)} components)")

            find_resp = await client.post(
                "/de2api/dataVisualization/findById",
                headers=headers,
                json={"id": dashboard_id, "busiFlag": "dashboard"},
            )
            find_data = data_dict(assert_ok(find_resp))
            saved_components = json.loads(find_data["componentData"])
            saved_view_info = find_data["canvasViewInfo"]
            assert isinstance(saved_view_info, dict)

            verify_pass = 0
            verify_fail: list[str] = []
            for ct in CHART_TYPES:
                chart_type = ct["value"]
                chart_id = chart_ids[chart_type]
                comp_or_none = find_component_by_id(saved_components, f"chart-{chart_id}")
                if comp_or_none is None:
                    verify_fail.append(f"{chart_type}: component not found in saved data")
                    continue
                comp = comp_or_none
                assert comp["component"] == "UserView"
                assert comp["innerType"] == chart_type

                cid = str(chart_id)
                assert cid in saved_view_info, f"{chart_type}: chart {cid} not in canvasViewInfo"
                assert saved_view_info[cid]["type"] == chart_type
                verify_pass += 1

            print(f"Phase 4: Verified {verify_pass}/{len(CHART_TYPES)} chart types in saved dashboard")
            assert verify_pass == len(CHART_TYPES), f"Failed charts: {verify_fail}"

            map_types = {"map", "bubble-map", "flow-map", "heat-map", "symbolic-map"}
            no_data_types = {"rich-text", "picture-group"}
            data_pass = 0
            data_fail: list[str] = []

            for ct in CHART_TYPES:
                chart_type = ct["value"]
                if chart_type in map_types or chart_type in no_data_types:
                    continue

                cid = chart_ids[chart_type]
                try:
                    chart_data_resp = await client.post(
                        "/de2api/chart/getData",
                        headers=headers,
                        json={
                            "id": cid,
                            "tableId": dataset_id,
                            "xAxis": canvas_view_info[str(cid)]["xAxis"],
                            "yAxis": canvas_view_info[str(cid)]["yAxis"],
                        },
                    )
                    if chart_data_resp.status_code == 200:
                        body = chart_data_resp.json()
                        if body.get("code") == 0:
                            data_pass += 1
                        else:
                            data_fail.append(f"{chart_type}: getData returned code={body.get('code')}")
                    else:
                        data_fail.append(f"{chart_type}: getData HTTP {chart_data_resp.status_code}")
                except Exception as exc:  # pragma: no cover - defensive for live e2e diagnostics
                    data_fail.append(f"{chart_type}: getData exception - {exc}")

            non_exempt_count = len(CHART_TYPES) - len(map_types) - len(no_data_types)
            print(f"Phase 5: getData {data_pass} passed, {len(data_fail)} issues out of {non_exempt_count}")
            if data_fail:
                print(f"Phase 5 issues: {data_fail[:10]}")

            min_expected = non_exempt_count // 2
            assert data_pass >= min_expected, (
                f"Too many getData failures: {data_pass} passed, need >= {min_expected}. Issues: {data_fail}"
            )
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
