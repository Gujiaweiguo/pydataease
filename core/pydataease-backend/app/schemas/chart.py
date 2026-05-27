from __future__ import annotations

from typing import TypeAlias

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

JSONDict: TypeAlias = dict[str, object]
JSONList: TypeAlias = list[object]
JSONValue: TypeAlias = JSONDict | JSONList


class ChartSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    title: str | None = None
    scene_id: int = Field(validation_alias=AliasChoices("sceneId", "scene_id"), serialization_alias="sceneId")
    table_id: int | None = Field(default=None, validation_alias=AliasChoices("tableId", "table_id"), serialization_alias="tableId")
    type: str | None = None
    render: str | None = None
    result_count: int | None = Field(default=None, validation_alias=AliasChoices("resultCount", "result_count"), serialization_alias="resultCount")
    result_mode: str | None = Field(default=None, validation_alias=AliasChoices("resultMode", "result_mode"), serialization_alias="resultMode")
    x_axis: JSONValue | None = Field(default=None, validation_alias=AliasChoices("xAxis", "x_axis"), serialization_alias="xAxis")
    x_axis_ext: JSONValue | None = Field(default=None, validation_alias=AliasChoices("xAxisExt", "x_axis_ext"), serialization_alias="xAxisExt")
    y_axis: JSONValue | None = Field(default=None, validation_alias=AliasChoices("yAxis", "y_axis"), serialization_alias="yAxis")
    y_axis_ext: JSONValue | None = Field(default=None, validation_alias=AliasChoices("yAxisExt", "y_axis_ext"), serialization_alias="yAxisExt")
    ext_stack: JSONValue | None = Field(default=None, validation_alias=AliasChoices("extStack", "ext_stack"), serialization_alias="extStack")
    ext_bubble: JSONValue | None = Field(default=None, validation_alias=AliasChoices("extBubble", "ext_bubble"), serialization_alias="extBubble")
    ext_label: JSONValue | None = Field(default=None, validation_alias=AliasChoices("extLabel", "ext_label"), serialization_alias="extLabel")
    ext_tooltip: JSONValue | None = Field(default=None, validation_alias=AliasChoices("extTooltip", "ext_tooltip"), serialization_alias="extTooltip")
    ext_color: JSONValue | None = Field(default=None, validation_alias=AliasChoices("extColor", "ext_color"), serialization_alias="extColor")
    custom_attr: JSONValue | None = Field(default=None, validation_alias=AliasChoices("customAttr", "custom_attr"), serialization_alias="customAttr")
    custom_style: JSONValue | None = Field(default=None, validation_alias=AliasChoices("customStyle", "custom_style"), serialization_alias="customStyle")
    custom_filter: JSONValue | None = Field(default=None, validation_alias=AliasChoices("customFilter", "custom_filter"), serialization_alias="customFilter")
    drill_fields: JSONValue | None = Field(default=None, validation_alias=AliasChoices("drillFields", "drill_fields"), serialization_alias="drillFields")
    senior: JSONValue | None = None
    snapshot: str | None = None
    style_priority: str | None = Field(default=None, validation_alias=AliasChoices("stylePriority", "style_priority"), serialization_alias="stylePriority")
    chart_type: str | None = Field(default=None, validation_alias=AliasChoices("chartType", "chart_type"), serialization_alias="chartType")
    is_plugin: bool | None = Field(default=None, validation_alias=AliasChoices("isPlugin", "is_plugin"), serialization_alias="isPlugin")
    data_from: str | None = Field(default=None, validation_alias=AliasChoices("dataFrom", "data_from"), serialization_alias="dataFrom")
    view_fields: JSONValue | None = Field(default=None, validation_alias=AliasChoices("viewFields", "view_fields"), serialization_alias="viewFields")
    refresh_view_enable: bool | None = Field(default=None, validation_alias=AliasChoices("refreshViewEnable", "refresh_view_enable"), serialization_alias="refreshViewEnable")
    refresh_unit: str | None = Field(default=None, validation_alias=AliasChoices("refreshUnit", "refresh_unit"), serialization_alias="refreshUnit")
    refresh_time: int | None = Field(default=None, validation_alias=AliasChoices("refreshTime", "refresh_time"), serialization_alias="refreshTime")
    linkage_active: bool | None = Field(default=None, validation_alias=AliasChoices("linkageActive", "linkage_active"), serialization_alias="linkageActive")
    jump_active: bool | None = Field(default=None, validation_alias=AliasChoices("jumpActive", "jump_active"), serialization_alias="jumpActive")
    aggregate: bool | None = None
    flow_map_start_name: JSONValue | None = Field(default=None, validation_alias=AliasChoices("flowMapStartName", "flow_map_start_name"), serialization_alias="flowMapStartName")
    flow_map_end_name: JSONValue | None = Field(default=None, validation_alias=AliasChoices("flowMapEndName", "flow_map_end_name"), serialization_alias="flowMapEndName")
    custom_attr_mobile: JSONValue | None = Field(default=None, validation_alias=AliasChoices("customAttrMobile", "custom_attr_mobile"), serialization_alias="customAttrMobile")
    custom_style_mobile: JSONValue | None = Field(default=None, validation_alias=AliasChoices("customStyleMobile", "custom_style_mobile"), serialization_alias="customStyleMobile")
    sort_priority: JSONValue | None = Field(default=None, validation_alias=AliasChoices("sortPriority", "sort_priority"), serialization_alias="sortPriority")


class ChartUpdateRequest(ChartSaveRequest):
    id: int  # pyright: ignore[reportGeneralTypeIssues, reportIncompatibleVariableOverride]


class ChartDataRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    scene_id: int | None = Field(default=None, validation_alias=AliasChoices("sceneId", "scene_id"), serialization_alias="sceneId")
    table_id: int | None = Field(default=None, validation_alias=AliasChoices("tableId", "table_id"), serialization_alias="tableId")
    x_axis: JSONValue | None = Field(default=None, validation_alias=AliasChoices("xAxis", "x_axis"), serialization_alias="xAxis")
    y_axis: JSONValue | None = Field(default=None, validation_alias=AliasChoices("yAxis", "y_axis"), serialization_alias="yAxis")
    x_axis_ext: JSONValue | None = Field(default=None, validation_alias=AliasChoices("xAxisExt", "x_axis_ext"), serialization_alias="xAxisExt")
    y_axis_ext: JSONValue | None = Field(default=None, validation_alias=AliasChoices("yAxisExt", "y_axis_ext"), serialization_alias="yAxisExt")
    ext_bubble: JSONValue | None = Field(default=None, validation_alias=AliasChoices("extBubble", "ext_bubble"), serialization_alias="extBubble")
    ext_label: JSONValue | None = Field(default=None, validation_alias=AliasChoices("extLabel", "ext_label"), serialization_alias="extLabel")
    ext_stack: JSONValue | None = Field(default=None, validation_alias=AliasChoices("extStack", "ext_stack"), serialization_alias="extStack")
    ext_tooltip: JSONValue | None = Field(default=None, validation_alias=AliasChoices("extTooltip", "ext_tooltip"), serialization_alias="extTooltip")
    ext_color: JSONValue | None = Field(default=None, validation_alias=AliasChoices("extColor", "ext_color"), serialization_alias="extColor")
    view_fields: JSONValue | None = Field(default=None, validation_alias=AliasChoices("viewFields", "view_fields"), serialization_alias="viewFields")
    fields: JSONValue | None = None


class ChartViewListRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    scene_id: int = Field(validation_alias=AliasChoices("sceneId", "scene_id"), serialization_alias="sceneId")


class ChartFieldEnumRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chart_id: int | None = Field(default=None, validation_alias=AliasChoices("chartId", "chart_id"), serialization_alias="chartId")
    result_limit: int = Field(default=100, validation_alias=AliasChoices("resultLimit", "result_limit"), serialization_alias="resultLimit")


class ChartDrillRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chart_id: int | None = Field(default=None, validation_alias=AliasChoices("chartId", "chart_id"), serialization_alias="chartId")
    drill_path: JSONList | None = Field(default=None, validation_alias=AliasChoices("drillPath", "drill_path"), serialization_alias="drillPath")


class DatasetExportRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chart_id: int | None = Field(default=None, validation_alias=AliasChoices("chartId", "chart_id"), serialization_alias="chartId")
    dataset_group_id: int | None = Field(default=None, validation_alias=AliasChoices("datasetGroupId", "dataset_group_id"), serialization_alias="datasetGroupId")
    view_config: JSONValue | None = Field(default=None, validation_alias=AliasChoices("viewConfig", "view_config"), serialization_alias="viewConfig")


class ChartFieldResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    origin_name: str | None = Field(default=None, validation_alias=AliasChoices("originName", "origin_name"), serialization_alias="originName")
    name: str | None = None
    type: str | None = None
    dataease_name: str | None = Field(default=None, validation_alias=AliasChoices("dataeaseName", "dataease_name"), serialization_alias="dataeaseName")
    de_type: int | None = Field(default=None, validation_alias=AliasChoices("deType", "de_type"), serialization_alias="deType")
    de_extract_type: int | None = Field(default=None, validation_alias=AliasChoices("deExtractType", "de_extract_type"), serialization_alias="deExtractType")
    ext_field: int | None = Field(default=None, validation_alias=AliasChoices("extField", "ext_field"), serialization_alias="extField")
    field_short_name: str | None = Field(default=None, validation_alias=AliasChoices("fieldShortName", "field_short_name"), serialization_alias="fieldShortName")


class ChartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str | None = None
    scene_id: int = Field(serialization_alias="sceneId")
    table_id: int | None = Field(default=None, serialization_alias="tableId")
    type: str | None = None
    render: str | None = None
    result_count: int | None = Field(default=None, serialization_alias="resultCount")
    result_mode: str | None = Field(default=None, serialization_alias="resultMode")
    x_axis: JSONValue | None = Field(default=None, serialization_alias="xAxis")
    x_axis_ext: JSONValue | None = Field(default=None, serialization_alias="xAxisExt")
    y_axis: JSONValue | None = Field(default=None, serialization_alias="yAxis")
    y_axis_ext: JSONValue | None = Field(default=None, serialization_alias="yAxisExt")
    ext_stack: JSONValue | None = Field(default=None, serialization_alias="extStack")
    ext_bubble: JSONValue | None = Field(default=None, serialization_alias="extBubble")
    ext_label: JSONValue | None = Field(default=None, serialization_alias="extLabel")
    ext_tooltip: JSONValue | None = Field(default=None, serialization_alias="extTooltip")
    ext_color: JSONValue | None = Field(default=None, serialization_alias="extColor")
    custom_attr: JSONValue | None = Field(default=None, serialization_alias="customAttr")
    custom_style: JSONValue | None = Field(default=None, serialization_alias="customStyle")
    custom_filter: JSONValue | None = Field(default=None, serialization_alias="customFilter")
    drill_fields: JSONValue | None = Field(default=None, serialization_alias="drillFields")
    senior: JSONValue | None = None
    create_by: str | None = Field(default=None, serialization_alias="createBy")
    create_time: int | None = Field(default=None, serialization_alias="createTime")
    update_time: int | None = Field(default=None, serialization_alias="updateTime")
    snapshot: str | None = None
    style_priority: str | None = Field(default=None, serialization_alias="stylePriority")
    chart_type: str | None = Field(default=None, serialization_alias="chartType")
    is_plugin: bool | None = Field(default=None, serialization_alias="isPlugin")
    data_from: str | None = Field(default=None, serialization_alias="dataFrom")
    view_fields: JSONValue | None = Field(default=None, serialization_alias="viewFields")
    refresh_view_enable: bool | None = Field(default=None, serialization_alias="refreshViewEnable")
    refresh_unit: str | None = Field(default=None, serialization_alias="refreshUnit")
    refresh_time: int | None = Field(default=None, serialization_alias="refreshTime")
    linkage_active: bool | None = Field(default=None, serialization_alias="linkageActive")
    jump_active: bool | None = Field(default=None, serialization_alias="jumpActive")
    aggregate: bool | None = None
    flow_map_start_name: JSONValue | None = Field(default=None, serialization_alias="flowMapStartName")
    flow_map_end_name: JSONValue | None = Field(default=None, serialization_alias="flowMapEndName")
    custom_attr_mobile: JSONValue | None = Field(default=None, serialization_alias="customAttrMobile")
    custom_style_mobile: JSONValue | None = Field(default=None, serialization_alias="customStyleMobile")
    sort_priority: JSONValue | None = Field(default=None, serialization_alias="sortPriority")


class ChartDetailResponse(BaseModel):
    chart: ChartResponse
    fields: list[ChartFieldResponse] = Field(default_factory=list)


class ChartDataResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    fields: list[object] = Field(default_factory=list)
    data: object = Field(default_factory=list)
    total: int = 0
    chart_id: int | None = Field(default=None, serialization_alias="chartId")
    scene_id: int | None = Field(default=None, serialization_alias="sceneId")
    error: str | None = None
    type: str | None = None
    render: str | None = None
    x_axis: JSONValue | None = Field(default=None, serialization_alias="xAxis")
    y_axis: JSONValue | None = Field(default=None, serialization_alias="yAxis")
    x_axis_ext: JSONValue | None = Field(default=None, serialization_alias="xAxisExt")
    y_axis_ext: JSONValue | None = Field(default=None, serialization_alias="yAxisExt")
