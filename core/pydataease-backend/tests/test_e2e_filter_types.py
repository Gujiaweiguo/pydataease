"""E2E tests for all VQuery filter display types."""
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

FILTER_DISPLAY_TYPES = [
    {"displayType": "0", "name": "下拉选择"},
    {"displayType": "1", "name": "日期"},
    {"displayType": "7", "name": "日期范围"},
    {"displayType": "8", "name": "文本搜索"},
    {"displayType": "9", "name": "树选择"},
    {"displayType": "22", "name": "数值"},
]


@E2E_GATE
@pytest.mark.asyncio
async def test_e2e_all_filter_types() -> None:
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
            number_field = next((f for f in table_fields if f.get("deType") in (2, 3)), table_fields[0])
            filter_components: list[dict[str, Any]] = []
            component_ids: dict[str, str] = {}

            for idx, filter_item in enumerate(FILTER_DISPLAY_TYPES):
                display_type = filter_item["displayType"]
                filter_name = filter_item["name"]
                base_field = number_field if display_type in {"1", "7", "22"} else text_field
                field_id = str(base_field["name"])
                filter_type = "logic" if display_type in {"1", "7", "22"} else "enum"
                component_id = f"filter-{display_type}-{ns_id()}"
                component_ids[display_type] = component_id
                filter_components.append(
                    {
                        "id": component_id,
                        "component": "VQuery",
                        "innerType": "VQuery",
                        "canvasId": "canvas-main",
                        "propValue": [
                            {
                                "id": f"filter-item-{ns_id()}",
                                "displayType": display_type,
                                "fieldId": field_id,
                                "datasetId": str(dataset_id),
                                "filterType": filter_type,
                                "name": filter_name,
                                "required": False,
                                "visible": True,
                                "defaultMapValue": [],
                                "defaultValueCheck": False,
                                "optionValueSource": 0,
                                "multiple": False,
                                "displayId": field_id,
                                "sort": "none",
                                "sortNum": 0,
                            }
                        ],
                        "rect": {"x": 2, "y": idx * 4, "w": 12, "h": 3},
                    }
                )

            save_resp = await client.post(
                "/de2api/dataVisualization/saveCanvas",
                headers=headers,
                json={
                    "id": dashboard_id,
                    "name": "E2E Filter Types Dashboard",
                    "pid": 0,
                    "type": "dashboard",
                    "componentData": json.dumps(filter_components),
                    "canvasStyleData": json.dumps({"width": 1920, "height": 1200}),
                    "canvasViewInfo": {},
                    "mobileLayout": False,
                },
            )
            assert_ok(save_resp)
            print("Phase 2: saveCanvas - OK")

            find_resp = await client.post(
                "/de2api/dataVisualization/findById",
                headers=headers,
                json={"id": dashboard_id, "busiFlag": "dashboard"},
            )
            find_data = data_dict(assert_ok(find_resp))
            saved_components = json.loads(find_data["componentData"])

            for filter_item in FILTER_DISPLAY_TYPES:
                display_type = filter_item["displayType"]
                component_id = component_ids[display_type]
                saved = find_component_by_id(saved_components, component_id)
                assert saved is not None, f"missing filter component {component_id}"
                assert saved["component"] == "VQuery"
                prop_value = saved["propValue"]
                assert isinstance(prop_value, list) and len(prop_value) == 1
                assert prop_value[0]["displayType"] == display_type
                assert prop_value[0]["name"] == filter_item["name"]

            print(f"Phase 3: Verified {len(FILTER_DISPLAY_TYPES)} filter display types - OK")
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
