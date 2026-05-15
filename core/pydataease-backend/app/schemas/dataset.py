from __future__ import annotations

from typing import TypeAlias

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

JSONDict: TypeAlias = dict[str, object]
JSONList: TypeAlias = list[object]


class BusiTreeRequest(BaseModel):
    busi_flag: str = Field(default="dataset", serialization_alias="busiFlag")
    weight: int | None = None


class DatasetGroupCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=128)
    pid: int = 0
    node_type: str = Field(validation_alias=AliasChoices("nodeType", "node_type"), serialization_alias="nodeType")
    type: str | None = None
    mode: int | None = None
    info: JSONDict | JSONList | None = None
    datasource_id: int | None = Field(default=None, validation_alias=AliasChoices("datasourceId", "datasource_id"), serialization_alias="datasourceId")
    table_name: str | None = Field(default=None, validation_alias=AliasChoices("tableName", "table_name"), serialization_alias="tableName")
    union: JSONList | None = None
    all_fields: JSONList | None = Field(default=None, validation_alias=AliasChoices("allFields", "all_fields"), serialization_alias="allFields")
    is_cross: bool | None = Field(default=None, validation_alias=AliasChoices("isCross", "is_cross"), serialization_alias="isCross")
    sql: str | None = None


class DatasetGroupUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str | None = Field(default=None, min_length=1, max_length=128)
    pid: int | None = None
    node_type: str | None = Field(default=None, validation_alias=AliasChoices("nodeType", "node_type"), serialization_alias="nodeType")
    type: str | None = None
    mode: int | None = None
    info: JSONDict | JSONList | None = None
    datasource_id: int | None = Field(default=None, validation_alias=AliasChoices("datasourceId", "datasource_id"), serialization_alias="datasourceId")
    table_name: str | None = Field(default=None, validation_alias=AliasChoices("tableName", "table_name"), serialization_alias="tableName")
    union: JSONList | None = None
    all_fields: JSONList | None = Field(default=None, validation_alias=AliasChoices("allFields", "all_fields"), serialization_alias="allFields")
    is_cross: bool | None = Field(default=None, validation_alias=AliasChoices("isCross", "is_cross"), serialization_alias="isCross")
    sql: str | None = None


class DatasetGroupRename(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=128)


class DatasetGroupMove(BaseModel):
    id: int
    pid: int


class DatasetTableFieldRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dataset_group_id: int | None = Field(default=None, validation_alias=AliasChoices("datasetGroupId", "dataset_group_id"), serialization_alias="datasetGroupId")
    datasource_id: int | None = Field(default=None, validation_alias=AliasChoices("datasourceId", "datasource_id"), serialization_alias="datasourceId")
    table_name: str | None = Field(default=None, validation_alias=AliasChoices("tableName", "table_name"), serialization_alias="tableName")


class DatasetNodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str | None = None
    pid: int | None = None
    level: int | None = None
    node_type: str | None = Field(default=None, serialization_alias="nodeType")
    type: str | None = None
    mode: int | None = None
    info: JSONDict | JSONList | str | None = None
    create_by: str | None = Field(default=None, serialization_alias="createBy")
    create_time: int | None = Field(default=None, serialization_alias="createTime")
    qrtz_instance: str | None = Field(default=None, serialization_alias="qrtzInstance")
    sync_status: str | None = Field(default=None, serialization_alias="syncStatus")
    update_by: str | None = Field(default=None, serialization_alias="updateBy")
    last_update_time: int | None = Field(default=None, serialization_alias="lastUpdateTime")
    union_sql: str | None = Field(default=None, serialization_alias="unionSql")
    is_cross: bool | None = Field(default=None, serialization_alias="isCross")


class DatasetTreeNodeResponse(DatasetNodeResponse):
    children: list[DatasetTreeNodeResponse] = Field(default_factory=list)
    leaf: bool | None = None


class DatasetTableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str | None = None
    table_name: str | None = Field(default=None, serialization_alias="tableName")
    datasource_id: int | None = Field(default=None, serialization_alias="datasourceId")
    dataset_group_id: int | None = Field(default=None, serialization_alias="datasetGroupId")
    type: str | None = None
    info: str | None = None


class DatasetFieldResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    datasource_id: int | None = Field(default=None, serialization_alias="datasourceId")
    dataset_table_id: int | None = Field(default=None, serialization_alias="datasetTableId")
    dataset_group_id: int | None = Field(default=None, serialization_alias="datasetGroupId")
    chart_id: int | None = Field(default=None, serialization_alias="chartId")
    origin_name: str | None = Field(default=None, serialization_alias="originName")
    name: str | None = None
    description: str | None = None
    dataease_name: str | None = Field(default=None, serialization_alias="dataeaseName")
    field_short_name: str | None = Field(default=None, serialization_alias="fieldShortName")
    group_type: str | None = Field(default=None, serialization_alias="groupType")
    type: str | None = None
    size: int | None = None
    de_type: int | None = Field(default=None, serialization_alias="deType")
    de_extract_type: int | None = Field(default=None, serialization_alias="deExtractType")
    ext_field: int | None = Field(default=None, serialization_alias="extField")
    checked: bool | None = None
    column_index: int | None = Field(default=None, serialization_alias="columnIndex")
    last_sync_time: int | None = Field(default=None, serialization_alias="lastSyncTime")
    accuracy: int | None = None
    date_format: str | None = Field(default=None, serialization_alias="dateFormat")
    date_format_type: str | None = Field(default=None, serialization_alias="dateFormatType")


class DatasetBarInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str | None = None
    create_by: str | None = Field(default=None, serialization_alias="createBy")
    create_time: int | None = Field(default=None, serialization_alias="createTime")
    update_by: str | None = Field(default=None, serialization_alias="updateBy")
    last_update_time: int | None = Field(default=None, serialization_alias="lastUpdateTime")


class DatasetFieldSaveRequest(BaseModel):
    """For save endpoint — matches Java DatasetTableFieldDTO."""
    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    dataset_group_id: int | None = Field(default=None, validation_alias=AliasChoices("datasetGroupId", "dataset_group_id"), serialization_alias="datasetGroupId")
    dataset_table_id: int | None = Field(default=None, validation_alias=AliasChoices("datasetTableId", "dataset_table_id"), serialization_alias="datasetTableId")
    chart_id: int | None = Field(default=None, validation_alias=AliasChoices("chartId", "chart_id"), serialization_alias="chartId")
    origin_name: str | None = Field(default=None, validation_alias=AliasChoices("originName", "origin_name"), serialization_alias="originName")
    name: str | None = None
    dataease_name: str | None = Field(default=None, validation_alias=AliasChoices("dataeaseName", "dataease_name"), serialization_alias="dataeaseName")
    group_type: str | None = Field(default=None, validation_alias=AliasChoices("groupType", "group_type"), serialization_alias="groupType")
    type: str | None = None
    de_type: int | None = Field(default=None, validation_alias=AliasChoices("deType", "de_type"), serialization_alias="deType")
    de_extract_type: int | None = Field(default=None, validation_alias=AliasChoices("deExtractType", "de_extract_type"), serialization_alias="deExtractType")
    ext_field: int | None = Field(default=None, validation_alias=AliasChoices("extField", "ext_field"), serialization_alias="extField")
    checked: bool | None = None
    column_index: int | None = Field(default=None, validation_alias=AliasChoices("columnIndex", "column_index"), serialization_alias="columnIndex")
    description: str | None = None
    date_format: str | None = Field(default=None, validation_alias=AliasChoices("dateFormat", "date_format"), serialization_alias="dateFormat")
    date_format_type: str | None = Field(default=None, validation_alias=AliasChoices("dateFormatType", "date_format_type"), serialization_alias="dateFormatType")
    accuracy: int | None = None


class DatasetFieldIdsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ids: list[int] = Field(default_factory=list)
