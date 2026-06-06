from __future__ import annotations

from copy import deepcopy
import json as _json
import time
from typing import Any, cast, final

from fastapi import Depends, HTTPException, status
from sqlalchemy import BigInteger, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.chart import CoreChartView
from app.models.visualization import DataVisualizationInfo
from app.repositories.chart_repo import ChartRepository
from app.repositories.store_repo import StoreRepository
from app.repositories.template_repo import TemplateRepository
from app.repositories.visualization_repo import VisualizationRepository
from app.utils.id_utils import _sid
from app.schemas.auth import TokenUser
from app.schemas.chart import ChartResponse
from app.schemas.visualization import (
    JumpRequest,
    LinkageRequest,
    OuterParamsRequest,
    StoreExecuteRequest,
    StoreResponse,
    VisualizationAppCanvasNameCheckRequest,
    VisualizationCanvasChangeRequest,
    VisualizationCanvasRequest,
    VisualizationCopyRequest,
    VisualizationDeleteLogicRequest,
    VisualizationDecompressionRequest,
    VisualizationFindByIdRequest,
    VisualizationMoveRequest,
    VisualizationNameCheckRequest,
    VisualizationPublishStatusRequest,
    VisualizationRecentRequest,
    VisualizationRenameRequest,
    VisualizationResponse,
    VisualizationSaveRequest,
    VisualizationTreeNodeResponse,
    VisualizationTreeRequest,
    VisualizationUpdateBaseRequest,
    VisualizationUpdateRequest,
)
from app.services.interactive_tree_service import InteractiveTreeService


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _new_identifier() -> int:
    return time.time_ns()


def _compute_level(all_items: list[DataVisualizationInfo], pid: int | None) -> int:
    if pid is None or pid == 0:
        return 0
    id_set = {item.id for item in all_items}
    if pid not in id_set:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Parent id {pid} does not exist")
    id_to_level = {item.id: item.level or 0 for item in all_items}
    return (id_to_level.get(pid, 0) or 0) + 1


def _parse_json_value(value: str | None) -> object | None:
    if value is None:
        return None
    try:
        return _json.loads(value)
    except (TypeError, ValueError):
        return value


def _normalize_int(value: int | str | None) -> int | None:
    """Normalize an int/str/None value. Returns None for 0, empty, or null (root-level pid)."""
    if value in (None, "", "null", 0, "0"):
        return None
    return int(value)


_COMMON_STYLE_DEFAULTS: dict[str, object] = {
    "rotate": 0,
    "opacity": 1,
    "borderActive": False,
    "borderWidth": 1,
    "borderRadius": 5,
    "borderStyle": "solid",
    "borderColor": "#cccccc",
}

_BASE_EVENTS: dict[str, object] = {
    "checked": False,
    "showTips": False,
    "type": "jump",
    "typeList": [
        {"key": "jump", "label": "jump"},
        {"key": "download", "label": "download"},
        {"key": "share", "label": "share"},
        {"key": "fullScreen", "label": "fullScreen"},
        {"key": "showHidden", "label": "showHidden"},
        {"key": "refreshDataV", "label": "refreshDataV"},
        {"key": "refreshView", "label": "refreshView"},
    ],
    "jump": {"value": "https://", "type": "_blank"},
    "download": {"value": True},
    "share": {"value": True},
    "showHidden": {"value": True},
    "refreshDataV": {"value": True},
    "refreshView": {"value": True, "target": "all"},
}

_BASE_CAROUSEL: dict[str, object] = {"enable": False, "time": 10}

_MULTI_DIMENSIONAL: dict[str, object] = {"enable": False, "x": 0, "y": 0, "z": 0}

_COMMON_COMPONENT_BACKGROUND_BASE: dict[str, object] = {
    "backgroundColorSelect": True,
    "backdropFilterEnable": False,
    "backgroundImageEnable": False,
    "backgroundType": "innerImage",
    "innerImage": "board/board_1.svg",
    "outerImage": None,
    "innerPadding": {"mode": "uniform", "top": 12},
    "borderRadius": {"mode": "uniform", "topLeft": 0},
    "backdropFilter": 4,
}

_COMMON_COMPONENT_BACKGROUND_LIGHT: dict[str, object] = {
    **_COMMON_COMPONENT_BACKGROUND_BASE,
    "backgroundColor": "rgba(255,255,255,1)",
    "innerImageColor": "rgba(16, 148, 229,1)",
}

_COMMON_COMPONENT_BACKGROUND_DARK: dict[str, object] = {
    **_COMMON_COMPONENT_BACKGROUND_BASE,
    "backgroundColor": "rgba(19,28,66,1)",
    "innerImageColor": "#1094E5",
}

_ACTION_SELECTION: dict[str, object] = {"linkageActive": "custom"}

_COMMON_ATTR: dict[str, object] = {
    "animations": [],
    "canvasId": "canvas-main",
    "events": _BASE_EVENTS,
    "carousel": _BASE_CAROUSEL,
    "multiDimensional": _MULTI_DIMENSIONAL,
    "groupStyle": {},
    "isLock": False,
    "maintainRadio": False,
    "aspectRatio": 1,
    "isShow": True,
    "dashboardHidden": False,
    "category": "base",
    "dragging": False,
    "resizing": False,
    "collapseName": [
        "position",
        "background",
        "style",
        "picture",
        "frameLinks",
        "videoLinks",
        "streamLinks",
        "carouselInfo",
        "events",
        "decoration_style",
    ],
    "linkage": {
        "duration": 0,
        "data": [{"id": "", "label": "", "event": "", "style": [{"key": "", "value": ""}]}],
    },
}

_DEFAULT_USER_VIEW: dict[str, object] = {
    **_COMMON_ATTR,
    "component": "UserView",
    "name": "view",
    "label": "view",
    "propValue": {"textValue": "", "urlList": []},
    "icon": "bar",
    "innerType": "bar",
    "editing": False,
    "canvasActive": False,
    "actionSelection": _ACTION_SELECTION,
    "x": 1,
    "y": 1,
    "sizeX": 36,
    "sizeY": 14,
    "style": {
        **_COMMON_STYLE_DEFAULTS,
        "adaptation": "adaptation",
        "width": 600,
        "height": 300,
    },
    "matrixStyle": {},
    "commonBackground": _COMMON_COMPONENT_BACKGROUND_LIGHT,
    "state": "ready",
}

_DEFAULT_CANVAS_STYLE_DATA: dict[str, object] = {
    "width": 1920,
    "height": 1080,
    "scale": 60,
    "scaleWidth": 60,
    "scaleHeight": 60,
    "backgroundColorSelect": True,
    "backgroundImageEnable": False,
    "backgroundType": "backgroundColor",
    "background": "",
    "openCommonStyle": True,
    "opacity": 1,
    "fontSize": 14,
    "fontFamily": "PingFang",
    "refreshViewEnable": False,
    "refreshViewLoading": True,
    "refreshUnit": "minute",
    "refreshTime": 5,
    "refreshBrowserEnable": False,
    "refreshBrowserUnit": "minute",
    "refreshBrowserTime": 5,
    "popupAvailable": True,
    "popupButtonAvailable": True,
    "suspensionButtonAvailable": False,
    "screenAdaptor": "widthFirst",
    "dashboardAdaptor": "keepHeightAndWidth",
    "themeId": "10001",
    "color": "#000000",
    "backgroundColor": "#f5f6f7",
    "dashboard": {
        "gap": "yes",
        "gapSize": 5,
        "gapMode": "middle",
        "showGrid": False,
        "matrixBase": 4,
        "resultMode": "all",
        "resultCount": 1000,
        "themeColor": "light",
        "mobileSetting": {
            "customSetting": False,
            "imageUrl": None,
            "backgroundType": "image",
            "color": "#000",
        },
    },
    "component": {
        "seniorStyleSetting": {
            "linkageIconColor": "#a6a6a6",
            "drillLayerColor": "#a6a6a6",
            "pagerColor": "#a6a6a6",
            "pagerSize": 14,
        },
        "formatterItem": {
            "type": "auto",
            "unitLanguage": "en",
            "unit": 1,
            "suffix": "",
            "decimalCount": 2,
            "thousandSeparator": True,
        },
        "chartTitle": {
            "show": True,
            "fontSize": 16,
            "hPosition": "left",
            "vPosition": "top",
            "isItalic": False,
            "isBolder": True,
            "remarkShow": False,
            "remark": "",
            "fontFamily": "",
            "letterSpace": "0",
            "fontShadow": False,
            "color": "#000000",
            "remarkBackgroundColor": "#ffffff",
        },
        "chartColor": {
            "basicStyle": {
                "colorScheme": "default",
                "colors": ["#1E90FF", "#90EE90", "#00CED1", "#E2BD84", "#7A90E0", "#3BA272", "#2BE7FF", "#0A8ADA", "#FFD700"],
                "alpha": 100,
                "gradient": False,
                "mapStyle": "normal",
                "areaBaseColor": "#FFFFFF",
                "areaBorderColor": "#303133",
                "gaugeStyle": "default",
                "tableBorderColor": "#E6E7E4",
                "tableScrollBarColor": "rgba(0, 0, 0, 0.15)",
                "zoomButtonColor": "#aaa",
                "zoomBackground": "#fff",
            },
            "misc": {
                "flowMapConfig": {
                    "lineConfig": {
                        "mapLineAnimate": True,
                        "mapLineGradient": False,
                        "mapLineSourceColor": "#146C94",
                        "mapLineTargetColor": "#576CBC",
                    }
                },
                "nameFontColor": "#000000",
                "valueFontColor": "#5470c6",
            },
            "tableHeader": {
                "tableHeaderBgColor": "#1E90FF",
                "tableHeaderCornerBgColor": "#1E90FF",
                "tableHeaderColBgColor": "#1E90FF",
                "tableHeaderFontColor": "#000000",
                "tableHeaderCornerFontColor": "#000000",
                "tableHeaderColFontColor": "#000000",
            },
            "tableCell": {
                "tableItemBgColor": "#FFFFFF",
                "tableFontColor": "#000000",
                "tableItemSubBgColor": "#1E90FF",
            },
            "label": {"color": "#000000", "fontSize": 12},
            "tooltip": {"color": "#000000", "fontSize": 12, "backgroundColor": "#FFFFFF"},
        },
        "chartCommonStyle": {
            "backgroundColorSelect": True,
            "backdropFilterEnable": False,
            "backgroundImageEnable": False,
            "backgroundType": "innerImage",
            "innerImage": "board/board_1.svg",
            "outerImage": None,
            "innerPadding": {"mode": "Uniform", "top": 12},
            "borderRadius": {"mode": "Uniform", "topLeft": 0},
            "backdropFilter": 4,
            "backgroundColor": "rgba(255,255,255,1)",
            "innerImageColor": "rgba(16, 148, 229,1)",
        },
        "filterStyle": {
            "layout": "horizontal",
            "titleLayout": "left",
            "labelColor": "#1f2329",
            "titleColor": "#1f2329",
            "color": "#1f2329",
            "borderColor": "#bbbfc4",
            "text": "#1f2329",
            "bgColor": "#FFFFFF",
        },
        "tabStyle": {
            "headPosition": "left",
            "headFontColor": "#000000",
            "headFontActiveColor": "#000000",
            "headBorderColor": "#ffffff",
            "headBorderActiveColor": "#ffffff",
        },
    },
}

_DEFAULT_CHART_CUSTOM_ATTR: dict[str, object] = {
    "basicStyle": {
        "alpha": 100,
        "colorScheme": "default",
        "colors": ["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de", "#3ba272", "#fc8452", "#9a60b4", "#ea7ccc"],
        "gradient": False,
        "lineWidth": 2,
        "lineSymbol": "circle",
        "lineSymbolSize": 4,
        "lineSmooth": True,
        "barDefault": True,
        "radiusColumnBar": "rightAngle",
        "columnBarRightAngleRadius": 20,
        "columnWidthRatio": 60,
        "barWidth": 40,
        "barGap": 0.4,
        "lineType": "solid",
    },
    "misc": {
        "pieInnerRadius": 0,
        "pieOuterRadius": 80,
        "radarShape": "polygon",
        "radarSize": 80,
    },
    "label": {
        "show": False,
        "position": "top",
        "color": "#909399",
        "fontSize": 12,
        "formatter": "",
        "labelLine": {"show": True},
        "reserveDecimalCount": 2,
        "showDimension": True,
        "showQuota": False,
        "showProportion": True,
    },
    "tooltip": {
        "show": True,
        "trigger": "item",
        "confine": True,
        "fontSize": 12,
        "color": "#909399",
        "backgroundColor": "#ffffff",
        "seriesTooltipFormatter": [],
    },
    "map": {"id": "", "level": "world"},
}

_DEFAULT_CHART_CUSTOM_STYLE: dict[str, object] = {
    "text": {
        "show": True,
        "fontSize": 16,
        "color": "#ffffff",
        "hPosition": "left",
        "vPosition": "top",
        "isItalic": False,
        "isBolder": True,
        "remarkShow": False,
        "remark": "",
        "remarkBackgroundColor": "#ffffff",
        "fontFamily": "",
        "letterSpace": "0",
        "fontShadow": False,
    },
    "legend": {
        "show": True,
        "hPosition": "center",
        "vPosition": "bottom",
        "orient": "horizontal",
        "icon": "circle",
        "color": "#333333",
        "fontSize": 12,
    },
    "xAxis": {
        "show": True,
        "position": "bottom",
        "nameShow": False,
        "color": "#333333",
        "fontSize": 12,
        "axisLabel": {"show": True, "color": "#333333", "fontSize": 12, "rotate": 0, "formatter": "{value}", "lengthLimit": 10},
        "axisLine": {"show": True, "lineStyle": {"color": "#cccccc", "width": 1, "style": "solid"}},
        "splitLine": {"show": False, "lineStyle": {"color": "#cccccc", "width": 1, "style": "solid"}},
    },
    "yAxis": {
        "show": True,
        "position": "left",
        "nameShow": False,
        "color": "#333333",
        "fontSize": 12,
        "axisLabel": {"show": True, "color": "#333333", "fontSize": 12, "rotate": 0, "formatter": "{value}", "lengthLimit": 10},
        "axisLine": {"show": False, "lineStyle": {"color": "#cccccc", "width": 1, "style": "solid"}},
        "splitLine": {"show": True, "lineStyle": {"color": "#cccccc", "width": 1, "style": "solid"}},
    },
    "misc": {
        "showName": False,
        "color": "#999",
        "fontSize": 12,
        "axisColor": "#999",
        "splitNumber": 5,
    },
}

_DEFAULT_CHART_SENIOR: dict[str, object] = {
    "functionCfg": {},
    "assistLineCfg": {"enable": False, "assistLine": []},
    "threshold": {"enable": False},
    "scrollCfg": {"open": False, "row": 1, "interval": 2000, "step": 50},
    "areaMapping": {},
    "bubbleCfg": {"enable": False},
}


def _deep_merge_defaults(defaults: object, value: object) -> object:
    if isinstance(defaults, dict):
        merged: dict[str, object] = {}
        value_dict = value if isinstance(value, dict) else {}
        for key, default_value in defaults.items():
            if key in value_dict:
                merged[key] = _deep_merge_defaults(default_value, value_dict[key])
            else:
                merged[key] = deepcopy(default_value)
        for key, current_value in value_dict.items():
            if key not in merged:
                merged[key] = deepcopy(current_value)
        return merged
    if isinstance(defaults, list):
        if isinstance(value, list):
            return deepcopy(value)
        return deepcopy(defaults)
    return deepcopy(value if value is not None else defaults)


def _enrich_canvas_style_data(canvas_style_data: object) -> object:
    """Enrich canvasStyleData with dashboard defaults for frontend compatibility."""
    if not isinstance(canvas_style_data, dict):
        return canvas_style_data
    return _deep_merge_defaults(_DEFAULT_CANVAS_STYLE_DATA, canvas_style_data)


def _enrich_chart_view(chart_dict: dict[str, object]) -> dict[str, object]:
    """Enrich a single canvasViewInfo entry with frontend-required defaults."""
    enriched = dict(chart_dict)

    for field in ("customAttr", "customStyle", "senior"):
        raw = enriched.get(field)
        if isinstance(raw, str):
            try:
                enriched[field] = _json.loads(raw)
            except (ValueError, TypeError):
                pass

    custom_attr = enriched.get("customAttr")
    if isinstance(custom_attr, dict):
        enriched["customAttr"] = _deep_merge_defaults(_DEFAULT_CHART_CUSTOM_ATTR, custom_attr)
    elif custom_attr is None:
        enriched["customAttr"] = deepcopy(_DEFAULT_CHART_CUSTOM_ATTR)

    custom_style = enriched.get("customStyle")
    if isinstance(custom_style, dict):
        enriched["customStyle"] = _deep_merge_defaults(_DEFAULT_CHART_CUSTOM_STYLE, custom_style)
    elif custom_style is None:
        enriched["customStyle"] = deepcopy(_DEFAULT_CHART_CUSTOM_STYLE)

    senior = enriched.get("senior")
    if isinstance(senior, dict):
        enriched["senior"] = _deep_merge_defaults(_DEFAULT_CHART_SENIOR, senior)
    elif senior is None:
        enriched["senior"] = deepcopy(_DEFAULT_CHART_SENIOR)

    for field in ("xAxis", "yAxis", "xAxisExt", "yAxisExt", "extStack", "drillFields", "viewFields", "extBubble", "extLabel", "extTooltip", "sortPriority"):
        if not isinstance(enriched.get(field), list):
            enriched[field] = []

    enriched.setdefault("type", "bar")
    enriched.setdefault("render", "antv")
    enriched.setdefault("title", "")
    enriched.setdefault("resultMode", "custom")
    enriched.setdefault("resultCount", 1000)
    enriched.setdefault("refreshViewEnable", False)
    enriched.setdefault("refreshTime", 5)
    enriched.setdefault("refreshUnit", "minute")
    enriched.setdefault("isPlugin", False)
    enriched.setdefault("plugin", {"isPlugin": False, "staticMap": None})
    enriched.setdefault("customFilter", {})
    enriched.setdefault("flowMapStartName", [])
    enriched.setdefault("flowMapEndName", [])

    return enriched


def _enrich_component_item(component: object, visualization_type: str | None, canvas_id: str = "canvas-main") -> object:
    if not isinstance(component, dict):
        return component

    enriched = deepcopy(component)
    component_type = enriched.get("component")

    if component_type == "UserView":
        defaults = deepcopy(_DEFAULT_USER_VIEW)
        defaults["commonBackground"] = deepcopy(
            _COMMON_COMPONENT_BACKGROUND_LIGHT if visualization_type == "dashboard" else _COMMON_COMPONENT_BACKGROUND_DARK
        )
        defaults["canvasId"] = canvas_id
        return _deep_merge_defaults(defaults, enriched)

    if component_type == "Group":
        prop_value = enriched.get("propValue")
        if isinstance(prop_value, list):
            enriched["propValue"] = [
                _enrich_component_item(item, visualization_type, str(enriched.get("id") or canvas_id)) for item in prop_value
            ]
        return enriched

    if component_type == "DeTabs":
        prop_value = enriched.get("propValue")
        tab_owner = str(enriched.get("id") or canvas_id)
        if isinstance(prop_value, list):
            new_tabs: list[object] = []
            for tab in prop_value:
                if not isinstance(tab, dict):
                    new_tabs.append(tab)
                    continue
                tab_copy = deepcopy(tab)
                tab_name = str(tab_copy.get("name") or "")
                tab_canvas_id = f"{tab_owner}--{tab_name}" if tab_name else tab_owner
                tab_components = tab_copy.get("componentData")
                if isinstance(tab_components, list):
                    tab_copy["componentData"] = [
                        _enrich_component_item(item, visualization_type, tab_canvas_id) for item in tab_components
                    ]
                new_tabs.append(tab_copy)
            enriched["propValue"] = new_tabs
        return enriched

    return enriched


def _enrich_component_data(component_data: object | None, visualization_type: str | None) -> object | None:
    if not isinstance(component_data, list):
        return component_data
    return [_enrich_component_item(component, visualization_type) for component in component_data]


def _build_tree(items: list[DataVisualizationInfo]) -> list[VisualizationTreeNodeResponse]:
    nodes: dict[int, VisualizationTreeNodeResponse] = {}
    for item in items:
        node = VisualizationTreeNodeResponse.model_validate(item)
        node.leaf = item.node_type == "leaf"
        # Frontend uses !children?.length to detect leaf nodes,
        # so only initialise children list for non-leaf (folder) nodes.
        if node.leaf:
            node.children = None
        else:
            node.children = []
        nodes[item.id] = node
    roots: list[VisualizationTreeNodeResponse] = []
    for item in items:
        node = nodes[item.id]
        if item.pid in (None, 0) or item.pid not in nodes:
            roots.append(node)
        else:
            parent = nodes[item.pid]
            if parent.children is None:
                parent.children = []
            parent.children.append(node)
    return roots


@final
class VisualizationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.visualization_repo = VisualizationRepository(session)
        self.store_repo = StoreRepository(session)
        self.chart_repo = ChartRepository(session)
        self.template_repo = TemplateRepository(session)

    def _normalize_decompression_payload(self, payload: dict[str, object]) -> dict[str, object]:
        normalized = dict(payload)

        component_data = normalized.get("componentData")
        if isinstance(component_data, (dict, list)):
            normalized["componentData"] = _json.dumps(component_data, ensure_ascii=False)

        canvas_style_data = normalized.get("canvasStyleData")
        if isinstance(canvas_style_data, (dict, list)):
            normalized["canvasStyleData"] = _json.dumps(canvas_style_data, ensure_ascii=False)

        if "canvasViewInfo" not in normalized and "dynamicData" in normalized:
            normalized["canvasViewInfo"] = normalized.get("dynamicData")

        return normalized

    async def tree(self, payload: VisualizationTreeRequest) -> object:
        items = await self.visualization_repo.list_all_ordered()
        visible = [item for item in items if not item.delete_flag]

        type_filter = self._busi_flag_to_type_filter(
            payload.busi_flag if hasattr(payload, "busi_flag") else None
        )
        if type_filter:
            visible = [item for item in visible if item.type in type_filter]

        nodes = _build_tree(visible)

        def _node_to_dict(node: VisualizationTreeNodeResponse) -> dict[str, object]:
            data = node.model_dump(by_alias=True)
            data["id"] = _sid(data.get("id"))
            data["pid"] = _sid(data.get("pid"))
            data["children"] = [_node_to_dict(child) for child in (node.children or [])] if node.children is not None else None
            return data

        if not nodes:
            return [{
                "id": "0",
                "name": "root",
                "pid": -1,
                "leaf": False,
                "weight": 7,
                "extraFlag": 0,
                "extraFlag1": 1,
                "children": [],
            }]

        return [_node_to_dict(node) for node in nodes]  # type: ignore[return-value]

    async def find_by_id(self, payload: VisualizationFindByIdRequest) -> object:
        item = await self._get_visualization(payload.id)
        result = self._serialize_visualization(item)
        # Attach canvasViewInfo — map of chartId -> chart view details
        charts = await self.chart_repo.list_by_scene(payload.id)
        view_info: dict[str, object] = {}
        for chart in charts:
            chart_dict: dict[str, object] = {}
            for col in CoreChartView.__table__.columns:
                val = getattr(chart, col.name, None)
                if col.name == "id":
                    chart_dict["id"] = _sid(val)
                else:
                    chart_dict[self._snake_to_camel(col.name)] = val
            # Parse JSON string fields that frontend expects as objects
            for json_field in ("customAttr", "customStyle", "customFilter", "senior", "xAxis", "yAxis", "xAxisExt", "yAxisExt", "extStack", "extBubble", "extLabel", "extTooltip", "drillFields", "viewFields", "extColor"):
                raw = chart_dict.get(json_field)
                if isinstance(raw, str):
                    try:
                        chart_dict[json_field] = _json.loads(raw)
                    except (ValueError, TypeError):
                        pass
            view_info[str(chart.id)] = _enrich_chart_view(chart_dict)
        result["canvasViewInfo"] = view_info
        canvas_style = result.get("canvasStyleData")
        if isinstance(canvas_style, str):
            try:
                canvas_style = _json.loads(canvas_style)
            except (ValueError, TypeError):
                canvas_style = {}
        if canvas_style is None:
            canvas_style = deepcopy(_DEFAULT_CANVAS_STYLE_DATA)
        if isinstance(canvas_style, dict):
            canvas_style = _enrich_canvas_style_data(canvas_style)
            result["canvasStyleData"] = _json.dumps(canvas_style, ensure_ascii=False)
        return result  # type: ignore[return-value]

    async def save(self, payload: VisualizationSaveRequest, user: TokenUser) -> VisualizationResponse:
        items = list(await self.visualization_repo.list_all_ordered())
        now = _timestamp_ms()
        pid = _normalize_int(payload.pid)
        created = await self.visualization_repo.create({
            **payload.model_dump(by_alias=False, exclude_none=True),
            "id": payload.id or _new_identifier(),
            "pid": pid,
            "level": _compute_level(items, pid),
            "create_time": now,
            "create_by": str(user.user_id),
            "update_time": now,
            "update_by": str(user.user_id),
            "delete_flag": bool(payload.delete_flag) if payload.delete_flag is not None else False,
        })
        return VisualizationResponse.model_validate(created)

    async def update(self, payload: VisualizationUpdateRequest, user: TokenUser) -> VisualizationResponse:
        existing = await self._get_visualization(payload.id)
        items = list(await self.visualization_repo.list_all_ordered())
        new_pid = _normalize_int(payload.pid) if payload.pid is not None else existing.pid
        update_data = payload.model_dump(by_alias=False, exclude_none=True)
        update_data.update({
            "pid": new_pid,
            "level": _compute_level(items, new_pid),
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        updated = await self.visualization_repo.update(existing, update_data)
        return VisualizationResponse.model_validate(updated)

    async def save_canvas(self, payload: VisualizationCanvasRequest, user: TokenUser) -> dict[str, object]:
        items = list(await self.visualization_repo.list_all_ordered())
        now = _timestamp_ms()
        visualization_id = payload.id or _new_identifier()
        pid = _normalize_int(payload.pid)
        existing = await self.visualization_repo.get_by_id(visualization_id)
        if existing is None:
            component_data = _enrich_component_data(_parse_json_value(payload.component_data), payload.type)
            canvas_style = _parse_json_value(payload.canvas_style_data)
            if canvas_style is None:
                canvas_style = deepcopy(_DEFAULT_CANVAS_STYLE_DATA)
            if isinstance(canvas_style, dict):
                canvas_style = _enrich_canvas_style_data(canvas_style)
            created = await self.visualization_repo.create({
                "id": visualization_id,
                "name": payload.name,
                "pid": pid,
                "level": _compute_level(items, pid),
                "node_type": "leaf",
                "type": payload.type,
                "canvas_style_data": canvas_style,
                "component_data": self._merge_component_state(component_data, None),
                "mobile_layout": payload.mobile_layout,
                "status": payload.status if payload.status is not None else 0,
                "content_id": payload.content_id,
                "check_version": payload.check_version,
                "create_time": now,
                "create_by": str(user.user_id),
                "update_time": now,
                "update_by": str(user.user_id),
                "delete_flag": False,
            })
        else:
            component_data = _enrich_component_data(_parse_json_value(payload.component_data), payload.type or existing.type)
            canvas_style = _parse_json_value(payload.canvas_style_data)
            if canvas_style is None:
                canvas_style = deepcopy(_DEFAULT_CANVAS_STYLE_DATA)
            if isinstance(canvas_style, dict):
                canvas_style = _enrich_canvas_style_data(canvas_style)
            created = await self.visualization_repo.update(existing, {
                "name": payload.name,
                "pid": pid if pid is not None else existing.pid,
                "level": _compute_level(items, pid if pid is not None else existing.pid),
                "node_type": existing.node_type or "leaf",
                "type": payload.type or existing.type,
                "canvas_style_data": canvas_style,
                "component_data": self._merge_component_state(component_data, existing.component_data),
                "mobile_layout": payload.mobile_layout if payload.mobile_layout is not None else existing.mobile_layout,
                "status": payload.status if payload.status is not None else existing.status,
                "content_id": payload.content_id if payload.content_id is not None else existing.content_id,
                "check_version": payload.check_version if payload.check_version is not None else existing.check_version,
                "update_time": now,
                "update_by": str(user.user_id),
            })
        await self._sync_canvas_views(created.id, payload.canvas_view_info, user, delete_missing=False)
        return {"id": _sid(created.id), "status": 0}

    async def update_canvas(self, payload: VisualizationCanvasRequest, user: TokenUser) -> dict[str, object]:
        if payload.id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Visualization id is required")
        existing = await self._get_visualization(payload.id)
        items = list(await self.visualization_repo.list_all_ordered())
        pid = _normalize_int(payload.pid)
        canvas_style = _parse_json_value(payload.canvas_style_data)
        if canvas_style is None:
            canvas_style = deepcopy(_DEFAULT_CANVAS_STYLE_DATA)
        if isinstance(canvas_style, dict):
            canvas_style = _enrich_canvas_style_data(canvas_style)
        component_data = self._merge_component_state(
            _enrich_component_data(_parse_json_value(payload.component_data), payload.type or existing.type),
            existing.component_data,
        )
        await self.visualization_repo.update(existing, {
            "name": payload.name,
            "pid": pid if pid is not None else existing.pid,
            "level": _compute_level(items, pid if pid is not None else existing.pid),
            "node_type": existing.node_type or "leaf",
            "type": payload.type or existing.type,
            "canvas_style_data": canvas_style,
            "component_data": component_data,
            "mobile_layout": payload.mobile_layout,
            "status": 2,
            "content_id": payload.content_id,
            "check_version": payload.check_version,
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        await self._sync_canvas_views(existing.id, payload.canvas_view_info, user, delete_missing=True)
        return {"status": 2}

    async def update_base(self, payload: VisualizationUpdateBaseRequest, user: TokenUser) -> dict[str, object]:
        existing = await self._get_visualization(payload.id)
        items = list(await self.visualization_repo.list_all_ordered())
        pid = _normalize_int(payload.pid)
        updated = await self.visualization_repo.update(existing, {
            "name": payload.name.strip() if payload.name else existing.name,
            "pid": pid if pid is not None else existing.pid,
            "level": _compute_level(items, pid if pid is not None else existing.pid),
            "node_type": payload.node_type or existing.node_type,
            "type": payload.type or existing.type,
            "mobile_layout": payload.mobile_layout if payload.mobile_layout is not None else existing.mobile_layout,
            "status": payload.status if payload.status is not None else existing.status,
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        return self._serialize_visualization(updated)

    async def update_publish_status(self, payload: VisualizationPublishStatusRequest, user: TokenUser) -> dict[str, object]:
        existing = await self._get_visualization(payload.id)
        component_data = self._merge_component_state(existing.component_data, existing.component_data, payload.active_view_ids)
        updated = await self.visualization_repo.update(existing, {
            "status": payload.status,
            "component_data": component_data,
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        return {"id": _sid(updated.id), "status": updated.status}

    async def name_check(self, payload: VisualizationNameCheckRequest) -> bool:
        pid = _normalize_int(payload.pid)
        normalized_name = payload.name.strip()
        items = await self.visualization_repo.list_all_ordered()
        for item in items:
            if item.delete_flag:
                continue
            if _normalize_int(item.pid) != pid:
                continue
            if (item.name or "").strip() != normalized_name:
                continue
            if payload.type and item.type != payload.type:
                continue
            if payload.opt == "edit" and payload.id is not None and item.id == payload.id:
                continue
            return False
        return True

    async def check_canvas_change(self, payload: VisualizationCanvasChangeRequest) -> str:
        existing = await self._get_visualization(payload.id)
        if payload.content_id and existing.content_id and payload.content_id != existing.content_id:
            return "Repeat"
        if payload.check_version and existing.check_version and payload.check_version != existing.check_version:
            return "Repeat"
        return "NoChange"

    async def recover_to_published(self, payload: VisualizationFindByIdRequest) -> object:
        return await self.find_by_id(payload)

    async def delete_logic(self, payload: VisualizationDeleteLogicRequest, user: TokenUser) -> dict[str, object]:
        await self.delete(payload.dv_id, user)
        return self._serialize_visualization(await self._get_visualization(payload.dv_id))

    async def find_copy_resource(self, dv_id: int, busi_flag: str) -> object:
        return await self.find_by_id(VisualizationFindByIdRequest(id=dv_id, busi_flag=busi_flag))

    async def copy(self, payload: VisualizationCopyRequest, user: TokenUser) -> str:
        source = await self._get_visualization(payload.id)
        copied_payload = cast(
            dict[str, Any],
            await self.find_copy_resource(payload.id, payload.busi_flag or self._copy_busi_flag_for_type(payload.type or source.type)),
        )
        component_data = _parse_json_value(cast(str | None, copied_payload.get("componentData")))
        canvas_style_data = _parse_json_value(cast(str | None, copied_payload.get("canvasStyleData")))
        canvas_view_info = copied_payload.get("canvasViewInfo")
        if not isinstance(canvas_view_info, dict):
            canvas_view_info = {}

        copied_view_info, id_map = self._duplicate_canvas_view_info(cast(dict[str, dict[str, object]], canvas_view_info))
        duplicated_component_data = self._replace_nested_ids(component_data, id_map)
        duplicated_payload = VisualizationCanvasRequest(
            id=_new_identifier(),
            name=(payload.name or source.name or "copy").strip(),
            pid=payload.pid if payload.pid is not None else source.pid,
            type=payload.type or source.type,
            canvas_style_data=_json.dumps(canvas_style_data, ensure_ascii=False) if canvas_style_data is not None else None,
            component_data=_json.dumps(duplicated_component_data, ensure_ascii=False) if duplicated_component_data is not None else None,
            canvas_view_info=copied_view_info,
            mobile_layout=source.mobile_layout,
            status=source.status,
            content_id=source.content_id,
            check_version=source.check_version,
        )
        result = await self.save_canvas(duplicated_payload, user)
        return cast(str, result["id"])

    async def interactive_tree(self, payload: object, user: TokenUser) -> object:
        _ = user
        tree_service = InteractiveTreeService(self.session)
        full_tree = await tree_service.get_tree()
        if isinstance(payload, VisualizationTreeRequest):
            branch_key = self._interactive_tree_key(payload.busi_flag)
            if branch_key is None:
                return []
            return full_tree.get(branch_key, [])

        if not isinstance(payload, dict):
            return {}

        result: dict[str, object] = {}
        for key, raw_request in payload.items():
            request = raw_request if isinstance(raw_request, dict) else {"busiFlag": key}
            busi_flag = request.get("busiFlag") or request.get("busi_flag") or key
            if not isinstance(busi_flag, str):
                continue
            branch_key = self._interactive_tree_key(busi_flag)
            if branch_key is None:
                continue
            result[key] = full_tree.get(branch_key, [])
        return result

    async def export_log_stub(self, _: object | None = None) -> list[object]:
        return []

    async def get_component_info(self, _: int) -> dict[str, object]:
        return {}

    async def export_to_app_check(self, _: object | None = None) -> dict[str, str]:
        return {"status": "ok"}

    async def app_canvas_name_check(self, _: VisualizationAppCanvasNameCheckRequest) -> str:
        return "success"

    async def decompression(self, payload: dict[str, object] | VisualizationDecompressionRequest) -> dict[str, object]:
        data = payload.data if isinstance(payload, VisualizationDecompressionRequest) else payload
        if not isinstance(data, dict):
            return {}

        if isinstance(data.get("data"), dict):
            data = data["data"]
        if not isinstance(data, dict):
            return {}

        new_from = data.get("newFrom")
        template_id = data.get("templateId")
        if new_from == "new_inner_template" and isinstance(template_id, str) and template_id:
            tpl = await self.template_repo.get_by_id(template_id)
            if tpl is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
            canvas_style_data = tpl.template_style or {}
            component_data = tpl.template_data or []
            canvas_view_info = tpl.dynamic_data or {}

            if isinstance(canvas_style_data, dict) and "component" not in canvas_style_data and isinstance(canvas_view_info, dict):
                scene_id = next(
                    (
                        item.get("sceneId")
                        for item in canvas_view_info.values()
                        if isinstance(item, dict) and item.get("sceneId")
                    ),
                    None,
                )
                if scene_id not in (None, "", "0"):
                    try:
                        source_result = await self.find_by_id(
                            VisualizationFindByIdRequest(id=int(scene_id), busi_flag=tpl.dv_type or None)
                        )
                    except (HTTPException, ValueError, TypeError):
                        source_result = None
                    if isinstance(source_result, dict):
                        source_canvas_style = source_result.get("canvasStyleData")
                        source_component_data = source_result.get("componentData")
                        source_canvas_view_info = source_result.get("canvasViewInfo")
                        if source_canvas_style:
                            canvas_style_data = source_canvas_style
                        if source_component_data:
                            component_data = source_component_data
                        if source_canvas_view_info:
                            canvas_view_info = source_canvas_view_info

            return self._normalize_decompression_payload({
                "name": tpl.name or "",
                "type": tpl.dv_type or "PANEL",
                "dvType": tpl.dv_type or "PANEL",
                "nodeType": tpl.node_type or "template",
                "snapshot": tpl.snapshot or "",
                "canvasStyleData": canvas_style_data,
                "componentData": component_data,
                "dynamicData": canvas_view_info,
                "canvasViewInfo": canvas_view_info,
                "version": 3,
            })

        return self._normalize_decompression_payload(data)

    async def delete(self, visualization_id: int, user: TokenUser) -> VisualizationResponse:
        existing = await self._get_visualization(visualization_id)
        updated = await self.visualization_repo.update(existing, {
            "delete_flag": True,
            "delete_time": _timestamp_ms(),
            "delete_by": str(user.user_id),
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        return VisualizationResponse.model_validate(updated)

    async def move(self, payload: VisualizationMoveRequest, user: TokenUser) -> VisualizationResponse:
        existing = await self._get_visualization(payload.id)
        items = list(await self.visualization_repo.list_all_ordered())
        pid = _normalize_int(payload.pid)
        updated = await self.visualization_repo.update(existing, {
            "pid": pid,
            "level": _compute_level(items, pid),
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        return VisualizationResponse.model_validate(updated)

    async def rename(self, payload: VisualizationRenameRequest, user: TokenUser) -> VisualizationResponse:
        existing = await self._get_visualization(payload.id)
        updated = await self.visualization_repo.update(existing, {
            "name": payload.name.strip(),
            "update_time": _timestamp_ms(),
            "update_by": str(user.user_id),
        })
        return VisualizationResponse.model_validate(updated)

    async def find_recent(self, payload: VisualizationRecentRequest) -> list[VisualizationResponse]:
        items = await self.visualization_repo.list_recent(
            size=payload.size,
            type_filter=payload.type,
            keyword=payload.keyword,
            asc=payload.asc,
        )
        return [VisualizationResponse.model_validate(item) for item in items]

    async def per_resource(self, visualization_id: int) -> object:
        item = await self._get_visualization(visualization_id)
        return self._serialize_visualization(item)  # type: ignore[return-value]

    async def view_detail_list(self, visualization_id: int) -> list[ChartResponse]:
        charts = await self.chart_repo.list_by_scene(visualization_id)
        return [ChartResponse.model_validate(chart) for chart in charts]

    async def favorited(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        item = await self.store_repo.get_by_resource(resource_id, user.user_id, resource_type)
        return StoreResponse(resource_id=resource_id, favorited=item is not None)

    async def add_store(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        existing = await self.store_repo.get_by_resource(resource_id, user.user_id, resource_type)
        if existing is None:
            await self.store_repo.create({
                "id": _new_identifier(),
                "resource_id": resource_id,
                "uid": user.user_id,
                "resource_type": resource_type,
                "time": _timestamp_ms(),
            })
        return StoreResponse(resource_id=resource_id, favorited=True)

    async def remove_store(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        await self.store_repo.delete_by_resource(resource_id, user.user_id, resource_type)
        return StoreResponse(resource_id=resource_id, favorited=False)

    async def execute_store(self, payload: StoreExecuteRequest, user: TokenUser) -> StoreResponse:
        resource_type = self._normalize_store_resource_type(payload.resource_type, payload.type)
        existing = await self.store_repo.get_by_resource(payload.resource_id, user.user_id, resource_type)
        if existing is None:
            return await self.add_store(payload.resource_id, resource_type, user)
        return await self.remove_store(payload.resource_id, resource_type, user)

    async def query_stores(
        self,
        user: TokenUser,
        keyword: str | None = None,
        type_filter: str | None = None,
        asc: bool | None = None,
    ) -> dict[str, object]:
        """Query favorited items for the current user, joined with visualization info."""
        resource_type = None
        if type_filter == "panel":
            resource_type = 1
        elif type_filter == "screen":
            resource_type = 2

        try:
            stores = await self.store_repo.query_by_user(user.user_id, resource_type)
        except (AttributeError, TypeError):
            return {"totalCount": 0, "list": []}

        resource_ids = [store.resource_id for store in stores if store.resource_id]
        viz_map: dict[int, DataVisualizationInfo] = {}
        if resource_ids:
            viz_rows = await self.visualization_repo.get_by_ids(resource_ids)
            viz_map = {viz.id: viz for viz in viz_rows}

        result_list = []
        for store in stores:
            viz = viz_map.get(store.resource_id)
            if viz is None or viz.delete_flag:
                continue
            if keyword and keyword.lower() not in (viz.name or "").lower():
                continue
            result_list.append({
                "id": viz.id,
                "name": viz.name or "",
                "type": viz.type or "panel",
                "creator": viz.create_by or "",
                "lastEditor": viz.update_by or "",
                "lastEditTime": viz.update_time,
                "storeId": store.id,
                "resourceType": store.resource_type,
            })

        if asc:
            result_list.reverse()

        return {"totalCount": len(result_list), "list": result_list}

    async def get_view_linkage_gather(self, payload: LinkageRequest) -> dict[str, object]:
        return await self._read_meta(payload.dv_id, payload.view_id, "_linkage")

    async def get_view_linkage_gather_array(self, payload: LinkageRequest) -> list[object]:
        data = await self._read_meta(payload.dv_id, payload.view_id, "_linkage")
        config = data.get("config", [])
        return list(config) if isinstance(config, list) else []

    async def save_linkage(self, payload: LinkageRequest) -> dict[str, object]:
        return await self._write_meta(payload.dv_id, payload.view_id, "_linkage", payload.model_dump(by_alias=True, exclude_none=True))

    async def get_visualization_all_linkage_info(self, dv_id: int, resource_table: str) -> dict[str, object]:
        return await self._read_meta(dv_id, None, "_linkage", resource_table)

    async def update_linkage_active(self, payload: LinkageRequest) -> dict[str, object]:
        current = await self._read_meta(payload.dv_id, payload.view_id, "_linkage")
        current["active"] = payload.active
        return await self._write_meta(payload.dv_id, payload.view_id, "_linkage", current)

    async def remove_linkage(self, payload: LinkageRequest) -> dict[str, object]:
        return await self._write_meta(payload.dv_id, payload.view_id, "_linkage", {})

    async def get_table_field_with_view_id(self, view_id: int) -> list[object]:
        chart = await self.chart_repo.get_by_id(view_id)
        if chart is None:
            return []
        if isinstance(chart.view_fields, list):
            return chart.view_fields
        return []

    async def query_with_view_id(self, dv_id: int, view_id: int) -> dict[str, object]:
        return await self._read_meta(dv_id, view_id, "_jump")

    async def update_jump_set(self, payload: JumpRequest) -> dict[str, object]:
        return await self._write_meta(payload.dv_id, payload.view_id, "_jump", payload.model_dump(by_alias=True, exclude_none=True))

    async def query_target_visualization_jump_info(self, payload: JumpRequest) -> dict[str, object]:
        return await self._read_meta(payload.target_dv_id or payload.dv_id, payload.view_id, "_jump")

    async def query_visualization_jump_info(self, dv_id: int, resource_table: str) -> dict[str, object]:
        return await self._read_meta(dv_id, None, "_jump", resource_table)

    async def update_jump_set_active(self, payload: JumpRequest) -> dict[str, object]:
        current = await self._read_meta(payload.dv_id, payload.view_id, "_jump")
        current["active"] = payload.active
        return await self._write_meta(payload.dv_id, payload.view_id, "_jump", current)

    async def remove_jump_set(self, payload: JumpRequest) -> dict[str, object]:
        return await self._write_meta(payload.dv_id, payload.view_id, "_jump", {})

    async def query_with_visualization_id(self, dv_id: int) -> dict[str, object]:
        return await self._read_meta(dv_id, None, "_outerParams")

    async def update_outer_params_set(self, payload: OuterParamsRequest) -> dict[str, object]:
        return await self._write_meta(payload.dv_id, None, "_outerParams", payload.model_dump(by_alias=True, exclude_none=True))

    async def get_outer_params_info(self, dv_id: int) -> dict[str, object]:
        data = await self._read_meta(dv_id, None, "_outerParams")
        return {"dvId": dv_id, "params": data.get("params", [])}

    async def query_ds_with_visualization_id(self, dv_id: int) -> list[dict[str, Any]]:
        visualization = await self._get_visualization(dv_id)
        component_data = visualization.component_data if isinstance(visualization.component_data, dict | list) else None
        dataset_ids: list[dict[str, Any]] = []

        def _collect_dataset_ids(components: list[object] | None) -> None:
            if not isinstance(components, list):
                return
            for item in components:
                if not isinstance(item, dict):
                    continue
                if item.get("datasetId") is not None:
                    dataset_ids.append({"datasetId": item.get("datasetId")})
                prop_value = item.get("propValue")
                if isinstance(prop_value, list):
                    for sub in prop_value:
                        if isinstance(sub, dict) and isinstance(sub.get("componentData"), list):
                            _collect_dataset_ids(sub["componentData"])

        if isinstance(component_data, list):
            _collect_dataset_ids(component_data)
        return dataset_ids

    async def find_dv_type(self, dv_id: int) -> str:
        item = await self.visualization_repo.get_by_id(dv_id)
        if item is None or item.type is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visualization not found")
        return item.type

    async def update_check_version(self, dv_id: int) -> str:
        item = await self._get_visualization(dv_id)
        await self.visualization_repo.update(item, {"check_version": str(_timestamp_ms())})
        return ""

    async def save_watermark(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"success": True}

    async def _sync_canvas_views(
        self,
        visualization_id: int,
        canvas_view_info: dict[str, dict[str, object]],
        user: TokenUser,
        *,
        delete_missing: bool,
    ) -> None:
        now = _timestamp_ms()
        keep_ids: set[int] = set()
        for raw_view_id, chart_info in canvas_view_info.items():
            view_id = self._resolve_chart_id(raw_view_id, chart_info)
            keep_ids.add(view_id)
            existing = await self.chart_repo.get_by_id(view_id)
            chart_payload = self._build_chart_payload(chart_info, view_id, visualization_id, str(user.user_id), now, existing)
            await self.chart_repo.upsert_by_id(chart_payload)
        if delete_missing:
            await self.chart_repo.delete_by_scene_excluding(visualization_id, keep_ids)

    def _build_chart_payload(
        self,
        chart_info: dict[str, object],
        view_id: int,
        visualization_id: int,
        user_id: str,
        now: int,
        existing: CoreChartView | None,
    ) -> dict[str, object]:
        field_names = {column.name for column in CoreChartView.__table__.columns}
        payload: dict[str, object] = {
            "id": view_id,
            "scene_id": visualization_id,
            "update_time": now,
        }
        if existing is None:
            payload["create_time"] = now
            payload["create_by"] = user_id
        else:
            payload["create_time"] = existing.create_time
            payload["create_by"] = existing.create_by
        for key, value in chart_info.items():
            snake_key = self._camel_to_snake(key)
            if snake_key in {"id", "scene_id", "update_by"}:
                continue
            if snake_key in field_names:
                payload[snake_key] = self._normalize_chart_field_value(snake_key, value)
        if "title" not in payload:
            payload["title"] = chart_info.get("title") or chart_info.get("name") or ""
        if "type" not in payload:
            payload["type"] = chart_info.get("type") or chart_info.get("chartType") or "bar"
        return payload

    @staticmethod
    def _normalize_chart_field_value(field_name: str, value: object) -> object:
        column = CoreChartView.__table__.columns.get(field_name)
        if column is None:
            return value
        if isinstance(column.type, (BigInteger, Integer)):
            if value in (None, "", "null"):
                return None
            if isinstance(value, str):
                try:
                    return int(value)
                except ValueError as exc:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid integer value for chart field '{field_name}'",
                    ) from exc
        return value

    @staticmethod
    def _resolve_chart_id(raw_view_id: str, chart_info: dict[str, object]) -> int:
        chart_id = chart_info.get("id", raw_view_id)
        if not isinstance(chart_id, (int, str)):
            raise TypeError("chart id must be int or str")
        return int(chart_id)

    @staticmethod
    def _camel_to_snake(value: str) -> str:
        chars: list[str] = []
        for char in value:
            if char.isupper():
                chars.extend(("_", char.lower()))
            else:
                chars.append(char)
        return "".join(chars).lstrip("_")

    @staticmethod
    def _snake_to_camel(value: str) -> str:
        parts = value.split("_")
        return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])

    @staticmethod
    def _merge_component_state(
        component_data: object | None,
        existing_component_data: object | None,
        active_view_ids: list[int] | None = None,
    ) -> object | None:
        if active_view_ids is None:
            if isinstance(component_data, list):
                return component_data
            if isinstance(component_data, dict):
                merged = dict(component_data)
                if isinstance(existing_component_data, dict) and "_activeViewIds" in existing_component_data and "_activeViewIds" not in merged:
                    merged["_activeViewIds"] = existing_component_data["_activeViewIds"]
                return merged
            return component_data

        if isinstance(component_data, dict):
            merged = dict(component_data)
        elif isinstance(existing_component_data, dict):
            merged = dict(existing_component_data)
        else:
            merged = {}
        merged["_activeViewIds"] = active_view_ids
        return merged

    async def _get_visualization(self, visualization_id: int) -> DataVisualizationInfo:
        item = await self.visualization_repo.get_by_id(visualization_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Visualization not found")
        return item

    async def _read_meta(self, dv_id: int | None, view_id: int | None, key: str, resource_table: str | None = None) -> dict[str, object]:
        if dv_id is None:
            return {"dvId": None, "viewId": _sid(view_id), "resourceTable": resource_table, "config": []}
        item = await self._get_visualization(dv_id)
        component = cast(dict[str, object], item.component_data if isinstance(item.component_data, dict) else {})
        stored = component.get(key)
        if isinstance(stored, dict):
            return stored
        return {"dvId": _sid(dv_id), "viewId": _sid(view_id), "resourceTable": resource_table, "config": []}

    async def _write_meta(self, dv_id: int | None, view_id: int | None, key: str, value: dict[str, object]) -> dict[str, object]:
        if dv_id is None:
            return {"dvId": None, "viewId": _sid(view_id), **value}
        item = await self._get_visualization(dv_id)
        component = cast(dict[str, object], item.component_data if isinstance(item.component_data, dict) else {})
        payload = {"dvId": _sid(dv_id), "viewId": _sid(view_id), **value}
        component[key] = payload
        await self.visualization_repo.update(item, {"component_data": component, "update_time": _timestamp_ms()})
        return payload

    @classmethod
    def _busi_flag_to_type_filter(cls, busi_flag: str | None) -> tuple[str, ...] | None:
        if not busi_flag:
            return None
        normalized = busi_flag.lower()
        if normalized in {"dashboard", "dashboard-copy", "panel"}:
            return ("panel",)
        if normalized in {"datav", "datav-copy", "screen"}:
            return ("screen",)
        return None

    @classmethod
    def _interactive_tree_key(cls, busi_flag: str) -> str | None:
        normalized = busi_flag.lower()
        if normalized in {"dashboard", "dashboard-copy", "panel"}:
            return "dashboard"
        if normalized in {"datav", "datav-copy", "screen"}:
            return "dataV"
        if normalized in {"dataset", "datasource"}:
            return normalized
        return None

    @classmethod
    def _copy_busi_flag_for_type(cls, visualization_type: str | None) -> str:
        if visualization_type == "screen":
            return "dataV"
        return "dashboard"

    @staticmethod
    def _normalize_store_resource_type(resource_type: int | None, type_name: str | None) -> int:
        if resource_type is not None:
            return resource_type
        normalized = (type_name or "").lower()
        if normalized in {"panel", "dashboard"}:
            return 1
        if normalized in {"datav", "screen"}:
            return 2
        return 0

    @staticmethod
    def _duplicate_canvas_view_info(
        canvas_view_info: dict[str, dict[str, object]],
    ) -> tuple[dict[str, dict[str, object]], dict[int | str, int | str]]:
        duplicated: dict[str, dict[str, object]] = {}
        id_map: dict[int | str, int | str] = {}
        for raw_id, chart_info in canvas_view_info.items():
            old_id = chart_info.get("id", raw_id)
            new_id = _new_identifier()
            id_map[raw_id] = new_id
            if isinstance(old_id, (int, str)):
                id_map[old_id] = new_id
            new_chart_info = deepcopy(chart_info)
            new_chart_info["id"] = new_id
            duplicated[str(new_id)] = cast(dict[str, object], VisualizationService._replace_nested_ids(new_chart_info, id_map))
        return duplicated, id_map

    @staticmethod
    def _replace_nested_ids(value: object, id_map: dict[int | str, int | str]) -> object:
        if isinstance(value, list):
            return [VisualizationService._replace_nested_ids(item, id_map) for item in value]
        if isinstance(value, dict):
            return {key: VisualizationService._replace_nested_ids(item, id_map) for key, item in value.items()}
        if isinstance(value, (int, str)) and value in id_map:
            return id_map[value]
        if isinstance(value, str):
            try:
                numeric_value = int(value)
            except ValueError:
                return value
            return id_map.get(numeric_value, value)
        return value

    @staticmethod
    def _serialize_visualization(item: DataVisualizationInfo) -> dict[str, object]:
        payload = VisualizationResponse.model_validate(item).model_dump(by_alias=True)
        payload["id"] = _sid(payload.get("id"))
        payload["pid"] = _sid(payload.get("pid"))
        # Frontend expects 'dashboard'/'dataV' but DB stores 'panel'/'screen'
        viz_type = payload.get("type")
        if viz_type == "panel":
            payload["type"] = "dashboard"
        elif viz_type == "screen":
            payload["type"] = "dataV"
        component_data = payload.get("componentData")
        if isinstance(component_data, dict):
            payload["componentData"] = []
        # Frontend expects JSON strings for these JSONB fields (Java backend stored as strings)
        for key in ("canvasStyleData", "componentData"):
            val = payload.get(key)
            if val is not None and not isinstance(val, str):
                payload[key] = _json.dumps(val, ensure_ascii=False)
        # Ensure componentData is always a JSON array (frontend calls .forEach on parsed result)
        cd_str = payload.get("componentData")
        if cd_str is None:
            payload["componentData"] = "[]"
        elif isinstance(cd_str, str):
            try:
                parsed = _json.loads(cd_str)
                if not isinstance(parsed, list):
                    payload["componentData"] = "[]"
            except (ValueError, TypeError):
                payload["componentData"] = "[]"
        return payload


async def get_visualization_service(session: AsyncSession = Depends(get_db)) -> VisualizationService:
    return VisualizationService(session)
