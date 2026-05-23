from __future__ import annotations

import base64
from unittest.mock import AsyncMock
from types import SimpleNamespace
from typing import Any, cast

import pytest

from app.models.datasource import CoreDatasource  # pyright: ignore[reportImplicitRelativeImport]
from app.models.dataset import CoreDatasetGroup, CoreDatasetTable, CoreDatasetTableField  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.dataset import DatasetEnumValueRequest, DatasetGroupCreate, DatasetGroupUpdate, DatasetPreviewDataRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.datasource import DatasourceFieldResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_service import DatasetService, _build_tree, _compute_level  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.datasource_repo import DatasourceRepository  # pyright: ignore[reportImplicitRelativeImport]

_de_type_for_column = DatasetService._de_type_for_column
_merge_source_info = DatasetService._merge_source_info
_normalize_info = DatasetService._normalize_info


def make_group(**overrides: object) -> SimpleNamespace:
    payload: dict[str, object] = {
        "id": 1,
        "name": "node",
        "pid": 0,
        "level": 0,
        "node_type": "folder",
        "type": None,
        "mode": None,
        "info": None,
        "create_by": None,
        "create_time": None,
        "qrtz_instance": None,
        "sync_status": None,
        "update_by": None,
        "last_update_time": None,
        "union_sql": None,
        "is_cross": None,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def make_field(**overrides: object) -> SimpleNamespace:
    payload: dict[str, object] = {
        "id": 101,
        "origin_name": "origin_col",
        "name": "display_col",
        "dataease_name": "de_col",
        "field_short_name": "short_col",
        "group_type": "d",
        "type": "VARCHAR",
        "size": 255,
        "de_type": 0,
        "de_extract_type": 1,
        "ext_field": 2,
        "checked": False,
        "column_index": 4,
        "accuracy": 6,
        "date_format": "yyyy-MM-dd",
        "date_format_type": "custom",
        "datasource_id": 202,
        "dataset_table_id": 303,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def make_datasource_field(**overrides: object) -> DatasourceFieldResponse:
    payload: dict[str, object] = {
        "name": "amount",
        "origin_name": "amount",
        "data_type": "VARCHAR",
        "de_type": 0,
        "type": None,
        "nullable": True,
    }
    payload.update(overrides)
    return DatasourceFieldResponse.model_validate(payload)


def make_table(**overrides: object) -> SimpleNamespace:
    payload: dict[str, object] = {
        "id": 303,
        "name": "orders",
        "table_name": "orders",
        "datasource_id": 202,
        "dataset_group_id": 1,
        "type": "db",
        "info": None,
        "sql_variable_details": None,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


class TestComputeLevel:
    def test_returns_zero_for_none_pid(self) -> None:
        assert _compute_level([], None) == 0

    def test_returns_zero_for_zero_pid(self) -> None:
        assert _compute_level([], 0) == 0

    def test_returns_parent_level_plus_one_for_existing_parent(self) -> None:
        groups = cast(list[CoreDatasetGroup], [SimpleNamespace(id=11, level=3)])

        assert _compute_level(groups, 11) == 4

    def test_returns_one_for_nonexistent_parent(self) -> None:
        groups = cast(list[CoreDatasetGroup], [SimpleNamespace(id=11, level=3)])

        assert _compute_level(groups, 99) == 1

    def test_treats_missing_parent_level_as_zero(self) -> None:
        groups = cast(list[CoreDatasetGroup], [SimpleNamespace(id=11, level=None)])

        assert _compute_level(groups, 11) == 1

    def test_supports_nested_three_level_chain(self) -> None:
        groups = cast(list[CoreDatasetGroup], [
            SimpleNamespace(id=1, level=0),
            SimpleNamespace(id=2, level=1),
            SimpleNamespace(id=3, level=2),
        ])

        assert _compute_level(groups, 3) == 3


class TestBuildTree:
    def test_returns_empty_list_for_empty_input(self) -> None:
        assert _build_tree([]) == []

    def test_returns_single_root_node(self) -> None:
        roots = _build_tree(cast(list[CoreDatasetGroup], [make_group(id=1, name="root", pid=0)]))

        assert len(roots) == 1
        assert roots[0].id == 1
        assert roots[0].name == "root"
        assert roots[0].children == []

    def test_nests_child_under_root(self) -> None:
        roots = _build_tree(cast(list[CoreDatasetGroup], [
            make_group(id=1, name="root", pid=0),
            make_group(id=2, name="child", pid=1, level=1),
        ]))

        assert len(roots) == 1
        assert [child.id for child in roots[0].children] == [2]

    def test_supports_nested_grandchildren(self) -> None:
        roots = _build_tree(cast(list[CoreDatasetGroup], [
            make_group(id=1, name="root", pid=0),
            make_group(id=2, name="child", pid=1, level=1),
            make_group(id=3, name="grandchild", pid=2, level=2),
        ]))

        assert roots[0].children[0].children[0].id == 3

    def test_returns_multiple_roots(self) -> None:
        roots = _build_tree(cast(list[CoreDatasetGroup], [
            make_group(id=1, name="root-a", pid=0),
            make_group(id=2, name="root-b", pid=None),
        ]))

        assert [node.id for node in roots] == [1, 2]

    def test_orphaned_child_becomes_root(self) -> None:
        roots = _build_tree(cast(list[CoreDatasetGroup], [make_group(id=2, name="orphan", pid=999, level=1)]))

        assert len(roots) == 1
        assert roots[0].id == 2

    def test_marks_dataset_nodes_as_leaf(self) -> None:
        roots = _build_tree(cast(list[CoreDatasetGroup], [make_group(id=1, node_type="dataset")]))

        assert roots[0].leaf is True

    def test_marks_folder_nodes_as_non_leaf(self) -> None:
        roots = _build_tree(cast(list[CoreDatasetGroup], [make_group(id=1, node_type="folder")]))

        assert roots[0].leaf is False


class TestDeTypeForColumn:
    def test_maps_int_to_numeric_type(self) -> None:
        assert _de_type_for_column("INT") == 1

    def test_maps_bigint_to_numeric_type(self) -> None:
        assert _de_type_for_column("BIGINT") == 1

    def test_maps_numeric_to_numeric_type(self) -> None:
        assert _de_type_for_column("NUMERIC") == 1

    def test_maps_decimal_to_numeric_type(self) -> None:
        assert _de_type_for_column("DECIMAL") == 1

    def test_maps_double_to_numeric_type(self) -> None:
        assert _de_type_for_column("DOUBLE") == 1

    def test_maps_float_to_numeric_type(self) -> None:
        assert _de_type_for_column("FLOAT") == 1

    def test_maps_real_to_numeric_type(self) -> None:
        assert _de_type_for_column("REAL") == 1

    def test_maps_date_to_time_type(self) -> None:
        assert _de_type_for_column("DATE") == 2

    def test_maps_datetime_to_time_type(self) -> None:
        assert _de_type_for_column("DATETIME") == 2

    def test_maps_timestamp_to_time_type(self) -> None:
        assert _de_type_for_column("TIMESTAMP") == 2

    def test_maps_time_to_time_type(self) -> None:
        assert _de_type_for_column("TIME") == 2

    def test_maps_varchar_to_string_type(self) -> None:
        assert _de_type_for_column("VARCHAR") == 0

    def test_maps_text_to_string_type(self) -> None:
        assert _de_type_for_column("TEXT") == 0

    def test_maps_char_to_string_type(self) -> None:
        assert _de_type_for_column("CHAR") == 0

    def test_maps_boolean_to_string_type(self) -> None:
        assert _de_type_for_column("BOOLEAN") == 0

    def test_handles_mixed_case_values(self) -> None:
        assert _de_type_for_column("Int") == 1
        assert _de_type_for_column("varchar") == 0
        assert _de_type_for_column("DateTime") == 2


class TestNormalizeInfo:
    def test_returns_none_unchanged(self) -> None:
        assert _normalize_info(None) is None

    def test_returns_dict_unchanged(self) -> None:
        info = {"a": 1}

        assert _normalize_info(info) is info

    def test_returns_list_unchanged(self) -> None:
        info = [1, 2, 3]

        assert _normalize_info(info) is info

    def test_parses_valid_json_string(self) -> None:
        assert _normalize_info('{"a": 1, "b": [2]}') == {"a": 1, "b": [2]}

    def test_returns_invalid_json_string_as_is(self) -> None:
        assert _normalize_info("{not-json") == "{not-json"

    def test_returns_integer_unchanged(self) -> None:
        assert _normalize_info(123) == 123


class TestMergeSourceInfo:
    def test_returns_original_info_when_both_values_are_none(self) -> None:
        info = {"a": 1}

        assert _merge_source_info(info, None, None) is info

    def test_adds_only_datasource_id(self) -> None:
        assert _merge_source_info({}, 7, None) == {"datasourceId": 7, "datasource_id": 7}

    def test_adds_only_table_keys(self) -> None:
        assert _merge_source_info({}, None, "orders") == {
            "tableName": "orders",
            "table_name": "orders",
            "table": "orders",
        }

    def test_adds_all_keys_when_both_values_are_set(self) -> None:
        assert _merge_source_info({}, 7, "orders") == {
            "datasourceId": 7,
            "datasource_id": 7,
            "tableName": "orders",
            "table_name": "orders",
            "table": "orders",
        }

    def test_creates_new_dict_when_info_is_none(self) -> None:
        assert _merge_source_info(None, 7, None) == {"datasourceId": 7, "datasource_id": 7}

    def test_merges_into_existing_dict(self) -> None:
        info = {"keep": True}

        assert _merge_source_info(info, 7, "orders") == {
            "keep": True,
            "datasourceId": 7,
            "datasource_id": 7,
            "tableName": "orders",
            "table_name": "orders",
            "table": "orders",
        }

    def test_ignores_empty_table_name(self) -> None:
        assert _merge_source_info({}, 7, "") == {"datasourceId": 7, "datasource_id": 7}

    def test_strips_table_name_before_merging(self) -> None:
        assert _merge_source_info({}, None, "  orders  ") == {
            "tableName": "orders",
            "table_name": "orders",
            "table": "orders",
        }


class TestResolveSourcePayload:
    def test_prefers_explicit_payload_values_over_union(self) -> None:
        datasource_id, table_name, info = DatasetService._resolve_source_payload(
            {"keep": True},
            9,
            "explicit_orders",
            [{
                "currentDs": {
                    "datasourceId": 7,
                    "tableName": "union_orders",
                    "info": {"sql": "SELECT 1"},
                }
            }],
        )

        assert datasource_id == 9
        assert table_name == "explicit_orders"
        assert info == {"keep": True}

    def test_falls_back_to_union_source_values(self) -> None:
        datasource_id, table_name, info = DatasetService._resolve_source_payload(
            None,
            None,
            None,
            [{
                "currentDs": {
                    "datasourceId": "7",
                    "tableName": "orders",
                    "info": {"sql": "SELECT * FROM orders"},
                }
            }],
        )

        assert datasource_id == 7
        assert table_name == "orders"
        assert info == {"sql": "SELECT * FROM orders"}

    def test_keeps_existing_info_when_union_only_supplies_source_keys(self) -> None:
        datasource_id, table_name, info = DatasetService._resolve_source_payload(
            {"sql": "SELECT * FROM custom_orders"},
            None,
            None,
            [{
                "currentDs": {
                    "datasourceId": 7,
                    "tableName": "orders",
                    "info": {"sql": "SELECT * FROM ignored"},
                }
            }],
        )

        assert datasource_id == 7
        assert table_name == "orders"
        assert info == {"sql": "SELECT * FROM custom_orders"}


class TestCreateAndSaveUnionFallback:
    @staticmethod
    def _build_service() -> DatasetService:
        group_repo = SimpleNamespace(
            list_all_ordered=AsyncMock(return_value=[]),
            create=AsyncMock(return_value=SimpleNamespace(id=1001, name="union-dataset", pid=None, level=0, node_type="dataset", type=None, mode=None, info=None, create_by="7", create_time=1, qrtz_instance=None, sync_status=None, update_by="7", last_update_time=1, union_sql=None, is_cross=None)),
            update=AsyncMock(return_value=SimpleNamespace(id=1002, name="union-dataset-updated", pid=None, level=0, node_type="dataset", type=None, mode=None, info=None, create_by="7", create_time=1, qrtz_instance=None, sync_status=None, update_by="7", last_update_time=2, union_sql=None, is_cross=None)),
        )
        table_repo = SimpleNamespace()
        field_repo = SimpleNamespace(delete_by_group=AsyncMock())
        service = DatasetService(
            session=AsyncMock(),
            group_repo=cast(Any, group_repo),
            table_repo=cast(Any, table_repo),
            field_repo=cast(Any, field_repo),
        )
        service._sync_dataset_source = AsyncMock()  # type: ignore[method-assign]
        service._save_fields_for_group = AsyncMock()  # type: ignore[method-assign]
        service._get_group = AsyncMock(return_value=SimpleNamespace(id=1002, name="existing", pid=0, level=0, node_type="dataset", type=None, mode=None, info=None, create_by="7", create_time=1, qrtz_instance=None, sync_status=None, update_by="7", last_update_time=1, union_sql=None, is_cross=None))  # type: ignore[method-assign]
        return service

    @staticmethod
    def _token_user() -> TokenUser:
        return TokenUser(user_id=7, oid=9)

    async def test_create_uses_union_source_when_top_level_source_absent(self) -> None:
        service = self._build_service()
        payload = DatasetGroupCreate.model_validate({
            "name": "union dataset",
            "pid": 0,
            "nodeType": "dataset",
            "union": [{
                "currentDs": {
                    "datasourceId": 88,
                    "tableName": "orders",
                    "info": {"sql": "SELECT * FROM orders"},
                }
            }],
        })

        await service.create(payload, self._token_user())

        create_info = cast(Any, service.group_repo.create).await_args.args[0]["info"]
        assert create_info == {
            "sql": "SELECT * FROM orders",
            "datasourceId": 88,
            "datasource_id": 88,
            "tableName": "orders",
            "table_name": "orders",
            "table": "orders",
            "union": [{
                "currentDs": {
                    "datasourceId": 88,
                    "tableName": "orders",
                    "info": {"sql": "SELECT * FROM orders"},
                }
            }],
        }
        cast(Any, service._sync_dataset_source).assert_awaited_once_with(1001, "union dataset", create_info)

    async def test_create_remaps_browser_field_dataset_table_ids_from_synced_table(self) -> None:
        service = self._build_service()
        dataset_table = SimpleNamespace(id=555, datasource_id=88)
        service._sync_dataset_source = AsyncMock(return_value=dataset_table)  # type: ignore[method-assign]
        payload = DatasetGroupCreate.model_validate({
            "name": "union dataset",
            "pid": 0,
            "nodeType": "dataset",
            "union": [{
                "currentDs": {
                    "datasourceId": "88",
                    "tableName": "orders",
                    "type": "db",
                    "info": '{"table":"orders","sql":""}',
                }
            }],
            "allFields": [{
                "originName": "order_id",
                "name": "order_id",
                "datasetTableId": "frontend-temp-id",
                "datasourceId": "frontend-datasource",
            }],
        })

        await service.create(payload, self._token_user())

        cast(Any, service.field_repo.delete_by_group).assert_awaited_once_with(1001)
        saved_fields = cast(Any, service._save_fields_for_group).await_args.args[1]
        assert saved_fields == [{
            "originName": "order_id",
            "name": "order_id",
            "datasetTableId": 555,
            "dataset_table_id": 555,
            "datasourceId": 88,
            "datasource_id": 88,
        }]

    async def test_save_uses_union_source_when_top_level_source_absent(self) -> None:
        service = self._build_service()
        payload = DatasetGroupUpdate.model_validate({
            "id": 1002,
            "union": [{
                "currentDs": {
                    "datasourceId": 66,
                    "tableName": "line_items",
                    "info": {"sql": "SELECT * FROM line_items"},
                }
            }],
        })

        await service.save(payload, self._token_user())

        update_info = cast(Any, service.group_repo.update).await_args.args[1]["info"]
        assert update_info == {
            "sql": "SELECT * FROM line_items",
            "datasourceId": 66,
            "datasource_id": 66,
            "tableName": "line_items",
            "table_name": "line_items",
            "table": "line_items",
            "union": [{
                "currentDs": {
                    "datasourceId": 66,
                    "tableName": "line_items",
                    "info": {"sql": "SELECT * FROM line_items"},
                }
            }],
        }
        cast(Any, service._sync_dataset_source).assert_awaited_once_with(1002, "union-dataset-updated", update_info)

    async def test_save_remaps_browser_field_dataset_table_ids_from_synced_table(self) -> None:
        service = self._build_service()
        dataset_table = SimpleNamespace(id=777, datasource_id=66)
        service._sync_dataset_source = AsyncMock(return_value=dataset_table)  # type: ignore[method-assign]
        payload = DatasetGroupUpdate.model_validate({
            "id": 1002,
            "union": [{
                "currentDs": {
                    "datasourceId": "66",
                    "tableName": "line_items",
                    "type": "db",
                    "info": '{"table":"line_items","sql":""}',
                }
            }],
            "allFields": [{
                "originName": "line_id",
                "name": "line_id",
                "datasetTableId": "frontend-temp-id",
            }],
        })

        await service.save(payload, self._token_user())

        cast(Any, service.field_repo.delete_by_group).assert_awaited_once_with(1002)
        saved_fields = cast(Any, service._save_fields_for_group).await_args.args[1]
        assert saved_fields == [{
            "originName": "line_id",
            "name": "line_id",
            "datasetTableId": 777,
            "dataset_table_id": 777,
            "datasourceId": 66,
            "datasource_id": 66,
        }]


class TestSyncDatasetSource:
    async def test_skips_field_reload_for_sql_backed_info(self) -> None:
        service = DatasetService(
            session=AsyncMock(),
            group_repo=cast(Any, SimpleNamespace()),
            table_repo=cast(Any, SimpleNamespace()),
            field_repo=cast(Any, SimpleNamespace(delete_by_group=AsyncMock())),
        )
        dataset_table = SimpleNamespace(id=321, datasource_id=88)
        service._get_or_create_dataset_table = AsyncMock(return_value=dataset_table)  # type: ignore[method-assign]
        service._load_datasource_fields = AsyncMock()  # type: ignore[method-assign]
        service._save_fields_for_group = AsyncMock()  # type: ignore[method-assign]

        result = await service._sync_dataset_source(1001, "sql dataset", '{"sql":"SELECT * FROM orders","table":"orders","datasourceId":88}')

        assert result is dataset_table
        cast(Any, service.field_repo.delete_by_group).assert_not_awaited()
        cast(Any, service._load_datasource_fields).assert_not_awaited()
        cast(Any, service._save_fields_for_group).assert_not_awaited()


class TestBuildSqlFromUnion:
    def test_accepts_browser_db_node_type(self) -> None:
        service = DatasetService(
            session=AsyncMock(),
            group_repo=cast(Any, SimpleNamespace()),
            table_repo=cast(Any, SimpleNamespace()),
            field_repo=cast(Any, SimpleNamespace()),
        )

        sql = service._build_sql_from_union([{
            "currentDs": {
                "type": "db",
                "tableName": "orders",
            }
        }])

        assert sql == 'SELECT * FROM "orders"'


class TestFieldToStoragePayload:
    def test_maps_primary_name_fields(self) -> None:
        payload = DatasetService._field_to_storage_payload(make_datasource_field(name="amount", data_type="INT"), 8, 9)

        assert payload["originName"] == "amount"
        assert payload["name"] == "amount"
        assert payload["dataeaseName"] == "amount"
        assert payload["fieldShortName"] == "amount"

    def test_sets_default_group_type_ext_field_and_checked(self) -> None:
        payload = DatasetService._field_to_storage_payload(make_datasource_field(name="amount", data_type="INT"), 8, 9)

        assert payload["groupType"] == "d"
        assert payload["extField"] == 0
        assert payload["checked"] is True

    def test_uses_de_type_for_column_result(self, monkeypatch) -> None:
        seen: list[str] = []
        monkeypatch.setattr(
            DatasetService,
            "_de_type_for_column",
            staticmethod(lambda data_type: seen.append(data_type) or 9),
        )

        payload = DatasetService._field_to_storage_payload(make_datasource_field(name="amount", data_type="custom"), 8, 9)

        assert seen == ["custom"]
        assert payload["deType"] == 9

    def test_defaults_data_type_to_varchar_when_missing(self) -> None:
        payload = DatasetService._field_to_storage_payload(
            cast(DatasourceFieldResponse, cast(object, SimpleNamespace(name="amount", data_type=None))), 8, 9
        )

        assert payload["type"] == "varchar"
        assert payload["deType"] == 0

    def test_includes_datasource_and_dataset_table_ids(self) -> None:
        payload = DatasetService._field_to_storage_payload(make_datasource_field(name="amount", data_type="DATE"), 8, 9)

        assert payload["datasourceId"] == 8
        assert payload["datasetTableId"] == 9


class TestFieldToDict:
    def test_serializes_all_expected_keys(self) -> None:
        payload = DatasetService._field_to_dict(make_field())

        assert payload == {
            "id": "101",
            "originName": "origin_col",
            "name": "display_col",
            "dataeaseName": "de_col",
            "fieldShortName": "short_col",
            "groupType": "d",
            "type": "VARCHAR",
            "size": 255,
            "deType": 0,
            "deExtractType": 1,
            "extField": 2,
            "checked": False,
            "columnIndex": 4,
            "accuracy": 6,
            "dateFormat": "yyyy-MM-dd",
            "dateFormatType": "custom",
            "groupList": None,
            "otherGroup": None,
            "datasourceId": "202",
            "datasetTableId": "303",
        }

    def test_uses_sid_for_identifier_fields(self) -> None:
        payload = DatasetService._field_to_dict(make_field(id=999, datasource_id=888, dataset_table_id=777))

        assert payload["id"] == "999"
        assert payload["datasourceId"] == "888"
        assert payload["datasetTableId"] == "777"

    def test_preserves_none_for_missing_identifiers(self) -> None:
        payload = DatasetService._field_to_dict(make_field(id=None, datasource_id=None, dataset_table_id=None))

        assert payload["id"] is None
        assert payload["datasourceId"] is None
        assert payload["datasetTableId"] is None

    def test_serializes_missing_optional_values_as_none(self) -> None:
        payload = DatasetService._field_to_dict(make_field(name=None, date_format=None, accuracy=None))

        assert payload["name"] is None
        assert payload["dateFormat"] is None
        assert payload["accuracy"] is None


class TestFieldToPreviewField:
    def test_returns_expected_preview_keys(self) -> None:
        payload = DatasetService._field_to_preview_field(make_field())

        assert payload == {
            "name": "display_col",
            "dataeaseName": "de_col",
            "originName": "origin_col",
            "type": "VARCHAR",
            "deType": 0,
            "groupType": "d",
        }

    def test_falls_back_to_origin_name_when_name_is_none(self) -> None:
        payload = DatasetService._field_to_preview_field(make_field(name=None))

        assert payload["name"] == "origin_col"

    def test_keeps_name_when_present(self) -> None:
        payload = DatasetService._field_to_preview_field(make_field(name="custom_name"))

        assert payload["name"] == "custom_name"

    def test_preserves_none_values_for_other_fields(self) -> None:
        payload = DatasetService._field_to_preview_field(
            make_field(dataease_name=None, type=None, de_type=None, group_type=None)
        )

        assert payload["dataeaseName"] is None
        assert payload["type"] is None
        assert payload["deType"] is None
        assert payload["groupType"] is None


class TestUnionPersistenceHelpers:
    def test_attach_union_to_info_merges_into_existing_dict(self) -> None:
        info = {"datasourceId": 88, "tableName": "orders"}
        union = [{"currentDs": {"datasourceId": 88, "tableName": "orders"}}]

        payload = DatasetService._attach_union_to_info(info, union)

        assert payload == {
            "datasourceId": 88,
            "tableName": "orders",
            "union": union,
        }

    def test_attach_union_to_info_wraps_non_dict_payload(self) -> None:
        union = [{"currentDs": {"datasourceId": 88, "tableName": "orders"}}]

        payload = DatasetService._attach_union_to_info(None, union)

        assert payload == {"union": union}

    def test_build_detail_union_prefers_stored_union(self) -> None:
        service = DatasetService(
            session=AsyncMock(),
            group_repo=cast(Any, SimpleNamespace()),
            table_repo=cast(Any, SimpleNamespace()),
            field_repo=cast(Any, SimpleNamespace()),
        )
        stored_union = [{"currentDs": {"datasourceId": "88", "tableName": "orders"}, "childrenDs": []}]

        payload = service._build_detail_union(
            cast(CoreDatasetGroup, cast(object, make_group(info={"union": stored_union}))),
            cast(list[CoreDatasetTable], []),
            [],
        )

        assert payload == stored_union

    def test_build_detail_union_falls_back_to_dataset_tables(self) -> None:
        service = DatasetService(
            session=AsyncMock(),
            group_repo=cast(Any, SimpleNamespace()),
            table_repo=cast(Any, SimpleNamespace()),
            field_repo=cast(Any, SimpleNamespace()),
        )

        payload = cast(list[dict[str, Any]], service._build_detail_union(
            cast(CoreDatasetGroup, cast(object, make_group(info={"datasourceId": 202, "tableName": "orders"}))),
            cast(list[CoreDatasetTable], [make_table()]),
            cast(list[CoreDatasetTableField], [make_field(dataset_table_id=303, datasource_id=202, origin_name="id", name="id")]),
        ))

        assert payload[0]["currentDs"]["datasourceId"] == "202"
        assert payload[0]["currentDs"]["tableName"] == "orders"
        assert payload[0]["currentDsFields"][0]["originName"] == "id"


class TestPreviewDataForFileDatasources:
    @staticmethod
    def _build_service(field_repo: object) -> DatasetService:
        service = DatasetService(
            session=AsyncMock(),
            group_repo=cast(Any, SimpleNamespace()),
            table_repo=cast(Any, SimpleNamespace(list_by_group=AsyncMock(return_value=[]))),
            field_repo=cast(Any, field_repo),
        )
        service._get_group = AsyncMock(return_value=make_group(  # type: ignore[method-assign]
            id=321,
            node_type="dataset",
            info={"datasourceId": 88, "tableName": "orders"},
        ))
        return service

    @staticmethod
    def _fields() -> list[SimpleNamespace]:
        return [
            make_field(id=1, origin_name="id", name="id", dataease_name="id", type="LONG", de_type=2),
            make_field(id=2, origin_name="name", name="name", dataease_name="name", type="TEXT", de_type=0),
        ]

    @pytest.mark.asyncio
    async def test_preview_data_returns_saved_excel_rows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        field_repo = SimpleNamespace(list_checked_by_group_no_chart_filter=AsyncMock(return_value=self._fields()))
        service = self._build_service(field_repo)

        datasource = CoreDatasource(
            id=88,
            name="orders-file",
            type="Excel",
            pid=None,
            edit_type=None,
            configuration=[{
                "tableName": "orders",
                "deTableName": "orders",
                "fields": [
                    {"originName": "id", "name": "id", "fieldType": "LONG", "deType": 2},
                    {"originName": "name", "name": "name", "fieldType": "TEXT", "deType": 0},
                ],
                "jsonArray": [
                    {"id": 1, "name": "alice"},
                    {"id": 2, "name": "bob"},
                    {"id": 3, "name": "carol"},
                ],
            }],
            description=None,
            create_time=1,
            update_time=2,
            update_by=7,
            create_by="7",
            status="Success",
            qrtz_instance=None,
            task_status="WaitingForExecution",
            enable_data_fill=False,
        )
        monkeypatch.setattr(DatasourceRepository, "get_by_id", AsyncMock(return_value=datasource))

        result = await service.preview_data(DatasetPreviewDataRequest(dataset_group_id=321, limit=2, offset=1))

        assert [field["originName"] for field in cast(list[dict[str, object]], result["allFields"])] == ["id", "name"]
        payload = cast(dict[str, object], result["data"])
        assert payload["fields"] == [
            {"name": "id", "originName": "id", "deType": 2, "fieldType": "LONG"},
            {"name": "name", "originName": "name", "deType": 0, "fieldType": "TEXT"},
        ]
        assert payload["data"] == [{"id": 2, "name": "bob"}, {"id": 3, "name": "carol"}]
        assert payload["total"] == 3

    @pytest.mark.asyncio
    async def test_preview_data_reparses_saved_csv_rows_when_json_array_is_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        field_repo = SimpleNamespace(list_checked_by_group_no_chart_filter=AsyncMock(return_value=self._fields()))
        service = self._build_service(field_repo)

        raw_csv = base64.b64encode(b"id,name\n1,alice\n2,bob\n").decode()
        datasource = CoreDatasource(
            id=88,
            name="orders-remote-file",
            type="ExcelRemote",
            pid=None,
            edit_type=None,
            configuration={
                "sheets": [{
                    "tableName": "orders",
                    "deTableName": "orders",
                    "fields": [
                        {"originName": "id", "name": "id", "fieldType": "LONG", "deType": 2},
                        {"originName": "name", "name": "name", "fieldType": "TEXT", "deType": 0},
                    ],
                    "jsonArray": [],
                    "_rawFileBase64": raw_csv,
                }]
            },
            description=None,
            create_time=1,
            update_time=2,
            update_by=7,
            create_by="7",
            status="Success",
            qrtz_instance=None,
            task_status="WaitingForExecution",
            enable_data_fill=False,
        )
        monkeypatch.setattr(DatasourceRepository, "get_by_id", AsyncMock(return_value=datasource))

        result = await service.preview_data(DatasetPreviewDataRequest(dataset_group_id=321, limit=10, offset=0))

        payload = cast(dict[str, object], result["data"])
        assert payload["data"] == [{"id": "1", "name": "alice"}, {"id": "2", "name": "bob"}]
        assert payload["total"] == 2

    @pytest.mark.asyncio
    async def test_get_dataset_preview_uses_file_preview_for_saved_excel_dataset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        field_repo = SimpleNamespace(
            list_by_group=AsyncMock(return_value=self._fields()),
            list_checked_by_group_no_chart_filter=AsyncMock(return_value=self._fields()),
        )
        service = self._build_service(field_repo)
        service._get_group = AsyncMock(return_value=make_group(  # type: ignore[method-assign]
            id=321,
            name="产品数据集",
            node_type="dataset",
            info={"datasourceId": 88, "tableName": "数据1"},
        ))
        service.table_repo = cast(Any, SimpleNamespace(list_by_group=AsyncMock(return_value=[make_table(
            id=303,
            name="产品数据集",
            table_name="数据1",
            datasource_id=88,
            type="db",
        )])))

        datasource = CoreDatasource(
            id=88,
            name="orders-file",
            type="Excel",
            pid=None,
            edit_type=None,
            configuration=[{
                "tableName": "数据1",
                "deTableName": "excel_data_1",
                "fields": [
                    {"originName": "订单号", "name": "订单号", "fieldType": "DOUBLE", "deType": 3},
                    {"originName": "客户名称", "name": "客户名称", "fieldType": "TEXT", "deType": 0},
                ],
                "jsonArray": [
                    {"订单号": 1, "客户名称": "alice"},
                    {"订单号": 2, "客户名称": "bob"},
                ],
            }],
            description=None,
            create_time=1,
            update_time=2,
            update_by=7,
            create_by="7",
            status="Success",
            qrtz_instance=None,
            task_status="WaitingForExecution",
            enable_data_fill=False,
        )
        monkeypatch.setattr(DatasourceRepository, "get_by_id", AsyncMock(return_value=datasource))

        result = await service.get_dataset_preview(321)

        assert result["id"] == "321"
        assert result["name"] == "产品数据集"
        assert result["total"] == 2
        payload = cast(dict[str, object], result["data"])
        assert payload["fields"] == [
            {"name": "订单号", "originName": "订单号", "deType": 3, "fieldType": "DOUBLE"},
            {"name": "客户名称", "originName": "客户名称", "deType": 0, "fieldType": "TEXT"},
        ]
        assert payload["data"] == [
            {"订单号": 1, "客户名称": "alice"},
            {"订单号": 2, "客户名称": "bob"},
        ]

    @pytest.mark.asyncio
    async def test_get_dataset_total_uses_file_preview_for_saved_excel_dataset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        field_repo = SimpleNamespace(
            list_by_group=AsyncMock(return_value=self._fields()),
            list_checked_by_group_no_chart_filter=AsyncMock(return_value=self._fields()),
        )
        service = self._build_service(field_repo)
        service._get_group = AsyncMock(return_value=make_group(  # type: ignore[method-assign]
            id=321,
            name="产品数据集",
            node_type="dataset",
            info={"datasourceId": 88, "tableName": "数据1"},
        ))
        service.table_repo = cast(Any, SimpleNamespace(list_by_group=AsyncMock(return_value=[make_table(
            id=303,
            name="产品数据集",
            table_name="数据1",
            datasource_id=88,
            type="db",
        )])))

        datasource = CoreDatasource(
            id=88,
            name="orders-file",
            type="Excel",
            pid=None,
            edit_type=None,
            configuration=[{
                "tableName": "数据1",
                "deTableName": "excel_data_1",
                "fields": [
                    {"originName": "订单号", "name": "订单号", "fieldType": "DOUBLE", "deType": 3},
                ],
                "jsonArray": [
                    {"订单号": 1},
                    {"订单号": 2},
                    {"订单号": 3},
                ],
            }],
            description=None,
            create_time=1,
            update_time=2,
            update_by=7,
            create_by="7",
            status="Success",
            qrtz_instance=None,
            task_status="WaitingForExecution",
            enable_data_fill=False,
        )
        monkeypatch.setattr(DatasourceRepository, "get_by_id", AsyncMock(return_value=datasource))

        assert await service.get_dataset_total(321) == 3

    @pytest.mark.asyncio
    async def test_get_enum_values_uses_file_preview_for_saved_excel_dataset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        excel_fields = [
            make_field(id=1, origin_name="订单号", name="订单号", dataease_name="订单号", type="DOUBLE", de_type=3),
            make_field(id=2, origin_name="客户名称", name="客户名称", dataease_name="客户名称", type="TEXT", de_type=0),
        ]
        field_repo = SimpleNamespace(
            list_by_group=AsyncMock(return_value=excel_fields),
            list_checked_by_group_no_chart_filter=AsyncMock(return_value=excel_fields),
        )
        service = self._build_service(field_repo)
        service._get_group = AsyncMock(return_value=make_group(  # type: ignore[method-assign]
            id=321,
            name="产品数据集",
            node_type="dataset",
            info={"datasourceId": 88, "tableName": "数据1"},
        ))
        service.table_repo = cast(Any, SimpleNamespace(list_by_group=AsyncMock(return_value=[make_table(
            id=303,
            name="产品数据集",
            table_name="数据1",
            datasource_id=88,
            type="db",
        )])))

        datasource = CoreDatasource(
            id=88,
            name="orders-file",
            type="Excel",
            pid=None,
            edit_type=None,
            configuration=[{
                "tableName": "数据1",
                "deTableName": "excel_data_1",
                "fields": [
                    {"originName": "订单号", "name": "订单号", "fieldType": "DOUBLE", "deType": 3},
                    {"originName": "客户名称", "name": "客户名称", "fieldType": "TEXT", "deType": 0},
                ],
                "jsonArray": [
                    {"订单号": 1, "客户名称": "alice"},
                    {"订单号": 2, "客户名称": "bob"},
                    {"订单号": 3, "客户名称": "alice"},
                    {"订单号": None, "客户名称": None},
                ],
            }],
            description=None,
            create_time=1,
            update_time=2,
            update_by=7,
            create_by="7",
            status="Success",
            qrtz_instance=None,
            task_status="WaitingForExecution",
            enable_data_fill=False,
        )
        monkeypatch.setattr(DatasourceRepository, "get_by_id", AsyncMock(return_value=datasource))

        assert await service.get_enum_values(DatasetEnumValueRequest(
            dataset_group_id=321,
            field_id=2,
            result_limit=10,
        )) == ["alice", "bob", ""]

    @pytest.mark.asyncio
    async def test_preview_data_uses_file_preview_for_excel_union_payload(self, monkeypatch: pytest.MonkeyPatch) -> None:
        field_repo = SimpleNamespace(list_checked_by_group_no_chart_filter=AsyncMock(return_value=self._fields()))
        service = self._build_service(field_repo)

        datasource = CoreDatasource(
            id=88,
            name="orders-file",
            type="Excel",
            pid=None,
            edit_type=None,
            configuration=[{
                "tableName": "数据1",
                "deTableName": "excel_data_1",
                "fields": [
                    {"originName": "订单号", "name": "订单号", "fieldType": "DOUBLE", "deType": 3},
                    {"originName": "客户名称", "name": "客户名称", "fieldType": "TEXT", "deType": 0},
                ],
                "jsonArray": [
                    {"订单号": 1, "客户名称": "alice"},
                    {"订单号": 2, "客户名称": "bob"},
                    {"订单号": 3, "客户名称": "carol"},
                ],
            }],
            description=None,
            create_time=1,
            update_time=2,
            update_by=7,
            create_by="7",
            status="Success",
            qrtz_instance=None,
            task_status="WaitingForExecution",
            enable_data_fill=False,
        )
        monkeypatch.setattr(DatasourceRepository, "get_by_id", AsyncMock(return_value=datasource))

        result = await service.preview_data(DatasetPreviewDataRequest.model_validate({
            "union": [{
                "currentDs": {
                    "id": "303",
                    "datasourceId": "88",
                    "tableName": "数据1",
                    "type": "TABLE",
                    "info": '{"table":"数据1","sql":""}',
                },
                "currentDsFields": [],
                "childrenDs": [],
                "unionToParent": {"unionType": "left", "unionFields": []},
            }],
            "allFields": self._fields(),
            "limit": 2,
            "offset": 1,
        }))

        payload = cast(dict[str, object], result["data"])
        assert payload["fields"] == [
            {"name": "订单号", "originName": "订单号", "deType": 3, "fieldType": "DOUBLE"},
            {"name": "客户名称", "originName": "客户名称", "deType": 0, "fieldType": "TEXT"},
        ]
        assert payload["data"] == [
            {"订单号": 2, "客户名称": "bob"},
            {"订单号": 3, "客户名称": "carol"},
        ]
        assert payload["total"] == 3
