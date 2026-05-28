from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.visualization import DataVisualizationInfo
from app.schemas.auth import TokenUser
from app.schemas.visualization import StoreExecuteRequest, StoreResponse, VisualizationTreeRequest
from app.services.visualization_service import VisualizationService, _enrich_component_data


def _visualization(component_data: object) -> DataVisualizationInfo:
    return DataVisualizationInfo(
        id=1,
        name="dashboard",
        pid=None,
        node_type="leaf",
        type="dashboard",
        component_data=component_data,
        canvas_style_data={"width": 100},
    )


def test_serialize_visualization_keeps_component_array() -> None:
    payload = VisualizationService._serialize_visualization(_visualization([{"id": "c1"}]))

    component_data = payload["componentData"]
    assert isinstance(component_data, str)
    assert json.loads(component_data) == [{"id": "c1"}]


def test_serialize_visualization_normalizes_component_dict_to_empty_array() -> None:
    payload = VisualizationService._serialize_visualization(_visualization({"_activeViewIds": [1]}))

    component_data = payload["componentData"]
    assert component_data == "[]"


def test_build_chart_payload_normalizes_numeric_string_fields() -> None:
    service = VisualizationService(cast(AsyncSession, cast(Any, SimpleNamespace())))

    payload = service._build_chart_payload(
        {
            "id": "1001",
            "title": "指标卡",
            "type": "indicator",
            "tableId": "1779526006431860713",
            "resultCount": "1000",
            "copyId": "1779526006438529243",
        },
        1001,
        2001,
        "7",
        3001,
        None,
    )

    assert payload["table_id"] == 1779526006431860713
    assert payload["result_count"] == 1000
    assert payload["copy_id"] == 1779526006438529243


def test_build_chart_payload_rejects_invalid_numeric_string_fields() -> None:
    service = VisualizationService(cast(AsyncSession, cast(Any, SimpleNamespace())))

    with pytest.raises(HTTPException) as exc_info:
        service._build_chart_payload(
            {
                "id": "1001",
                "title": "指标卡",
                "type": "indicator",
                "tableId": "not-a-number",
            },
            1001,
            2001,
            "7",
            3001,
            None,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid integer value for chart field 'table_id'"


def test_enrich_component_data_adds_userview_defaults_for_dashboard() -> None:
    enriched = _enrich_component_data(
        [{"id": "chart-1", "component": "UserView", "innerType": "bar", "style": {"width": 500}}],
        "dashboard",
    )

    assert isinstance(enriched, list)
    component = enriched[0]
    assert component["events"]["type"] == "jump"
    assert component["commonBackground"]["backgroundColor"] == "rgba(255,255,255,1)"
    assert component["style"]["width"] == 500
    assert component["style"]["height"] == 300
    assert component["canvasId"] == "canvas-main"


def test_enrich_component_data_handles_nested_tabs_and_groups() -> None:
    enriched = _enrich_component_data(
        [
            {
                "id": "tabs-1",
                "component": "DeTabs",
                "propValue": [
                    {
                        "name": "tab-a",
                        "componentData": [
                            {"id": "chart-2", "component": "UserView", "innerType": "bar"}
                        ],
                    }
                ],
            },
            {
                "id": "group-1",
                "component": "Group",
                "propValue": [{"id": "chart-3", "component": "UserView", "innerType": "line"}],
            },
        ],
        "panel",
    )

    assert isinstance(enriched, list)
    tab_chart = enriched[0]["propValue"][0]["componentData"][0]
    group_chart = enriched[1]["propValue"][0]
    assert tab_chart["canvasId"] == "tabs-1--tab-a"
    assert group_chart["canvasId"] == "group-1"
    assert tab_chart["commonBackground"]["backgroundColor"] == "rgba(19,28,66,1)"


def test_duplicate_canvas_view_info_and_replace_nested_ids_remap_chart_identifiers() -> None:
    duplicated_view_info, id_map = VisualizationService._duplicate_canvas_view_info(
        {
            "101": {"id": 101, "title": "Sales"},
            "202": {"id": 202, "title": "Profit"},
        }
    )

    assert sorted(duplicated_view_info.keys()) != ["101", "202"]
    assert id_map["101"] != 101
    remapped = cast(
        list[dict[str, object]],
        VisualizationService._replace_nested_ids(
            [{"id": "101", "viewId": 202}, {"children": [{"id": 101}]}],
            id_map,
        ),
    )
    assert remapped[0]["id"] == id_map["101"]
    assert remapped[0]["viewId"] == id_map[202]
    assert cast(list[dict[str, object]], remapped[1]["children"])[0]["id"] == id_map[101]


async def test_execute_store_toggles_between_add_and_remove() -> None:
    service = VisualizationService(cast(AsyncSession, cast(Any, SimpleNamespace())))
    user = TokenUser(user_id=7, oid=9)
    service.store_repo.get_by_resource = AsyncMock(side_effect=[None, SimpleNamespace(id=1)])  # type: ignore[attr-defined]
    service.add_store = AsyncMock(return_value=StoreResponse(resource_id=10, favorited=True))  # type: ignore[method-assign]
    service.remove_store = AsyncMock(return_value=StoreResponse(resource_id=10, favorited=False))  # type: ignore[method-assign]

    added = await service.execute_store(StoreExecuteRequest(resource_id=10, type="panel"), user)
    removed = await service.execute_store(StoreExecuteRequest(resource_id=10, type="panel"), user)

    assert added.favorited is True
    assert removed.favorited is False
    service.add_store.assert_awaited_once_with(10, 1, user)  # type: ignore[attr-defined]
    service.remove_store.assert_awaited_once_with(10, 1, user)  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_tree_returns_empty_root_when_no_visualizations_exist() -> None:
    service = VisualizationService(cast(AsyncSession, cast(Any, SimpleNamespace())))
    service.visualization_repo.list_all_ordered = AsyncMock(return_value=[])  # type: ignore[attr-defined]

    tree = await service.tree(VisualizationTreeRequest(busi_flag="dataV"))

    assert tree == [{
        "id": "0",
        "name": "root",
        "pid": -1,
        "leaf": False,
        "weight": 7,
        "extraFlag": 0,
        "extraFlag1": 1,
        "children": [],
    }]


def test_enrich_component_data_screen_type_uses_dark_background() -> None:
    enriched = _enrich_component_data(
        [{"id": "sc-1", "component": "UserView", "innerType": "bar"}],
        "screen",
    )
    component = enriched[0]
    assert component["commonBackground"]["backgroundColor"] == "rgba(19,28,66,1)"


def test_interactive_tree_key_classifies_screen_aliases() -> None:
    assert VisualizationService._interactive_tree_key("screen") == "dataV"
    assert VisualizationService._interactive_tree_key("datav") == "dataV"
    assert VisualizationService._interactive_tree_key("datav-copy") == "dataV"
    assert VisualizationService._interactive_tree_key("dashboard") == "dashboard"
    assert VisualizationService._interactive_tree_key("panel") == "dashboard"
    assert VisualizationService._interactive_tree_key("unknown") is None


def test_normalize_store_resource_type_screen() -> None:
    assert VisualizationService._normalize_store_resource_type(None, "datav") == 2
    assert VisualizationService._normalize_store_resource_type(None, "screen") == 2
    assert VisualizationService._normalize_store_resource_type(None, "dashboard") == 1
