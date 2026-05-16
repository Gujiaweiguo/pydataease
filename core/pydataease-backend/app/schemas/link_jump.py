from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


# --- Target view info (innermost) ---
class LinkJumpTargetViewInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    target_id: int | None = Field(
        None,
        validation_alias=AliasChoices("target_id", "targetId"),
        serialization_alias="targetId",
    )
    link_jump_info_id: int | None = Field(
        None,
        validation_alias=AliasChoices("link_jump_info_id", "linkJumpInfoId"),
        serialization_alias="linkJumpInfoId",
    )
    source_field_active_id: int | None = Field(
        None,
        validation_alias=AliasChoices("source_field_active_id", "sourceFieldActiveId"),
        serialization_alias="sourceFieldActiveId",
    )
    target_view_id: str | None = Field(
        None,
        validation_alias=AliasChoices("target_view_id", "targetViewId"),
        serialization_alias="targetViewId",
    )
    target_field_id: str | None = Field(
        None,
        validation_alias=AliasChoices("target_field_id", "targetFieldId"),
        serialization_alias="targetFieldId",
    )
    copy_from: int | None = Field(
        None,
        validation_alias=AliasChoices("copy_from", "copyFrom"),
        serialization_alias="copyFrom",
    )
    copy_id: int | None = Field(
        None,
        validation_alias=AliasChoices("copy_id", "copyId"),
        serialization_alias="copyId",
    )
    target_type: str | None = Field(
        None,
        validation_alias=AliasChoices("target_type", "targetType"),
        serialization_alias="targetType",
    )
    outer_params_name: str | None = Field(
        None,
        validation_alias=AliasChoices("outer_params_name", "outerParamsName"),
        serialization_alias="outerParamsName",
    )


# --- Link jump info (middle layer) ---
class LinkJumpInfoDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int | None = None
    link_jump_id: int | None = Field(
        None,
        validation_alias=AliasChoices("link_jump_id", "linkJumpId"),
        serialization_alias="linkJumpId",
    )
    link_type: str | None = Field(
        None,
        validation_alias=AliasChoices("link_type", "linkType"),
        serialization_alias="linkType",
    )
    jump_type: str | None = Field(
        None,
        validation_alias=AliasChoices("jump_type", "jumpType"),
        serialization_alias="jumpType",
    )
    window_size: str | None = Field(
        None,
        validation_alias=AliasChoices("window_size", "windowSize"),
        serialization_alias="windowSize",
    )
    target_dv_id: int | None = Field(
        None,
        validation_alias=AliasChoices("target_dv_id", "targetDvId"),
        serialization_alias="targetDvId",
    )
    source_field_id: int | None = Field(
        None,
        validation_alias=AliasChoices("source_field_id", "sourceFieldId"),
        serialization_alias="sourceFieldId",
    )
    content: str | None = None
    checked: bool | None = None
    attach_params: bool | None = Field(
        None,
        validation_alias=AliasChoices("attach_params", "attachParams"),
        serialization_alias="attachParams",
    )
    copy_from: int | None = Field(
        None,
        validation_alias=AliasChoices("copy_from", "copyFrom"),
        serialization_alias="copyFrom",
    )
    copy_id: int | None = Field(
        None,
        validation_alias=AliasChoices("copy_id", "copyId"),
        serialization_alias="copyId",
    )
    # DTO extensions
    source_field_name: str | None = Field(
        None,
        validation_alias=AliasChoices("source_field_name", "sourceFieldName"),
        serialization_alias="sourceFieldName",
    )
    source_jump_info: str | None = Field(
        None,
        validation_alias=AliasChoices("source_jump_info", "sourceJumpInfo"),
        serialization_alias="sourceJumpInfo",
    )
    source_de_type: int | None = Field(
        None,
        validation_alias=AliasChoices("source_de_type", "sourceDeType"),
        serialization_alias="sourceDeType",
    )
    public_jump_id: str | None = Field(
        None,
        validation_alias=AliasChoices("public_jump_id", "publicJumpId"),
        serialization_alias="publicJumpId",
    )
    target_dv_type: str | None = Field(
        None,
        validation_alias=AliasChoices("target_dv_type", "targetDvType"),
        serialization_alias="targetDvType",
    )
    target_view_info_list: list[LinkJumpTargetViewInfo] | None = Field(
        None,
        validation_alias=AliasChoices("target_view_info_list", "targetViewInfoList"),
        serialization_alias="targetViewInfoList",
    )


# --- Link jump (top level) ---
class VisualizationLinkJumpDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int | None = None
    source_dv_id: int | None = Field(
        None,
        validation_alias=AliasChoices("source_dv_id", "sourceDvId", "dvId"),
        serialization_alias="sourceDvId",
    )
    source_view_id: int | None = Field(
        None,
        validation_alias=AliasChoices("source_view_id", "sourceViewId", "viewId"),
        serialization_alias="sourceViewId",
    )
    link_jump_info: str | None = Field(
        None,
        validation_alias=AliasChoices("link_jump_info", "linkJumpInfo"),
        serialization_alias="linkJumpInfo",
    )
    checked: bool | None = None
    copy_from: int | None = Field(
        None,
        validation_alias=AliasChoices("copy_from", "copyFrom"),
        serialization_alias="copyFrom",
    )
    copy_id: int | None = Field(
        None,
        validation_alias=AliasChoices("copy_id", "copyId"),
        serialization_alias="copyId",
    )
    # DTO extensions
    source_info: str | None = Field(
        None,
        validation_alias=AliasChoices("source_info", "sourceInfo"),
        serialization_alias="sourceInfo",
    )
    target_info_list: list[str] | None = Field(
        None,
        validation_alias=AliasChoices("target_info_list", "targetInfoList"),
        serialization_alias="targetInfoList",
    )
    link_jump_info_array: list[LinkJumpInfoDTO] | None = Field(
        None,
        validation_alias=AliasChoices("link_jump_info_array", "linkJumpInfoArray"),
        serialization_alias="linkJumpInfoArray",
    )


# --- Request schemas ---
class LinkJumpBaseRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    source_dv_id: int | None = Field(
        None,
        validation_alias=AliasChoices("source_dv_id", "sourceDvId"),
        serialization_alias="sourceDvId",
    )
    source_view_id: int | None = Field(
        None,
        validation_alias=AliasChoices("source_view_id", "sourceViewId"),
        serialization_alias="sourceViewId",
    )
    source_field_id: int | None = Field(
        None,
        validation_alias=AliasChoices("source_field_id", "sourceFieldId"),
        serialization_alias="sourceFieldId",
    )
    target_dv_id: int | None = Field(
        None,
        validation_alias=AliasChoices("target_dv_id", "targetDvId"),
        serialization_alias="targetDvId",
    )
    target_view_id: int | None = Field(
        None,
        validation_alias=AliasChoices("target_view_id", "targetViewId"),
        serialization_alias="targetViewId",
    )
    link_jump_id: int | None = Field(
        None,
        validation_alias=AliasChoices("link_jump_id", "linkJumpId"),
        serialization_alias="linkJumpId",
    )
    active_status: bool | None = Field(
        None,
        validation_alias=AliasChoices("active_status", "activeStatus"),
        serialization_alias="activeStatus",
    )
    resource_table: str = Field(
        default="core",
        validation_alias=AliasChoices("resource_table", "resourceTable"),
        serialization_alias="resourceTable",
    )


# --- Response schemas ---
class LinkJumpBaseResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    base_jump_info_map: dict[str, LinkJumpInfoDTO] | None = Field(
        None,
        validation_alias=AliasChoices("base_jump_info_map", "baseJumpInfoMap"),
        serialization_alias="baseJumpInfoMap",
    )
    base_jump_info_visualization_map: dict[str, list[str]] | None = Field(
        None,
        validation_alias=AliasChoices(
            "base_jump_info_visualization_map", "baseJumpInfoVisualizationMap"
        ),
        serialization_alias="baseJumpInfoVisualizationMap",
    )


class DatasetTableFieldDTO(BaseModel):
    """Minimal DTO for table fields returned by getTableFieldWithViewId."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int | None = None
    origin_name: str | None = Field(
        None,
        validation_alias=AliasChoices("origin_name", "originName"),
        serialization_alias="originName",
    )
    name: str | None = None
    type: str | None = None
    de_type: int | None = Field(
        None,
        validation_alias=AliasChoices("de_type", "deType"),
        serialization_alias="deType",
    )


class ViewTableFieldDTO(BaseModel):
    """Field info within a view table detail entry."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int | None = None
    origin_name: str | None = Field(
        None,
        validation_alias=AliasChoices("origin_name", "originName"),
        serialization_alias="originName",
    )
    name: str | None = None
    type: str | None = None
    de_type: int | None = Field(
        None,
        validation_alias=AliasChoices("de_type", "deType"),
        serialization_alias="deType",
    )


class ViewTableDetailDTO(BaseModel):
    """Single view with its fields for viewTableDetailList."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int | None = None
    title: str | None = None
    type: str | None = None
    dv_id: int | None = Field(
        None,
        validation_alias=AliasChoices("dv_id", "dvId"),
        serialization_alias="dvId",
    )
    table_fields: list[ViewTableFieldDTO] | None = Field(
        None,
        validation_alias=AliasChoices("table_fields", "tableFields"),
        serialization_alias="tableFields",
    )


class OutParamsJumpDTO(BaseModel):
    """Outer params jump info."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str | None = None
    name: str | None = None
    title: str | None = None
    type: str | None = None


class VisualizationComponentDTO(BaseModel):
    """Response for viewTableDetailList endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    component_data: str = Field(
        "[]",
        validation_alias=AliasChoices("component_data", "componentData"),
        serialization_alias="componentData",
    )
    result: list[ViewTableDetailDTO] = Field(default_factory=list)
    out_params_jump_info: list[OutParamsJumpDTO] = Field(
        default_factory=list,
        validation_alias=AliasChoices("out_params_jump_info", "outParamsJumpInfo"),
        serialization_alias="outParamsJumpInfo",
    )
