from __future__ import annotations

import json
import os
from types import SimpleNamespace
from typing import Any, cast

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.test_factories import stamp as _stamp  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import timestamp_ms as _timestamp_ms  # pyright: ignore[reportImplicitRelativeImport]

from app.models.chart import CoreChartView  # pyright: ignore[reportImplicitRelativeImport]
from app.models.store import CoreStore  # pyright: ignore[reportImplicitRelativeImport]
from app.models.visualization import DataVisualizationInfo  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.chart_repo import ChartRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.store_repo import StoreRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.visualization_repo import VisualizationRepository  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.visualization import (  # pyright: ignore[reportImplicitRelativeImport]
    JumpRequest,
    LinkageRequest,
    OuterParamsRequest,
    VisualizationAppCanvasNameCheckRequest,
    VisualizationCanvasChangeRequest,
    VisualizationCanvasRequest,
    VisualizationDecompressionRequest,
    VisualizationDeleteLogicRequest,
    VisualizationFindByIdRequest,
    VisualizationMoveRequest,
    VisualizationNameCheckRequest,
    VisualizationPublishStatusRequest,
    VisualizationRecentRequest,
    VisualizationRenameRequest,
    VisualizationSaveRequest,
    VisualizationTreeRequest,
    VisualizationUpdateBaseRequest,
    VisualizationUpdateRequest,
)
from app.services.visualization_service import (  # pyright: ignore[reportImplicitRelativeImport]
    VisualizationService,
    _build_tree,
    _compute_level,
    _deep_merge_defaults,
    _enrich_canvas_style_data,
    _enrich_chart_view,
    _normalize_int,
    _parse_json_value,
)

@pytest.fixture


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


def _viz_payload(
    stamp: int,
    *,
    name: str,
    pid: int | None = None,
    level: int = 0,
    node_type: str = "leaf",
    type_value: str = "panel",
    component_data: object | None = None,
    canvas_style_data: object | None = None,
    status: int = 0,
    delete_flag: bool = False,
    content_id: str | None = None,
    check_version: str | None = None,
) -> dict[str, object]:
    now = _timestamp_ms()
    return {
        "id": _stamp(),
        "name": f"{name}-{stamp}",
        "pid": pid,
        "level": level,
        "node_type": node_type,
        "type": type_value,
        "canvas_style_data": canvas_style_data,
        "component_data": component_data,
        "mobile_layout": False,
        "status": status,
        "sort": 0,
        "create_time": now,
        "create_by": "7",
        "update_time": now,
        "update_by": "7",
        "delete_flag": delete_flag,
        "content_id": content_id,
        "check_version": check_version,
    }


def _chart_payload(
    *,
    chart_id: int,
    scene_id: int,
    title: str = "chart",
    custom_attr: object | None = None,
    custom_style: object | None = None,
    senior: object | None = None,
    view_fields: object | None = None,
    x_axis: object | None = None,
    ext_color: object | None = None,
) -> dict[str, object]:
    now = _timestamp_ms()
    return {
        "id": chart_id,
        "scene_id": scene_id,
        "title": title,
        "type": "bar",
        "render": "antv",
        "result_count": 20,
        "result_mode": "custom",
        "custom_attr": custom_attr,
        "custom_style": custom_style,
        "senior": senior,
        "view_fields": view_fields,
        "x_axis": x_axis,
        "ext_color": ext_color,
        "create_by": "7",
        "create_time": now,
        "update_time": now,
    }


async def _cleanup_entities(
    session: AsyncSession,
    *,
    visualization_ids: list[int],
    chart_ids: list[int],
    store_resource_ids: list[int],
) -> None:
    if chart_ids:
        await session.execute(delete(CoreChartView).where(CoreChartView.id.in_(chart_ids)))
    if store_resource_ids:
        await session.execute(delete(CoreStore).where(CoreStore.resource_id.in_(store_resource_ids)))
    if visualization_ids:
        await session.execute(delete(DataVisualizationInfo).where(DataVisualizationInfo.id.in_(visualization_ids)))
    await session.commit()


class TestVisualizationServiceIntegration:
    pytestmark = [
        pytest.mark.asyncio,
        pytest.mark.skipif(
            os.getenv("DE_E2E") != "1",
            reason="Requires PostgreSQL (set DE_E2E=1)",
        ),
    ]

    async def test_save_update_tree_move_rename_delete_and_recent(self, db_session: AsyncSession) -> None:
        service = VisualizationService(db_session)
        repo = VisualizationRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            root = await repo.create(_viz_payload(stamp, name="root", node_type="folder", type_value="panel"))
            created_ids.append(root.id)

            created = await service.save(
                VisualizationSaveRequest(name=" Alpha ", pid=root.id, node_type="leaf", type="panel"),
                _user(),
            )
            created_ids.append(created.id)
            assert created.pid == root.id
            assert created.level == 1

            updated = await service.update(
                VisualizationUpdateRequest(id=created.id, name="Beta", pid=0, node_type="leaf", type="screen"),
                _user(),
            )
            assert updated.pid is None
            assert updated.level == 0
            assert updated.type == "screen"

            moved = await service.move(VisualizationMoveRequest(id=created.id, pid=root.id), _user())
            assert moved.pid == root.id
            assert moved.level == 1

            renamed = await service.rename(VisualizationRenameRequest(id=created.id, name="  Gamma  "), _user())
            assert renamed.name == "Gamma"

            tree = await service.tree(VisualizationTreeRequest())
            root_node = next(node for node in cast(list[dict[str, Any]], tree) if node["id"] == str(root.id))
            assert root_node["children"][0]["id"] == str(created.id)
            assert root_node["children"][0]["leaf"] is True

            recent = await service.find_recent(VisualizationRecentRequest(size=10, type="screen", keyword="Gam", asc=True))
            assert [item.id for item in recent] == [created.id]

            deleted = await service.delete(created.id, _user())
            assert deleted.delete_flag is True
            assert await service.name_check(
                VisualizationNameCheckRequest(pid=root.id, name="Gamma", type="screen", opt="new")
            )
        finally:
            await _cleanup_entities(db_session, visualization_ids=created_ids, chart_ids=[], store_resource_ids=[])

    async def test_find_by_id_and_recover_to_published_enrich_canvas_and_chart_defaults(self, db_session: AsyncSession) -> None:
        service = VisualizationService(db_session)
        viz_repo = VisualizationRepository(db_session)
        chart_repo = ChartRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        chart_ids: list[int] = []
        try:
            visualization = await viz_repo.create(
                _viz_payload(
                    stamp,
                    name="detail",
                    type_value="dashboard",
                    component_data=[{"datasetId": "d-1"}],
                    canvas_style_data={"backgroundColor": "#fff"},
                )
            )
            created_ids.append(visualization.id)
            chart = await chart_repo.create(
                _chart_payload(
                    chart_id=_stamp(),
                    scene_id=visualization.id,
                    title="sales",
                    custom_attr='{"basicStyle": {"lineWidth": 9}}',
                    custom_style='{"text": {"show": false}}',
                    senior='{"scrollCfg": {"open": true}}',
                    view_fields="invalid",
                    x_axis='["month"]',
                    ext_color='{"legend": "blue"}',
                )
            )
            chart_ids.append(chart.id)

            payload = cast(
                dict[str, Any],
                await service.find_by_id(VisualizationFindByIdRequest(id=visualization.id, busi_flag="dashboard")),
            )
            recovered = cast(dict[str, Any], await service.recover_to_published(VisualizationFindByIdRequest(id=visualization.id)))

            assert payload["id"] == str(visualization.id)
            assert recovered["id"] == str(visualization.id)
            canvas_style = json.loads(payload["canvasStyleData"])
            assert canvas_style["dashboard"]["themeColor"] == "light"
            chart_payload = payload["canvasViewInfo"][str(chart.id)]
            assert chart_payload["customAttr"]["basicStyle"]["lineWidth"] == 9
            assert chart_payload["customStyle"]["text"]["show"] is False
            assert chart_payload["senior"]["scrollCfg"]["open"] is True
            assert chart_payload["viewFields"] == []
            assert chart_payload["flowMapStartName"] is None
            assert chart_payload["plugin"]["isPlugin"] is False
        finally:
            await _cleanup_entities(db_session, visualization_ids=created_ids, chart_ids=chart_ids, store_resource_ids=[])

    async def test_save_canvas_and_update_canvas_sync_chart_views_and_component_state(self, db_session: AsyncSession) -> None:
        service = VisualizationService(db_session)
        repo = VisualizationRepository(db_session)
        chart_repo = ChartRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        chart_ids: list[int] = []
        try:
            folder = await repo.create(_viz_payload(stamp, name="folder", node_type="folder"))
            created_ids.append(folder.id)
            chart_one_id = _stamp()
            save_result = await service.save_canvas(
                VisualizationCanvasRequest(
                    name="Canvas A",
                    pid=str(folder.id),
                    type="dashboard",
                    canvas_style_data='{"width":1280}',
                    component_data='[{"id":"view-1","component":"UserView","datasetId":100}]',
                    canvas_view_info={
                        str(chart_one_id): {
                            "id": chart_one_id,
                            "title": "Revenue",
                            "chartType": "line",
                            "viewFields": [{"id": 1}],
                        }
                    },
                    mobile_layout=True,
                    content_id="c-1",
                    check_version="v1",
                ),
                _user(),
            )
            created_id = int(cast(dict[str, Any], save_result)["id"])
            created_ids.append(created_id)
            chart_ids.append(chart_one_id)

            created = await repo.get_by_id(created_id)
            assert created is not None
            assert created.mobile_layout is True
            assert isinstance(created.canvas_style_data, dict)
            assert created.canvas_style_data["width"] == 1280
            assert isinstance(created.component_data, list)

            chart_one = await chart_repo.get_by_id(chart_one_id)
            assert chart_one is not None
            assert chart_one.chart_type == "line"
            assert chart_one.title == "Revenue"

            chart_two_id = _stamp()
            chart_ids.append(chart_two_id)
            publish_result = await service.update_publish_status(
                VisualizationPublishStatusRequest(id=created_id, status=1, active_view_ids=[chart_one_id]),
                _user(),
            )
            assert publish_result == {"id": str(created_id), "status": 1}

            update_result = await service.update_canvas(
                VisualizationCanvasRequest(
                    id=created_id,
                    name="Canvas B",
                    pid=0,
                    type="dashboard",
                    canvas_style_data='{"height":720}',
                    component_data='{"extra":true}',
                    canvas_view_info={
                        str(chart_two_id): {
                            "id": chart_two_id,
                            "title": "Margin",
                            "render": "custom",
                            "customAttr": {"basicStyle": {"lineWidth": 3}},
                        }
                    },
                    content_id="c-2",
                    check_version="v2",
                    mobile_layout=False,
                ),
                _user(),
            )
            assert update_result == {"status": 2}

            updated = await repo.get_by_id(created_id)
            assert updated is not None
            assert updated.status == 2
            assert updated.content_id == "c-2"
            assert updated.check_version == "v2"
            assert isinstance(updated.component_data, dict)
            assert updated.component_data["extra"] is True
            assert updated.component_data["_activeViewIds"] == [chart_one_id]

            assert await chart_repo.get_by_id(chart_one_id) is None
            chart_two = await chart_repo.get_by_id(chart_two_id)
            assert chart_two is not None
            assert chart_two.render == "custom"
            assert chart_two.custom_attr == {"basicStyle": {"lineWidth": 3}}

            datasets = await service.query_ds_with_visualization_id(created_id)
            assert datasets == []
        finally:
            await _cleanup_entities(db_session, visualization_ids=created_ids, chart_ids=chart_ids, store_resource_ids=[])

    async def test_update_base_check_canvas_change_and_find_dv_type(self, db_session: AsyncSession) -> None:
        service = VisualizationService(db_session)
        repo = VisualizationRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            parent = await repo.create(_viz_payload(stamp, name="parent", node_type="folder"))
            created_ids.append(parent.id)
            visualization = await repo.create(
                _viz_payload(
                    stamp,
                    name="before",
                    pid=parent.id,
                    level=1,
                    type_value="dashboard",
                    status=0,
                    content_id="content-a",
                    check_version="ver-a",
                )
            )
            created_ids.append(visualization.id)

            updated = await service.update_base(
                VisualizationUpdateBaseRequest(
                    id=visualization.id,
                    name="  after  ",
                    pid=0,
                    node_type="folder",
                    type="screen",
                    mobile_layout=True,
                    status=3,
                ),
                _user(),
            )
            assert updated["name"] == "after"
            assert updated["pid"] == str(parent.id)
            assert updated["nodeType"] == "folder"
            assert updated["type"] == "screen"

            assert await service.check_canvas_change(
                VisualizationCanvasChangeRequest(id=visualization.id, content_id="other")
            ) == "Repeat"
            assert await service.check_canvas_change(
                VisualizationCanvasChangeRequest(id=visualization.id, content_id="content-a", check_version="other")
            ) == "Repeat"
            assert await service.check_canvas_change(
                VisualizationCanvasChangeRequest(id=visualization.id, content_id="content-a", check_version="ver-a")
            ) == "NoChange"

            assert await service.find_dv_type(visualization.id) == "screen"
        finally:
            await _cleanup_entities(db_session, visualization_ids=created_ids, chart_ids=[], store_resource_ids=[])

    async def test_delete_logic_find_copy_resource_update_check_version_and_decompression(self, db_session: AsyncSession) -> None:
        service = VisualizationService(db_session)
        repo = VisualizationRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        try:
            visualization = await repo.create(
                _viz_payload(
                    stamp,
                    name="logic",
                    type_value="dashboard",
                    component_data=[{"datasetId": 88}],
                    canvas_style_data={"width": 800},
                )
            )
            created_ids.append(visualization.id)

            deleted = await service.delete_logic(
                VisualizationDeleteLogicRequest(dv_id=visualization.id, busi_flag="dashboard"),
                _user(),
            )
            assert deleted["deleteFlag"] is True

            copied = cast(dict[str, Any], await service.find_copy_resource(visualization.id, "dashboard"))
            assert copied["id"] == str(visualization.id)

            assert await service.update_check_version(visualization.id) == ""
            refreshed = await repo.get_by_id(visualization.id)
            assert refreshed is not None
            assert refreshed.check_version

            passthrough = await service.decompression({"name": "demo"})
            wrapped = await service.decompression(VisualizationDecompressionRequest(data={"ok": True}))
            assert passthrough == {"name": "demo"}
            assert wrapped == {"ok": True}
            assert await service.app_canvas_name_check(VisualizationAppCanvasNameCheckRequest()) == "success"
        finally:
            await _cleanup_entities(db_session, visualization_ids=created_ids, chart_ids=[], store_resource_ids=[])

    async def test_store_and_query_stores_cover_filters_and_remove(self, db_session: AsyncSession) -> None:
        service = VisualizationService(db_session)
        repo = VisualizationRepository(db_session)
        store_repo = StoreRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        resource_ids: list[int] = []
        try:
            panel = await repo.create(_viz_payload(stamp, name="panel-store", type_value="panel"))
            screen = await repo.create(_viz_payload(stamp, name="screen-store", type_value="screen"))
            deleted = await repo.create(_viz_payload(stamp, name="deleted-store", type_value="panel", delete_flag=True))
            created_ids.extend([panel.id, screen.id, deleted.id])
            resource_ids.extend([panel.id, screen.id, deleted.id])

            assert (await service.favorited(panel.id, 1, _user())).favorited is False
            assert (await service.add_store(panel.id, 1, _user())).favorited is True
            assert (await service.add_store(panel.id, 1, _user())).favorited is True
            assert (await service.add_store(screen.id, 2, _user())).favorited is True
            await store_repo.create({
                "id": _stamp(),
                "resource_id": deleted.id,
                "uid": _user().user_id,
                "resource_type": 1,
                "time": _timestamp_ms(),
            })

            panel_only = cast(dict[str, Any], await service.query_stores(_user(), keyword="panel-store", type_filter="panel", asc=True))
            assert panel_only["totalCount"] == 1
            assert panel_only["list"][0]["id"] == panel.id
            assert panel_only["list"][0]["resourceType"] == 1

            all_items = cast(dict[str, Any], await service.query_stores(_user()))
            assert all_items["totalCount"] == 2
            assert {item["id"] for item in cast(list[dict[str, Any]], all_items["list"])} == {panel.id, screen.id}

            removed = await service.remove_store(panel.id, 1, _user())
            assert removed.favorited is False
            assert (await service.favorited(panel.id, 1, _user())).favorited is False
        finally:
            await _cleanup_entities(db_session, visualization_ids=created_ids, chart_ids=[], store_resource_ids=resource_ids)

    async def test_meta_operations_view_lists_and_per_resource(self, db_session: AsyncSession) -> None:
        service = VisualizationService(db_session)
        repo = VisualizationRepository(db_session)
        chart_repo = ChartRepository(db_session)
        stamp = _stamp()
        created_ids: list[int] = []
        chart_ids: list[int] = []
        try:
            visualization = await repo.create(
                _viz_payload(
                    stamp,
                    name="meta",
                    type_value="panel",
                    component_data={"_jump": {"dvId": "preset", "config": [1]}},
                    canvas_style_data={"width": 1000},
                )
            )
            created_ids.append(visualization.id)
            chart = await chart_repo.create(
                _chart_payload(chart_id=_stamp(), scene_id=visualization.id, title="Details", view_fields=[{"field": "region"}])
            )
            chart_ids.append(chart.id)

            linkage_saved = await service.save_linkage(
                LinkageRequest(dv_id=visualization.id, view_id=chart.id, config=[{"id": 1}], active=True)
            )
            assert linkage_saved["dvId"] == visualization.id
            assert linkage_saved["viewId"] == chart.id
            assert (await service.get_view_linkage_gather(LinkageRequest(dv_id=visualization.id, view_id=chart.id)))["config"] == []
            assert await service.get_view_linkage_gather_array(LinkageRequest(dv_id=visualization.id, view_id=chart.id)) == []
            assert (await service.update_linkage_active(LinkageRequest(dv_id=visualization.id, view_id=chart.id, active=False)))["active"] is False
            assert await service.remove_linkage(LinkageRequest(dv_id=visualization.id, view_id=chart.id)) == {
                "dvId": str(visualization.id),
                "viewId": str(chart.id),
            }

            jump_saved = await service.update_jump_set(
                JumpRequest(dv_id=visualization.id, view_id=chart.id, config=[{"target": 2}], active=True)
            )
            assert jump_saved["config"] == [{"target": 2}]
            assert (await service.query_with_view_id(visualization.id, chart.id))["dvId"]
            assert (
                await service.query_target_visualization_jump_info(
                    JumpRequest(dv_id=visualization.id, target_dv_id=visualization.id, view_id=chart.id)
                )
            )["dvId"]
            assert (await service.query_visualization_jump_info(visualization.id, "core"))["config"] == [1]
            assert (await service.update_jump_set_active(JumpRequest(dv_id=visualization.id, view_id=chart.id, active=False)))["active"] is False
            assert await service.remove_jump_set(JumpRequest(dv_id=visualization.id, view_id=chart.id)) == {
                "dvId": str(visualization.id),
                "viewId": str(chart.id),
            }

            outer_saved = await service.update_outer_params_set(
                OuterParamsRequest(dv_id=visualization.id, params=[{"name": "tenant"}])
            )
            assert outer_saved["params"] == [{"name": "tenant"}]
            assert await service.query_with_visualization_id(visualization.id) == {
                "dvId": str(visualization.id),
                "viewId": None,
                "resourceTable": None,
                "config": [],
            }
            assert await service.get_outer_params_info(visualization.id) == {
                "dvId": visualization.id,
                "params": [],
            }

            all_linkage = await service.get_visualization_all_linkage_info(visualization.id, "core")
            assert all_linkage["resourceTable"] == "core"
            assert all_linkage["config"] == []

            assert await service.get_table_field_with_view_id(chart.id) == [{"field": "region"}]
            assert await service.get_table_field_with_view_id(_stamp()) == []
            detail_list = await service.view_detail_list(visualization.id)
            assert detail_list[0].scene_id == visualization.id
            per_resource = cast(dict[str, Any], await service.per_resource(visualization.id))
            assert per_resource["id"] == str(visualization.id)
        finally:
            await _cleanup_entities(db_session, visualization_ids=created_ids, chart_ids=chart_ids, store_resource_ids=[])


class TestVisualizationServiceUnit:
    def test_parse_json_normalize_int_and_compute_level(self) -> None:
        items = [
            DataVisualizationInfo(id=1, name="root", pid=None, level=0, node_type="folder", type="panel"),
            DataVisualizationInfo(id=2, name="child", pid=1, level=1, node_type="leaf", type="panel"),
        ]

        assert _parse_json_value('{"a":1}') == {"a": 1}
        assert _parse_json_value("oops") == "oops"
        assert _parse_json_value(None) is None
        assert _normalize_int(None) is None
        assert _normalize_int("0") is None
        assert _normalize_int("12") == 12
        assert _compute_level(items, None) == 0
        assert _compute_level(items, 1) == 1
        assert _compute_level(items, 999) == 1

    def test_deep_merge_defaults_and_canvas_style_enrichment(self) -> None:
        merged = _deep_merge_defaults(
            {"a": {"x": 1, "y": [1]}, "b": 2},
            {"a": {"x": 5}, "c": 3},
        )
        enriched = _enrich_canvas_style_data({"width": 1440, "dashboard": {"gap": "no"}})

        assert merged == {"a": {"x": 5, "y": [1]}, "b": 2, "c": 3}
        enriched_dict = cast(dict[str, Any], enriched)
        assert enriched_dict["width"] == 1440
        assert cast(dict[str, Any], enriched_dict["dashboard"])["gap"] == "no"
        assert cast(dict[str, Any], enriched_dict["dashboard"])["themeColor"] == "light"

    def test_build_tree_marks_leaf_and_missing_parent_as_root(self) -> None:
        tree = _build_tree(
            [
                DataVisualizationInfo(id=11, name="child", pid=10, level=1, node_type="leaf", type="panel"),
                DataVisualizationInfo(id=12, name="orphan", pid=999, level=1, node_type="folder", type="panel"),
                DataVisualizationInfo(id=10, name="root", pid=None, level=0, node_type="folder", type="panel"),
            ]
        )

        root = next(node for node in tree if node.id == 10)
        orphan = next(node for node in tree if node.id == 12)
        assert root.children and root.children[0].id == 11
        assert root.children[0].leaf is True
        assert root.children[0].children is None
        assert orphan.children == []

    def test_enrich_chart_view_parses_strings_and_supplies_defaults(self) -> None:
        enriched = _enrich_chart_view(
            {
                "customAttr": '{"label": {"show": true}}',
                "customStyle": {"legend": {"show": False}},
                "senior": None,
                "xAxis": "bad",
                "title": "Profit",
            }
        )

        enriched_dict = cast(dict[str, Any], enriched)
        assert cast(dict[str, Any], cast(dict[str, Any], enriched_dict["customAttr"])["label"])["show"] is True
        assert cast(dict[str, Any], cast(dict[str, Any], enriched_dict["customAttr"])["basicStyle"])["lineWidth"] == 2
        assert cast(dict[str, Any], cast(dict[str, Any], enriched_dict["customStyle"])["legend"])["show"] is False
        assert cast(dict[str, Any], cast(dict[str, Any], enriched_dict["senior"])["threshold"])["enable"] is False
        assert enriched_dict["xAxis"] == []
        assert enriched_dict["title"] == "Profit"
        assert enriched_dict["render"] == "antv"

    def test_build_chart_payload_maps_keys_and_preserves_existing_create_fields(self) -> None:
        service = VisualizationService(session=cast(AsyncSession, cast(Any, None)))
        existing = cast(CoreChartView, cast(object, SimpleNamespace(create_by="creator", create_time=111)))

        payload = service._build_chart_payload(
            {
                "title": "Sales",
                "chartType": "pie",
                "customAttr": {"a": 1},
                "updateBy": "ignored",
                "unknownKey": "skip",
            },
            20,
            30,
            "7",
            999,
            existing,
        )

        assert payload["id"] == 20
        assert payload["scene_id"] == 30
        assert payload["title"] == "Sales"
        assert payload["chart_type"] == "pie"
        assert payload["custom_attr"] == {"a": 1}
        assert payload["create_by"] == "creator"
        assert payload["create_time"] == 111
        assert "update_by" not in payload
        assert "unknown_key" not in payload

    def test_resolve_chart_id_case_conversion_and_merge_component_state(self) -> None:
        assert VisualizationService._resolve_chart_id("21", {}) == 21
        assert VisualizationService._resolve_chart_id("22", {"id": 23}) == 23
        with pytest.raises(TypeError):
            VisualizationService._resolve_chart_id("24", {"id": {"bad": True}})

        assert VisualizationService._camel_to_snake("chartType") == "chart_type"
        assert VisualizationService._snake_to_camel("custom_attr_mobile") == "customAttrMobile"
        assert VisualizationService._merge_component_state([{"id": 1}], {"_activeViewIds": [9]}) == [{"id": 1}]
        assert VisualizationService._merge_component_state({"a": 1}, {"_activeViewIds": [9]}) == {
            "a": 1,
            "_activeViewIds": [9],
        }
        assert VisualizationService._merge_component_state(None, {"b": 2}, [5]) == {"b": 2, "_activeViewIds": [5]}

    async def test_read_and_write_meta_without_visualization_id(self) -> None:
        service = VisualizationService(session=cast(AsyncSession, cast(Any, None)))

        read_payload = await service._read_meta(None, 10, "_jump", "core")
        write_payload = await service._write_meta(None, 11, "_jump", {"config": [1]})

        assert read_payload == {"dvId": None, "viewId": "10", "resourceTable": "core", "config": []}
        assert write_payload == {"dvId": None, "viewId": "11", "config": [1]}

    def test_serialize_visualization_converts_ids_and_invalid_component_to_array(self) -> None:
        payload = VisualizationService._serialize_visualization(
            DataVisualizationInfo(
                id=99,
                name="Serialize",
                pid=88,
                node_type="leaf",
                type="panel",
                component_data={"_activeViewIds": [1]},
                canvas_style_data={"width": 1},
            )
        )

        assert payload["id"] == "99"
        assert payload["pid"] == "88"
        assert payload["componentData"] == "[]"
        assert json.loads(cast(str, payload["canvasStyleData"])) == {"width": 1}
