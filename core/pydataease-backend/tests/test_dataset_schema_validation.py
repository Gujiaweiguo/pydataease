from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.dataset import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetBarInfoResponse,
    DatasetFieldIdsRequest,
    DatasetFieldResponse,
    DatasetFieldSaveRequest,
    DatasetGroupCreate,
    DatasetGroupMove,
    DatasetGroupRename,
    DatasetGroupUpdate,
    DatasetNodeResponse,
    DatasetTableFieldRequest,
    DatasetTreeNodeResponse,
)
from app.schemas.dataset_sql_log import (  # pyright: ignore[reportImplicitRelativeImport]
    SqlLogCreateRequest,
    SqlLogListRequest,
    SqlLogResponse,
)


VALID_NAME = "dataset-name"
TOO_LONG_NAME = "x" * 129


class TestDatasetGroupCreate:
    def test_accepts_valid_snake_case_payload(self) -> None:
        model = DatasetGroupCreate(
            name=VALID_NAME,
            pid=1,
            node_type="folder",
            datasource_id=2,
            table_name="orders",
            all_fields=[{"id": 1}],
            is_cross=True,
        )

        assert model.name == VALID_NAME
        assert model.node_type == "folder"
        assert model.datasource_id == 2

    def test_accepts_valid_camel_case_payload(self) -> None:
        model = DatasetGroupCreate.model_validate(
            {
                "name": VALID_NAME,
                "nodeType": "folder",
                "datasourceId": 3,
                "tableName": "users",
                "allFields": ["a"],
                "isCross": False,
            }
        )

        assert model.node_type == "folder"
        assert model.datasource_id == 3
        assert model.table_name == "users"

    def test_rejects_empty_name(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupCreate(name="", node_type="folder")

    def test_rejects_too_long_name(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupCreate(name=TOO_LONG_NAME, node_type="folder")

    def test_requires_name(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupCreate.model_validate({"node_type": "folder"})

    def test_requires_node_type(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupCreate.model_validate({"name": VALID_NAME})

    def test_serializes_aliases_in_camel_case(self) -> None:
        model = DatasetGroupCreate(
            name=VALID_NAME,
            node_type="folder",
            datasource_id=8,
            table_name="sales",
            all_fields=[1],
            is_cross=True,
        )

        dumped = model.model_dump(by_alias=True)
        assert dumped["nodeType"] == "folder"
        assert dumped["datasourceId"] == 8
        assert dumped["tableName"] == "sales"
        assert dumped["allFields"] == [1]
        assert dumped["isCross"] is True

    def test_serializes_field_names_in_snake_case(self) -> None:
        model = DatasetGroupCreate.model_validate(
            {"name": VALID_NAME, "nodeType": "folder", "datasourceId": 9}
        )

        dumped = model.model_dump(by_alias=False)
        assert dumped["node_type"] == "folder"
        assert dumped["datasource_id"] == 9


class TestDatasetGroupUpdate:
    def test_accepts_id_only(self) -> None:
        model = DatasetGroupUpdate(id=1)

        assert model.id == 1
        assert model.name is None

    def test_accepts_camel_case_aliases(self) -> None:
        model = DatasetGroupUpdate.model_validate(
            {
                "id": 1,
                "nodeType": "dataset",
                "datasourceId": 5,
                "tableName": "orders",
                "allFields": [{"name": "col"}],
                "isCross": True,
            }
        )

        assert model.node_type == "dataset"
        assert model.datasource_id == 5
        assert model.table_name == "orders"

    def test_rejects_empty_name_when_provided(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupUpdate(id=1, name="")

    def test_rejects_too_long_name_when_provided(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupUpdate(id=1, name=TOO_LONG_NAME)

    def test_requires_id(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupUpdate.model_validate({"name": VALID_NAME})

    def test_serializes_aliases_in_camel_case(self) -> None:
        model = DatasetGroupUpdate(id=1, node_type="folder", datasource_id=4, table_name="t")

        dumped = model.model_dump(by_alias=True)
        assert dumped["nodeType"] == "folder"
        assert dumped["datasourceId"] == 4
        assert dumped["tableName"] == "t"

    def test_serializes_field_names_in_snake_case(self) -> None:
        model = DatasetGroupUpdate.model_validate(
            {"id": 1, "nodeType": "folder", "datasourceId": 4}
        )

        dumped = model.model_dump(by_alias=False)
        assert dumped["node_type"] == "folder"
        assert dumped["datasource_id"] == 4


class TestDatasetGroupRename:
    def test_accepts_valid_payload(self) -> None:
        model = DatasetGroupRename(id=1, name=VALID_NAME)

        assert model.id == 1
        assert model.name == VALID_NAME

    def test_rejects_empty_name(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupRename(id=1, name="")

    def test_rejects_too_long_name(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupRename(id=1, name=TOO_LONG_NAME)

    def test_requires_id(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupRename.model_validate({"name": VALID_NAME})

    def test_requires_name(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupRename.model_validate({"id": 1})


class TestDatasetGroupMove:
    def test_accepts_valid_payload(self) -> None:
        model = DatasetGroupMove(id=1, pid=2)

        assert model.id == 1
        assert model.pid == 2

    def test_requires_id(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupMove.model_validate({"pid": 2})

    def test_requires_pid(self) -> None:
        with pytest.raises(ValidationError):
            DatasetGroupMove.model_validate({"id": 1})


class TestDatasetTableFieldRequest:
    def test_accepts_empty_payload(self) -> None:
        model = DatasetTableFieldRequest()

        assert model.dataset_group_id is None
        assert model.datasource_id is None
        assert model.table_name is None

    def test_accepts_camel_case_aliases(self) -> None:
        model = DatasetTableFieldRequest.model_validate(
            {"datasetGroupId": 7, "datasourceId": 8, "tableName": "sales"}
        )

        assert model.dataset_group_id == 7
        assert model.datasource_id == 8
        assert model.table_name == "sales"

    def test_accepts_snake_case_aliases(self) -> None:
        model = DatasetTableFieldRequest(dataset_group_id=7, datasource_id=8, table_name="sales")

        assert model.dataset_group_id == 7
        assert model.datasource_id == 8
        assert model.table_name == "sales"

    def test_serializes_aliases_in_camel_case(self) -> None:
        model = DatasetTableFieldRequest(dataset_group_id=1, datasource_id=2, table_name="t")

        assert model.model_dump(by_alias=True) == {
            "datasetGroupId": 1,
            "datasourceId": 2,
            "tableName": "t",
        }

    def test_serializes_field_names_in_snake_case(self) -> None:
        model = DatasetTableFieldRequest.model_validate(
            {"datasetGroupId": 1, "datasourceId": 2, "tableName": "t"}
        )

        assert model.model_dump(by_alias=False) == {
            "dataset_group_id": 1,
            "datasource_id": 2,
            "table_name": "t",
        }


class TestDatasetNodeResponse:
    def test_validates_from_attributes(self) -> None:
        source = SimpleNamespace(
            id=1,
            name="root",
            pid=0,
            level=1,
            node_type="folder",
            create_by="alice",
            create_time=123,
            qrtz_instance="job-1",
            sync_status="SUCCESS",
            update_by="bob",
            last_update_time=456,
            union_sql="select 1",
            is_cross=True,
        )

        model = DatasetNodeResponse.model_validate(source, from_attributes=True)
        assert model.id == 1
        assert model.node_type == "folder"
        assert model.create_by == "alice"

    def test_requires_id(self) -> None:
        with pytest.raises(ValidationError):
            DatasetNodeResponse.model_validate({"name": "root"})

    def test_serializes_aliases_in_camel_case(self) -> None:
        model = DatasetNodeResponse(
            id=1,
            node_type="folder",
            create_by="alice",
            create_time=1,
            qrtz_instance="job",
            sync_status="OK",
            update_by="bob",
            last_update_time=2,
            union_sql="sql",
            is_cross=False,
        )

        dumped = model.model_dump(by_alias=True)
        assert dumped["nodeType"] == "folder"
        assert dumped["createBy"] == "alice"
        assert dumped["lastUpdateTime"] == 2
        assert dumped["isCross"] is False

    def test_serializes_field_names_in_snake_case(self) -> None:
        model = DatasetNodeResponse(id=1, node_type="folder", create_by="alice")

        dumped = model.model_dump(by_alias=False)
        assert dumped["node_type"] == "folder"
        assert dumped["create_by"] == "alice"


class TestDatasetTreeNodeResponse:
    def test_supports_nested_children(self) -> None:
        model = DatasetTreeNodeResponse(
            id=1,
            name="root",
            node_type="folder",
            leaf=False,
            children=[
                DatasetTreeNodeResponse(
                    id=2,
                    name="child",
                    node_type="dataset",
                    leaf=True,
                    children=[],
                )
            ],
        )

        assert len(model.children) == 1
        assert model.children[0].id == 2
        assert model.children[0].leaf is True

    def test_defaults_children_to_empty_list(self) -> None:
        model = DatasetTreeNodeResponse(id=1, node_type=None)

        assert model.children == []

    def test_serializes_nested_children_with_aliases(self) -> None:
        model = DatasetTreeNodeResponse(
            id=1,
            node_type="folder",
            children=[DatasetTreeNodeResponse(id=2, node_type="dataset", children=[])],
        )

        dumped = model.model_dump(by_alias=True)
        assert dumped["nodeType"] == "folder"
        assert dumped["children"][0]["nodeType"] == "dataset"


class TestDatasetFieldResponse:
    def test_validates_from_attributes(self) -> None:
        source = SimpleNamespace(
            id=1,
            datasource_id=2,
            dataset_table_id=3,
            dataset_group_id=4,
            chart_id=5,
            origin_name="origin",
            name="name",
            description="desc",
            dataease_name="de-name",
            field_short_name="short",
            group_type="dim",
            type="string",
            size=10,
            de_type=1,
            de_extract_type=2,
            ext_field=0,
            checked=True,
            column_index=6,
            last_sync_time=7,
            accuracy=8,
            date_format="%Y-%m-%d",
            date_format_type="custom",
        )

        model = DatasetFieldResponse.model_validate(source, from_attributes=True)
        assert model.dataset_table_id == 3
        assert model.dataease_name == "de-name"
        assert model.date_format_type == "custom"

    def test_requires_id(self) -> None:
        with pytest.raises(ValidationError):
            DatasetFieldResponse.model_validate({"name": "field"})

    def test_serializes_aliases_in_camel_case(self) -> None:
        model = DatasetFieldResponse(id=1, datasource_id=2, dataset_table_id=3, origin_name="origin", de_type=4)

        dumped = model.model_dump(by_alias=True)
        assert dumped["datasourceId"] == 2
        assert dumped["datasetTableId"] == 3
        assert dumped["originName"] == "origin"
        assert dumped["deType"] == 4

    def test_serializes_field_names_in_snake_case(self) -> None:
        model = DatasetFieldResponse(id=1, dataset_group_id=3, dataease_name="alias")

        dumped = model.model_dump(by_alias=False)
        assert dumped["dataset_group_id"] == 3
        assert dumped["dataease_name"] == "alias"


class TestDatasetFieldSaveRequest:
    def test_accepts_empty_payload(self) -> None:
        model = DatasetFieldSaveRequest()

        assert model.id is None
        assert model.dataset_group_id is None

    def test_accepts_camel_case_aliases(self) -> None:
        model = DatasetFieldSaveRequest.model_validate(
            {
                "datasetGroupId": 1,
                "datasetTableId": 2,
                "chartId": 3,
                "originName": "origin",
                "dataeaseName": "de-name",
                "groupType": "dim",
                "deType": 4,
                "deExtractType": 5,
                "extField": 6,
                "columnIndex": 7,
                "dateFormat": "%Y",
                "dateFormatType": "year",
            }
        )

        assert model.dataset_group_id == 1
        assert model.dataset_table_id == 2
        assert model.date_format_type == "year"

    def test_accepts_snake_case_aliases(self) -> None:
        model = DatasetFieldSaveRequest(
            dataset_group_id=1,
            dataset_table_id=2,
            chart_id=3,
            origin_name="origin",
            dataease_name="de-name",
            group_type="dim",
            de_type=4,
            de_extract_type=5,
            ext_field=6,
            column_index=7,
            date_format="%Y",
            date_format_type="year",
        )

        assert model.chart_id == 3
        assert model.group_type == "dim"
        assert model.de_extract_type == 5

    def test_serializes_aliases_in_camel_case(self) -> None:
        model = DatasetFieldSaveRequest(dataset_group_id=1, dataset_table_id=2, origin_name="origin", date_format_type="year")

        dumped = model.model_dump(by_alias=True)
        assert dumped["datasetGroupId"] == 1
        assert dumped["datasetTableId"] == 2
        assert dumped["originName"] == "origin"
        assert dumped["dateFormatType"] == "year"

    def test_serializes_field_names_in_snake_case(self) -> None:
        model = DatasetFieldSaveRequest.model_validate(
            {
                "datasetGroupId": 1,
                "datasetTableId": 2,
                "originName": "origin",
                "dateFormatType": "year",
            }
        )

        dumped = model.model_dump(by_alias=False)
        assert dumped["dataset_group_id"] == 1
        assert dumped["dataset_table_id"] == 2
        assert dumped["origin_name"] == "origin"
        assert dumped["date_format_type"] == "year"


class TestDatasetFieldIdsRequest:
    def test_accepts_ids_list(self) -> None:
        model = DatasetFieldIdsRequest(ids=[1, 2, 3])

        assert model.ids == [1, 2, 3]

    def test_defaults_to_empty_list(self) -> None:
        model = DatasetFieldIdsRequest()

        assert model.ids == []


class TestDatasetBarInfoResponse:
    def test_validates_from_attributes(self) -> None:
        source = SimpleNamespace(id=1, name="dataset", create_by="alice", create_time=11, update_by="bob", last_update_time=22)

        model = DatasetBarInfoResponse.model_validate(source, from_attributes=True)
        assert model.create_by == "alice"
        assert model.last_update_time == 22

    def test_requires_id(self) -> None:
        with pytest.raises(ValidationError):
            DatasetBarInfoResponse.model_validate({"name": "dataset"})

    def test_serializes_aliases_in_camel_case(self) -> None:
        model = DatasetBarInfoResponse(id=1, create_by="alice", create_time=2, update_by="bob", last_update_time=3)

        dumped = model.model_dump(by_alias=True)
        assert dumped["createBy"] == "alice"
        assert dumped["createTime"] == 2
        assert dumped["lastUpdateTime"] == 3


class TestSqlLogCreateRequest:
    def test_accepts_empty_payload(self) -> None:
        model = SqlLogCreateRequest.model_validate({})

        assert model.table_id is None
        assert model.error_msg is None

    def test_accepts_camel_case_aliases(self) -> None:
        model = SqlLogCreateRequest.model_validate(
            {
                "tableId": "1",
                "sqlSnapshot": "select 1",
                "tableName": "orders",
                "errorMsg": "boom",
            }
        )

        assert model.table_id == "1"
        assert model.sql_snapshot == "select 1"
        assert model.error_msg == "boom"

    def test_accepts_snake_case_aliases(self) -> None:
        model = SqlLogCreateRequest(table_id="1", sql_snapshot="select 1", table_name="orders", error_msg="boom")

        assert model.table_name == "orders"
        assert model.error_msg == "boom"

    def test_serializes_field_names_in_snake_case(self) -> None:
        model = SqlLogCreateRequest.model_validate(
            {
                "tableId": "1",
                "sqlSnapshot": "select 1",
                "tableName": "orders",
                "errorMsg": "boom",
            }
        )

        assert model.model_dump(by_alias=False) == {
            "table_id": "1",
            "sql_snapshot": "select 1",
            "table_name": "orders",
            "status": None,
            "error_msg": "boom",
        }


class TestSqlLogListRequest:
    def test_accepts_empty_payload(self) -> None:
        model = SqlLogListRequest.model_validate({})

        assert model.table_id is None

    def test_accepts_camel_case_alias(self) -> None:
        model = SqlLogListRequest.model_validate({"tableId": "2"})

        assert model.table_id == "2"

    def test_accepts_snake_case_alias(self) -> None:
        model = SqlLogListRequest(table_id="3")

        assert model.table_id == "3"


class TestSqlLogResponse:
    def test_validates_from_attributes(self) -> None:
        source = SimpleNamespace(
            id="1",
            table_id="2",
            sql_snapshot="select 1",
            table_name="orders",
            create_time=3,
            create_by="alice",
            status="SUCCESS",
            error_msg=None,
        )

        model = SqlLogResponse.model_validate(source, from_attributes=True)
        assert model.id == "1"
        assert model.table_id == "2"
        assert model.create_by == "alice"

    def test_requires_id(self) -> None:
        with pytest.raises(ValidationError):
            SqlLogResponse.model_validate({"table_id": "2"})

    def test_serializes_aliases_in_camel_case(self) -> None:
        model = SqlLogResponse(
            id="1",
            table_id="2",
            sql_snapshot="select 1",
            table_name="orders",
            create_time=3,
            create_by="alice",
            status="SUCCESS",
            error_msg="boom",
        )

        dumped = model.model_dump(by_alias=True)
        assert dumped["tableId"] == "2"
        assert dumped["sqlSnapshot"] == "select 1"
        assert dumped["tableName"] == "orders"
        assert dumped["createTime"] == 3
        assert dumped["createBy"] == "alice"
        assert dumped["errorMsg"] == "boom"

    def test_serializes_field_names_in_snake_case(self) -> None:
        model = SqlLogResponse(
            id="1",
            table_id="2",
            sql_snapshot=None,
            table_name=None,
            create_time=None,
            create_by=None,
            status=None,
            error_msg="boom",
        )

        dumped = model.model_dump(by_alias=False)
        assert dumped["table_id"] == "2"
        assert dumped["error_msg"] == "boom"
