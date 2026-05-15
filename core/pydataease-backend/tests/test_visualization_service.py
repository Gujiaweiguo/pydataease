from __future__ import annotations

import json

from app.models.visualization import DataVisualizationInfo
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
