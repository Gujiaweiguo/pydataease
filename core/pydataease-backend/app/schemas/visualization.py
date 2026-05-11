from __future__ import annotations

from typing import TypeAlias

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

JSONDict: TypeAlias = dict[str, object]
JSONList: TypeAlias = list[object]
JSONValue: TypeAlias = JSONDict | JSONList


class VisualizationTreeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    busi_flag: str = Field(default="data_visualization", validation_alias=AliasChoices("busiFlag", "busi_flag"), serialization_alias="busiFlag")
    weight: int | None = None


class VisualizationFindByIdRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    busi_flag: str | None = Field(default=None, validation_alias=AliasChoices("busiFlag", "busi_flag"), serialization_alias="busiFlag")
    source: str | None = None
    task_id: str | None = Field(default=None, validation_alias=AliasChoices("taskId", "task_id"), serialization_alias="taskId")


class VisualizationSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    name: str
    pid: int | None = 0
    org_id: int | None = Field(default=None, validation_alias=AliasChoices("orgId", "org_id"), serialization_alias="orgId")
    level: int | None = None
    node_type: str = Field(validation_alias=AliasChoices("nodeType", "node_type"), serialization_alias="nodeType")
    type: str | None = None
    canvas_style_data: JSONValue | None = Field(default=None, validation_alias=AliasChoices("canvasStyleData", "canvas_style_data"), serialization_alias="canvasStyleData")
    component_data: JSONValue | None = Field(default=None, validation_alias=AliasChoices("componentData", "component_data"), serialization_alias="componentData")
    mobile_layout: bool | None = Field(default=None, validation_alias=AliasChoices("mobileLayout", "mobile_layout"), serialization_alias="mobileLayout")
    status: int | None = None
    self_watermark_status: int | None = Field(default=None, validation_alias=AliasChoices("selfWatermarkStatus", "self_watermark_status"), serialization_alias="selfWatermarkStatus")
    sort: int | None = None
    remark: str | None = None
    source: str | None = None
    delete_flag: bool | None = Field(default=None, validation_alias=AliasChoices("deleteFlag", "delete_flag"), serialization_alias="deleteFlag")
    version: int | None = None
    content_id: str | None = Field(default=None, validation_alias=AliasChoices("contentId", "content_id"), serialization_alias="contentId")
    check_version: str | None = Field(default=None, validation_alias=AliasChoices("checkVersion", "check_version"), serialization_alias="checkVersion")


class VisualizationUpdateRequest(VisualizationSaveRequest):
    id: int  # pyright: ignore[reportGeneralTypeIssues]


class VisualizationMoveRequest(BaseModel):
    id: int
    pid: int = 0


class VisualizationRenameRequest(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=255)


class VisualizationDeleteRequest(BaseModel):
    id: int


class VisualizationRecentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    size: int = 50
    busi_flag: str | None = Field(default=None, validation_alias=AliasChoices("busiFlag", "busi_flag"), serialization_alias="busiFlag")
    keyword: str | None = None
    type: str | None = None
    asc: bool | None = None


class VisualizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str | None = None
    pid: int | None = None
    org_id: int | None = Field(default=None, serialization_alias="orgId")
    level: int | None = None
    node_type: str | None = Field(default=None, serialization_alias="nodeType")
    type: str | None = None
    canvas_style_data: JSONValue | None = Field(default=None, serialization_alias="canvasStyleData")
    component_data: JSONValue | None = Field(default=None, serialization_alias="componentData")
    mobile_layout: bool | None = Field(default=None, serialization_alias="mobileLayout")
    status: int | None = None
    self_watermark_status: int | None = Field(default=None, serialization_alias="selfWatermarkStatus")
    sort: int | None = None
    create_time: int | None = Field(default=None, serialization_alias="createTime")
    create_by: str | None = Field(default=None, serialization_alias="createBy")
    update_time: int | None = Field(default=None, serialization_alias="updateTime")
    update_by: str | None = Field(default=None, serialization_alias="updateBy")
    remark: str | None = None
    source: str | None = None
    delete_flag: bool | None = Field(default=None, serialization_alias="deleteFlag")
    delete_time: int | None = Field(default=None, serialization_alias="deleteTime")
    delete_by: str | None = Field(default=None, serialization_alias="deleteBy")
    version: int | None = None
    content_id: str | None = Field(default=None, serialization_alias="contentId")
    check_version: str | None = Field(default=None, serialization_alias="checkVersion")


class VisualizationTreeNodeResponse(VisualizationResponse):
    children: list[VisualizationTreeNodeResponse] = Field(default_factory=list)
    leaf: bool | None = None


class StoreFavoritedRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_id: int = Field(validation_alias=AliasChoices("resourceId", "resource_id"), serialization_alias="resourceId")
    resource_type: int = Field(default=0, validation_alias=AliasChoices("resourceType", "resource_type"), serialization_alias="resourceType")


class StoreCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_type: int = Field(default=0, validation_alias=AliasChoices("resourceType", "resource_type"), serialization_alias="resourceType")


class StoreResponse(BaseModel):
    resource_id: int = Field(serialization_alias="resourceId")
    favorited: bool


class LinkageRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dv_id: int | None = Field(default=None, validation_alias=AliasChoices("dvId", "dv_id"), serialization_alias="dvId")
    view_id: int | None = Field(default=None, validation_alias=AliasChoices("viewId", "view_id"), serialization_alias="viewId")
    resource_table: str | None = Field(default=None, validation_alias=AliasChoices("resourceTable", "resource_table"), serialization_alias="resourceTable")
    config: JSONValue | None = None
    active: bool | None = None


class JumpRequest(LinkageRequest):
    target_dv_id: int | None = Field(default=None, validation_alias=AliasChoices("targetDvId", "target_dv_id"), serialization_alias="targetDvId")


class OuterParamsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dv_id: int = Field(validation_alias=AliasChoices("dvId", "dv_id"), serialization_alias="dvId")
    params: JSONValue | None = None
