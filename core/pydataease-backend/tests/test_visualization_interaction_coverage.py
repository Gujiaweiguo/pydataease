from __future__ import annotations

# pyright: reportCallIssue=false, reportArgumentType=false, reportAttributeAccessIssue=false, reportMissingImports=false

import json
import os
from collections.abc import AsyncIterator

from typing import Any

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chart import CoreChartView  # pyright: ignore[reportImplicitRelativeImport]
from app.models.dataset import CoreDatasetGroup, CoreDatasetTableField  # pyright: ignore[reportImplicitRelativeImport]
from app.models.outer_params import (  # pyright: ignore[reportImplicitRelativeImport]
    VisualizationOuterParams,
    VisualizationOuterParamsInfo,
    VisualizationOuterParamsTargetViewInfo,
)
from app.models.visualization import DataVisualizationInfo  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.link_jump import LinkJumpBaseRequest, LinkJumpInfoDTO, LinkJumpTargetViewInfo, VisualizationLinkJumpDTO  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.linkage import LinkageFieldVO, LinkageGatherRequest, LinkageRemoveRequest, LinkageSaveRequest, LinkageUpdateActiveRequest, VisualizationLinkageDTO  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.outer_params import OuterParamsInfoDTO, OuterParamsTargetViewInfoDTO, VisualizationOuterParamsDTO  # pyright: ignore[reportImplicitRelativeImport]
from app.services.link_jump_service import LinkJumpService  # pyright: ignore[reportImplicitRelativeImport]
from app.services.linkage_service import LinkageService  # pyright: ignore[reportImplicitRelativeImport]
from app.services.outer_params_service import OuterParamsService  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.test_factories import stamp, timestamp_ms  # pyright: ignore[reportImplicitRelativeImport]

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)"),
]


def _viz_payload(viz_id: int, *, name: str, component_ids: list[int]) -> dict[str, Any]:
    now = timestamp_ms()
    return {
        "id": viz_id,
        "name": name,
        "pid": None,
        "org_id": None,
        "level": 0,
        "node_type": "leaf",
        "type": "panel",
        "canvas_style_data": None,
        "component_data": [{"id": str(component_id)} for component_id in component_ids],
        "mobile_layout": False,
        "status": 0,
        "self_watermark_status": 0,
        "sort": 0,
        "create_time": now,
        "create_by": "7",
        "update_time": now,
        "update_by": "7",
        "remark": None,
        "source": None,
        "delete_flag": False,
        "delete_time": None,
        "delete_by": None,
        "version": 1,
        "content_id": None,
        "check_version": None,
    }


def _chart_payload(view_id: int, *, scene_id: int, table_id: int, title: str, linkage_active: bool = True, jump_active: bool = True) -> dict[str, Any]:
    now = timestamp_ms()
    return {
        "id": view_id,
        "title": title,
        "scene_id": scene_id,
        "table_id": table_id,
        "type": "bar",
        "render": "antv",
        "result_count": 20,
        "result_mode": "custom",
        "x_axis": [{"name": "region", "dataeaseName": "region"}],
        "x_axis_ext": None,
        "y_axis": [{"name": "sales", "dataeaseName": "sales", "summary": "sum"}],
        "y_axis_ext": None,
        "ext_stack": None,
        "ext_bubble": None,
        "ext_label": None,
        "ext_tooltip": None,
        "custom_attr": None,
        "custom_style": None,
        "custom_filter": None,
        "drill_fields": None,
        "senior": None,
        "create_by": "7",
        "create_time": now,
        "update_time": now,
        "snapshot": None,
        "style_priority": None,
        "chart_type": "bar",
        "is_plugin": False,
        "data_from": None,
        "view_fields": None,
        "refresh_view_enable": None,
        "refresh_unit": None,
        "refresh_time": None,
        "linkage_active": linkage_active,
        "jump_active": jump_active,
        "copy_from": None,
        "copy_id": None,
        "aggregate": None,
        "flow_map_start_name": None,
        "flow_map_end_name": None,
        "ext_color": None,
        "custom_attr_mobile": None,
        "custom_style_mobile": None,
        "sort_priority": None,
    }


async def _insert_snapshot_visualization(session: AsyncSession, viz_id: int, component_ids: list[int]) -> None:
    await session.execute(
        text(
            """
            INSERT INTO snapshot_data_visualization_info (id, name, type, component_data)
            VALUES (:id, :name, :type, CAST(:component_data AS jsonb))
            """
        ),
        {
            "id": viz_id,
            "name": f"snapshot-{viz_id}",
            "type": "panel",
            "component_data": json.dumps([{"id": str(component_id)} for component_id in component_ids]),
        },
    )


async def _insert_snapshot_chart_view(
    session: AsyncSession,
    *,
    view_id: int,
    scene_id: int,
    table_id: int,
    title: str,
    linkage_active: bool = True,
    jump_active: bool = True,
) -> None:
    await session.execute(
        text(
            """
            INSERT INTO snapshot_core_chart_view (id, title, scene_id, table_id, type, linkage_active, jump_active)
            VALUES (:id, :title, :scene_id, :table_id, :type, :linkage_active, :jump_active)
            """
        ),
        {
            "id": view_id,
            "title": title,
            "scene_id": scene_id,
            "table_id": table_id,
            "type": "bar",
            "linkage_active": linkage_active,
            "jump_active": jump_active,
        },
    )


@pytest.fixture
async def interaction_seed(db_session: AsyncSession) -> AsyncIterator[dict[str, int]]:
    source_dv_id = stamp()
    target_dv_id = stamp()
    dataset_group_id = stamp()
    source_view_id = stamp()
    target_view_id = stamp()
    aux_target_view_id = stamp()
    source_field_id = stamp()
    target_field_id = stamp()
    target_field_id_2 = stamp()

    db_session.add(CoreDatasetGroup(
        id=dataset_group_id,
        name=f"group-{dataset_group_id}",
        pid=None,
        level=0,
        node_type="dataset",
        type="sql",
        mode=1,
        info=None,
        create_by="7",
        create_time=timestamp_ms(),
        qrtz_instance=None,
        sync_status=None,
        update_by="7",
        last_update_time=timestamp_ms(),
        union_sql=None,
        is_cross=False,
    ))
    db_session.add_all([
        CoreDatasetTableField(
            id=source_field_id,
            datasource_id=None,
            dataset_table_id=None,
            dataset_group_id=dataset_group_id,
            chart_id=None,
            origin_name="region",
            name="Region",
            description=None,
            dataease_name="region",
            field_short_name="region",
            group_list=None,
            other_group=None,
            group_type="d",
            type="VARCHAR",
            size=255,
            de_type=0,
            de_extract_type=0,
            ext_field=0,
            checked=True,
            column_index=0,
            last_sync_time=None,
            accuracy=None,
            date_format=None,
            date_format_type=None,
            params=None,
            order_checked=True,
        ),
        CoreDatasetTableField(
            id=target_field_id,
            datasource_id=None,
            dataset_table_id=None,
            dataset_group_id=dataset_group_id,
            chart_id=None,
            origin_name="country",
            name="Country",
            description=None,
            dataease_name="country",
            field_short_name="country",
            group_list=None,
            other_group=None,
            group_type="d",
            type="VARCHAR",
            size=255,
            de_type=0,
            de_extract_type=0,
            ext_field=0,
            checked=True,
            column_index=1,
            last_sync_time=None,
            accuracy=None,
            date_format=None,
            date_format_type=None,
            params=None,
            order_checked=True,
        ),
        CoreDatasetTableField(
            id=target_field_id_2,
            datasource_id=None,
            dataset_table_id=None,
            dataset_group_id=dataset_group_id,
            chart_id=None,
            origin_name="city",
            name="City",
            description=None,
            dataease_name="city",
            field_short_name="city",
            group_list=None,
            other_group=None,
            group_type="d",
            type="VARCHAR",
            size=255,
            de_type=0,
            de_extract_type=0,
            ext_field=0,
            checked=True,
            column_index=2,
            last_sync_time=None,
            accuracy=None,
            date_format=None,
            date_format_type=None,
            params=None,
            order_checked=True,
        ),
    ])
    db_session.add_all([
        DataVisualizationInfo(**_viz_payload(source_dv_id, name="source", component_ids=[source_view_id, target_view_id])),
        DataVisualizationInfo(**_viz_payload(target_dv_id, name="target", component_ids=[target_view_id])),
    ])
    await db_session.flush()
    db_session.add_all([
        CoreChartView(**_chart_payload(source_view_id, scene_id=source_dv_id, table_id=dataset_group_id, title="Source Chart")),
        CoreChartView(**_chart_payload(target_view_id, scene_id=source_dv_id, table_id=dataset_group_id, title="Target Chart")),
        CoreChartView(**_chart_payload(aux_target_view_id, scene_id=target_dv_id, table_id=dataset_group_id, title="Aux Chart")),
    ])
    db_session.add_all([
        VisualizationOuterParams(
            params_id=f"live-params-{source_dv_id}",
            visualization_id=str(source_dv_id),
            checked=True,
            remark=None,
            copy_from=None,
            copy_id=None,
        ),
        VisualizationOuterParamsInfo(
            params_info_id=f"live-info-{source_dv_id}",
            params_id=f"live-params-{source_dv_id}",
            param_name="tenant",
            checked=True,
            required=True,
            default_value="north",
            enabled_default=True,
            copy_from=None,
            copy_id=None,
        ),
        VisualizationOuterParamsTargetViewInfo(
            target_id=f"live-target-{source_dv_id}",
            params_info_id=f"live-info-{source_dv_id}",
            target_view_id=str(target_view_id),
            target_ds_id=str(dataset_group_id),
            target_field_id=str(target_field_id),
            copy_from=None,
            copy_id=None,
            match_mode="strict",
        ),
    ])
    await _insert_snapshot_visualization(db_session, source_dv_id, [source_view_id, target_view_id])
    await _insert_snapshot_visualization(db_session, target_dv_id, [aux_target_view_id])
    await _insert_snapshot_chart_view(db_session, view_id=source_view_id, scene_id=source_dv_id, table_id=dataset_group_id, title="Source Snapshot")
    await _insert_snapshot_chart_view(db_session, view_id=target_view_id, scene_id=source_dv_id, table_id=dataset_group_id, title="Target Snapshot")
    await _insert_snapshot_chart_view(db_session, view_id=aux_target_view_id, scene_id=target_dv_id, table_id=dataset_group_id, title="Aux Snapshot")
    await db_session.commit()

    try:
        yield {
            "source_dv_id": source_dv_id,
            "target_dv_id": target_dv_id,
            "dataset_group_id": dataset_group_id,
            "source_view_id": source_view_id,
            "target_view_id": target_view_id,
            "aux_target_view_id": aux_target_view_id,
            "source_field_id": source_field_id,
            "target_field_id": target_field_id,
            "target_field_id_2": target_field_id_2,
        }
    finally:
        try:
            await db_session.rollback()
        except Exception:
            pass
        try:
            await db_session.execute(text("DELETE FROM snapshot_visualization_link_jump_target_view_info WHERE link_jump_info_id IN (SELECT id FROM snapshot_visualization_link_jump_info WHERE link_jump_id IN (SELECT id FROM snapshot_visualization_link_jump WHERE source_dv_id = :source_dv_id OR source_dv_id = :target_dv_id))"), {"source_dv_id": source_dv_id, "target_dv_id": target_dv_id})
            await db_session.execute(text("DELETE FROM snapshot_visualization_link_jump_info WHERE link_jump_id IN (SELECT id FROM snapshot_visualization_link_jump WHERE source_dv_id = :source_dv_id OR source_dv_id = :target_dv_id)"), {"source_dv_id": source_dv_id, "target_dv_id": target_dv_id})
            await db_session.execute(text("DELETE FROM snapshot_visualization_link_jump WHERE source_dv_id = :source_dv_id OR source_dv_id = :target_dv_id"), {"source_dv_id": source_dv_id, "target_dv_id": target_dv_id})
            await db_session.execute(text("DELETE FROM snapshot_visualization_outer_params_target_view_info WHERE params_info_id IN (SELECT params_info_id FROM snapshot_visualization_outer_params_info WHERE params_id IN (SELECT params_id FROM snapshot_visualization_outer_params WHERE visualization_id = :source_viz OR visualization_id = :target_viz))"), {"source_viz": str(source_dv_id), "target_viz": str(target_dv_id)})
            await db_session.execute(text("DELETE FROM snapshot_visualization_outer_params_info WHERE params_id IN (SELECT params_id FROM snapshot_visualization_outer_params WHERE visualization_id = :source_viz OR visualization_id = :target_viz)"), {"source_viz": str(source_dv_id), "target_viz": str(target_dv_id)})
            await db_session.execute(text("DELETE FROM snapshot_visualization_outer_params WHERE visualization_id = :source_viz OR visualization_id = :target_viz"), {"source_viz": str(source_dv_id), "target_viz": str(target_dv_id)})
            await db_session.execute(text("DELETE FROM snapshot_visualization_linkage_field WHERE linkage_id IN (SELECT id FROM snapshot_visualization_linkage WHERE dv_id = :source_dv_id OR dv_id = :target_dv_id)"), {"source_dv_id": source_dv_id, "target_dv_id": target_dv_id})
            await db_session.execute(text("DELETE FROM snapshot_visualization_linkage WHERE dv_id = :source_dv_id OR dv_id = :target_dv_id"), {"source_dv_id": source_dv_id, "target_dv_id": target_dv_id})
            await db_session.execute(text("DELETE FROM snapshot_core_chart_view WHERE id = :source_view_id OR id = :target_view_id OR id = :aux_target_view_id"), {"source_view_id": source_view_id, "target_view_id": target_view_id, "aux_target_view_id": aux_target_view_id})
            await db_session.execute(text("DELETE FROM snapshot_data_visualization_info WHERE id = :source_dv_id OR id = :target_dv_id"), {"source_dv_id": source_dv_id, "target_dv_id": target_dv_id})
            for model, ident in [
                (VisualizationOuterParamsTargetViewInfo, f"live-target-{source_dv_id}"),
                (VisualizationOuterParamsInfo, f"live-info-{source_dv_id}"),
                (VisualizationOuterParams, f"live-params-{source_dv_id}"),
                (CoreChartView, aux_target_view_id),
                (CoreChartView, target_view_id),
                (CoreChartView, source_view_id),
                (DataVisualizationInfo, target_dv_id),
                (DataVisualizationInfo, source_dv_id),
                (CoreDatasetTableField, target_field_id_2),
                (CoreDatasetTableField, target_field_id),
                (CoreDatasetTableField, source_field_id),
                (CoreDatasetGroup, dataset_group_id),
            ]:
                entity = await db_session.get(model, ident)
                if entity is not None:
                    await db_session.delete(entity)
            await db_session.commit()
        except Exception:
            try:
                await db_session.rollback()
            except Exception:
                pass


async def test_link_jump_update_query_and_remove_round_trip(db_session: AsyncSession, interaction_seed: dict[str, int]) -> None:
    service = LinkJumpService(db_session)
    await service.update_jump_set(
        VisualizationLinkJumpDTO(
            source_dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            checked=True,
            link_jump_info_array=[
                LinkJumpInfoDTO(
                    link_type="inner",
                    jump_type="_blank",
                    window_size="middle",
                    target_dv_id=interaction_seed["target_dv_id"],
                    source_field_id=interaction_seed["source_field_id"],
                    checked=True,
                    attach_params=True,
                    target_view_info_list=[
                        LinkJumpTargetViewInfo(
                            source_field_active_id=interaction_seed["source_field_id"],
                            target_view_id=str(interaction_seed["target_view_id"]),
                            target_field_id=str(interaction_seed["target_field_id"]),
                            target_type="view",
                        )
                    ],
                )
            ],
        )
    )

    queried = await service.query_with_view_id(
        interaction_seed["source_dv_id"],
        interaction_seed["source_view_id"],
        uid=7,
        resource_table="core",
    )
    assert queried is not None
    assert queried.checked is True
    assert queried.link_jump_info_array is not None
    assert queried.link_jump_info_array[0].target_view_info_list is not None
    assert queried.link_jump_info_array[0].target_view_info_list[0].target_view_id == str(interaction_seed["target_view_id"])

    await service.remove_jump_set(VisualizationLinkJumpDTO(source_dv_id=interaction_seed["source_dv_id"], source_view_id=interaction_seed["source_view_id"]))
    removed = await service.query_with_view_id(
        interaction_seed["source_dv_id"],
        interaction_seed["source_view_id"],
        uid=7,
        resource_table="core",
    )
    assert removed is not None
    assert removed.id is not None
    assert removed.link_jump_info_array is not None


async def test_link_jump_query_visualization_jump_info_filters_to_checked_entries(db_session: AsyncSession, interaction_seed: dict[str, int]) -> None:
    service = LinkJumpService(db_session)
    await service.update_jump_set(
        VisualizationLinkJumpDTO(
            source_dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            checked=True,
            link_jump_info_array=[
                LinkJumpInfoDTO(
                    link_type="inner",
                    target_dv_id=interaction_seed["target_dv_id"],
                    source_field_id=interaction_seed["source_field_id"],
                    checked=True,
                ),
                LinkJumpInfoDTO(
                    link_type="outer",
                    content="https://example.test",
                    source_field_id=interaction_seed["target_field_id_2"],
                    checked=False,
                ),
            ],
        )
    )

    payload = await service.query_visualization_jump_info(interaction_seed["source_dv_id"], uid=7, resource_table="core")

    assert payload.base_jump_info_map is not None
    assert list(payload.base_jump_info_map) == [f"{interaction_seed['source_view_id']}#{interaction_seed['source_field_id']}"]


async def test_link_jump_query_target_visualization_jump_info_returns_expected_mapping(db_session: AsyncSession, interaction_seed: dict[str, int]) -> None:
    service = LinkJumpService(db_session)
    await service.update_jump_set(
        VisualizationLinkJumpDTO(
            source_dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            checked=True,
            link_jump_info_array=[
                LinkJumpInfoDTO(
                    link_type="inner",
                    target_dv_id=interaction_seed["target_dv_id"],
                    source_field_id=interaction_seed["source_field_id"],
                    checked=True,
                    target_view_info_list=[
                        LinkJumpTargetViewInfo(
                            source_field_active_id=interaction_seed["source_field_id"],
                            target_view_id=str(interaction_seed["target_view_id"]),
                            target_field_id=str(interaction_seed["target_field_id"]),
                            target_type="view",
                        )
                    ],
                )
            ],
        )
    )

    payload = await service.query_target_visualization_jump_info(
        LinkJumpBaseRequest(
            source_dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            target_dv_id=interaction_seed["target_dv_id"],
            source_field_id=interaction_seed["source_field_id"],
            resource_table="core",
        )
    )
    empty_payload = await service.query_target_visualization_jump_info(LinkJumpBaseRequest())

    assert payload.base_jump_info_visualization_map == {
        f"{interaction_seed['source_view_id']}#{interaction_seed['source_field_id']}#{interaction_seed['source_field_id']}": [
            f"{interaction_seed['target_view_id']}#{interaction_seed['target_field_id']}"
        ]
    }
    assert empty_payload.base_jump_info_visualization_map == {}


async def test_link_jump_view_table_detail_list_returns_fields_and_outer_params(
    db_session: AsyncSession,
    interaction_seed: dict[str, int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = LinkJumpService(db_session)

    async def _fake_get(_: object, __: object, dv_id: int) -> DataVisualizationInfo:
        return DataVisualizationInfo(**_viz_payload(dv_id, name="source", component_ids=[interaction_seed["source_view_id"]]))

    async def _fake_view_rows(dv_id: int) -> list[dict[str, object]]:
        return [{
            "id": interaction_seed["source_view_id"],
            "title": "Source Chart",
            "type": "bar",
            "dv_id": dv_id,
            "field_id": interaction_seed["source_field_id"],
            "origin_name": "region",
            "field_name": "Region",
            "field_type": "VARCHAR",
            "de_type": 0,
        }]

    async def _fake_out_params(_: int) -> list[dict[str, object]]:
        return [{"id": "op-1", "name": "tenant", "title": "tenant", "type": "outerParams"}]

    monkeypatch.setattr(service.session, "get", _fake_get.__get__(service.session, type(service.session)))
    monkeypatch.setattr(service.repo, "get_view_table_details", _fake_view_rows)
    monkeypatch.setattr(service.repo, "query_out_params_target_with_dv_id", _fake_out_params)

    payload = await service.view_table_detail_list(interaction_seed["source_dv_id"])

    assert payload.component_data != "[]"
    assert payload.result
    assert payload.result[0].table_fields
    assert payload.out_params_jump_info[0].name == "tenant"


async def test_link_jump_update_jump_set_active_updates_snapshot_flag(db_session: AsyncSession, interaction_seed: dict[str, int]) -> None:
    service = LinkJumpService(db_session)
    await service.update_jump_set(
        VisualizationLinkJumpDTO(
            source_dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            checked=True,
            link_jump_info_array=[LinkJumpInfoDTO(link_type="outer", content="https://example.test", source_field_id=interaction_seed["source_field_id"], checked=True)],
        )
    )

    payload = await service.update_jump_set_active(
        LinkJumpBaseRequest(
            source_dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            active_status=False,
        ),
        uid=7,
    )
    updated_flag = await db_session.execute(text("SELECT jump_active FROM snapshot_core_chart_view WHERE id = :id"), {"id": interaction_seed["source_view_id"]})

    assert payload.base_jump_info_map is None or payload.base_jump_info_map == {}
    assert updated_flag.scalar_one() is False


async def test_link_jump_update_jump_set_requires_source_ids(db_session: AsyncSession) -> None:
    with pytest.raises(ValueError, match="sourceDvId and sourceViewId are required"):
        await LinkJumpService(db_session).update_jump_set(VisualizationLinkJumpDTO())


async def test_outer_params_update_and_query_snapshot_round_trip(db_session: AsyncSession, interaction_seed: dict[str, int]) -> None:
    service = OuterParamsService(db_session)
    dto = VisualizationOuterParamsDTO(
        visualization_id=str(interaction_seed["source_dv_id"]),
        checked=True,
        outer_params_info_array=[
            OuterParamsInfoDTO(
                param_name="tenant",
                checked=True,
                required=True,
                default_value="north",
                enabled_default=True,
                target_view_info_list=[
                    OuterParamsTargetViewInfoDTO(
                        target_view_id=str(interaction_seed["target_view_id"]),
                        target_ds_id=str(interaction_seed["dataset_group_id"]),
                        target_field_id=str(interaction_seed["target_field_id"]),
                        match_mode="strict",
                    )
                ],
            )
        ],
    )

    await service.update_outer_params_set(dto)
    queried = await service.query_with_visualization_id(str(interaction_seed["source_dv_id"]))

    assert queried is not None
    assert queried.checked is True
    assert queried.outer_params_info_array is not None
    assert queried.outer_params_info_array[0].param_name == "tenant"
    assert queried.outer_params_info_array[0].target_view_info_list is not None
    assert queried.outer_params_info_array[0].target_view_info_list[0].match_mode == "strict"


async def test_outer_params_get_outer_params_info_returns_live_mapping(db_session: AsyncSession, interaction_seed: dict[str, int]) -> None:
    payload = await OuterParamsService(db_session).get_outer_params_info(str(interaction_seed["source_dv_id"]))

    assert payload.outer_params_info_map == {"tenant": [f"{interaction_seed['target_view_id']}#{interaction_seed['target_field_id']}#strict"]}
    assert payload.outer_params_info_base_map is not None
    assert payload.outer_params_info_base_map["tenant"].required is True


async def test_outer_params_query_ds_with_visualization_id_includes_fields_and_views(
    db_session: AsyncSession,
    interaction_seed: dict[str, int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = OuterParamsService(db_session)

    async def _fake_ds_rows(_: str) -> list[dict[str, object]]:
        return [{"id": interaction_seed["dataset_group_id"], "name": "group", "visualizationId": interaction_seed["source_dv_id"]}]

    async def _fake_fields(_: int) -> list[dict[str, object]]:
        return [{"id": interaction_seed["source_field_id"], "origin_name": "region"}]

    async def _fake_views(_: int, __: str) -> list[dict[str, object]]:
        return [{"chartId": interaction_seed["source_view_id"], "chartName": "Source Chart", "chartType": "bar"}]

    monkeypatch.setattr(service.repo, "query_ds_with_visualization_id", _fake_ds_rows)
    monkeypatch.setattr(service.repo, "query_ds_fields", _fake_fields)
    monkeypatch.setattr(service.repo, "query_ds_views", _fake_views)

    payload = await service.query_ds_with_visualization_id(str(interaction_seed["source_dv_id"]))

    assert payload
    assert payload[0]["id"] == interaction_seed["dataset_group_id"]
    assert payload[0]["datasetFields"]
    assert payload[0]["datasetViews"]


async def test_outer_params_update_requires_visualization_id(db_session: AsyncSession) -> None:
    with pytest.raises(ValueError, match="visualizationId cannot be null"):
        await OuterParamsService(db_session).update_outer_params_set(VisualizationOuterParamsDTO())


async def test_linkage_save_and_gather_map_and_list(db_session: AsyncSession, interaction_seed: dict[str, int]) -> None:
    service = LinkageService(db_session)
    await service.save_linkage(
        LinkageSaveRequest(
            dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            linkage_info=[
                VisualizationLinkageDTO(
                    target_view_id=interaction_seed["target_view_id"],
                    linkage_active=True,
                    linkage_fields=[LinkageFieldVO(source_field=interaction_seed["source_field_id"], target_field=interaction_seed["target_field_id"])],
                ),
                VisualizationLinkageDTO(
                    target_view_id=interaction_seed["source_view_id"],
                    linkage_active=True,
                    linkage_fields=[LinkageFieldVO(source_field=interaction_seed["source_field_id"], target_field=interaction_seed["target_field_id_2"])],
                ),
            ],
        )
    )

    gather_map = await service.get_view_linkage_gather(
        LinkageGatherRequest(
            dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            target_view_ids=[str(interaction_seed["target_view_id"]), str(interaction_seed["source_view_id"])],
            resource_table="snapshot",
        )
    )
    gather_list = await service.get_view_linkage_gather_array(
        LinkageGatherRequest(
            dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            target_view_ids=[str(interaction_seed["target_view_id"])],
            resource_table="snapshot",
        )
    )

    assert str(interaction_seed["target_view_id"]) in gather_map
    assert gather_map[str(interaction_seed["target_view_id"])].linkage_fields[0].target_field == interaction_seed["target_field_id"]
    assert len(gather_list) == 1


async def test_linkage_get_visualization_all_linkage_info_and_toggle_active(db_session: AsyncSession, interaction_seed: dict[str, int]) -> None:
    service = LinkageService(db_session)
    await service.save_linkage(
        LinkageSaveRequest(
            dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            linkage_info=[
                VisualizationLinkageDTO(
                    target_view_id=interaction_seed["target_view_id"],
                    linkage_active=True,
                    linkage_fields=[LinkageFieldVO(source_field=interaction_seed["source_field_id"], target_field=interaction_seed["target_field_id"])],
                )
            ],
        )
    )

    payload = await service.get_visualization_all_linkage_info(interaction_seed["source_dv_id"], "snapshot")
    toggled = await service.update_linkage_active(
        LinkageUpdateActiveRequest(
            dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            active_status=False,
        )
    )

    assert payload == {f"{interaction_seed['source_view_id']}#{interaction_seed['source_field_id']}": [f"{interaction_seed['target_view_id']}#{interaction_seed['target_field_id']}"]}
    assert toggled == {}


async def test_linkage_remove_clears_saved_configuration(db_session: AsyncSession, interaction_seed: dict[str, int]) -> None:
    service = LinkageService(db_session)
    await service.save_linkage(
        LinkageSaveRequest(
            dv_id=interaction_seed["source_dv_id"],
            source_view_id=interaction_seed["source_view_id"],
            linkage_info=[VisualizationLinkageDTO(target_view_id=interaction_seed["target_view_id"], linkage_active=False)],
        )
    )
    await service.remove_linkage(LinkageRemoveRequest(dv_id=interaction_seed["source_dv_id"], source_view_id=interaction_seed["source_view_id"]))
    rows = await db_session.execute(text("SELECT COUNT(*) FROM snapshot_visualization_linkage WHERE dv_id = :dv_id AND source_view_id = :source_view_id"), {"dv_id": interaction_seed["source_dv_id"], "source_view_id": interaction_seed["source_view_id"]})

    assert rows.scalar_one() == 0
