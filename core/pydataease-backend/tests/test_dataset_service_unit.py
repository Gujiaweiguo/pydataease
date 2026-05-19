from __future__ import annotations

from types import SimpleNamespace
from typing import cast

from app.models.dataset import CoreDatasetGroup  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.datasource import DatasourceFieldResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_service import DatasetService, _build_tree, _compute_level  # pyright: ignore[reportImplicitRelativeImport]

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
