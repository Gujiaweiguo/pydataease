from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


# --- Target view info (innermost) ---
class OuterParamsTargetViewInfoDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    target_id: str | None = Field(
        None,
        validation_alias=AliasChoices("target_id", "targetId"),
        serialization_alias="targetId",
    )
    params_info_id: str | None = Field(
        None,
        validation_alias=AliasChoices("params_info_id", "paramsInfoId"),
        serialization_alias="paramsInfoId",
    )
    target_view_id: str | None = Field(
        None,
        validation_alias=AliasChoices("target_view_id", "targetViewId"),
        serialization_alias="targetViewId",
    )
    target_ds_id: str | None = Field(
        None,
        validation_alias=AliasChoices("target_ds_id", "targetDsId"),
        serialization_alias="targetDsId",
    )
    target_field_id: str | None = Field(
        None,
        validation_alias=AliasChoices("target_field_id", "targetFieldId"),
        serialization_alias="targetFieldId",
    )
    copy_from: str | None = Field(
        None,
        validation_alias=AliasChoices("copy_from", "copyFrom"),
        serialization_alias="copyFrom",
    )
    copy_id: str | None = Field(
        None,
        validation_alias=AliasChoices("copy_id", "copyId"),
        serialization_alias="copyId",
    )
    match_mode: str | None = Field(
        None,
        validation_alias=AliasChoices("match_mode", "matchMode"),
        serialization_alias="matchMode",
    )


# --- Outer params info (middle layer) ---
class OuterParamsInfoDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    params_info_id: str | None = Field(
        None,
        validation_alias=AliasChoices("params_info_id", "paramsInfoId"),
        serialization_alias="paramsInfoId",
    )
    params_id: str | None = Field(
        None,
        validation_alias=AliasChoices("params_id", "paramsId"),
        serialization_alias="paramsId",
    )
    param_name: str | None = Field(
        None,
        validation_alias=AliasChoices("param_name", "paramName"),
        serialization_alias="paramName",
    )
    checked: bool | None = None
    required: bool | None = None
    default_value: str | None = Field(
        None,
        validation_alias=AliasChoices("default_value", "defaultValue"),
        serialization_alias="defaultValue",
    )
    enabled_default: bool | None = Field(
        None,
        validation_alias=AliasChoices("enabled_default", "enabledDefault"),
        serialization_alias="enabledDefault",
    )
    copy_from: str | None = Field(
        None,
        validation_alias=AliasChoices("copy_from", "copyFrom"),
        serialization_alias="copyFrom",
    )
    copy_id: str | None = Field(
        None,
        validation_alias=AliasChoices("copy_id", "copyId"),
        serialization_alias="copyId",
    )
    # DTO extensions
    dv_id: str | None = Field(
        None,
        validation_alias=AliasChoices("dv_id", "dvId"),
        serialization_alias="dvId",
    )
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
    target_view_info_list: list[OuterParamsTargetViewInfoDTO] | None = Field(
        None,
        validation_alias=AliasChoices("target_view_info_list", "targetViewInfoList"),
        serialization_alias="targetViewInfoList",
    )


# --- Outer params (top level) ---
class VisualizationOuterParamsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    params_id: str | None = Field(
        None,
        validation_alias=AliasChoices("params_id", "paramsId"),
        serialization_alias="paramsId",
    )
    visualization_id: str | None = Field(
        None,
        validation_alias=AliasChoices("visualization_id", "visualizationId", "dvId"),
        serialization_alias="visualizationId",
    )
    checked: bool | None = None
    remark: str | None = None
    copy_from: str | None = Field(
        None,
        validation_alias=AliasChoices("copy_from", "copyFrom"),
        serialization_alias="copyFrom",
    )
    copy_id: str | None = Field(
        None,
        validation_alias=AliasChoices("copy_id", "copyId"),
        serialization_alias="copyId",
    )
    required: bool | None = None
    default_value: str | None = Field(
        None,
        validation_alias=AliasChoices("default_value", "defaultValue"),
        serialization_alias="defaultValue",
    )
    # DTO extensions
    outer_params_info_array: list[OuterParamsInfoDTO] | None = Field(
        None,
        validation_alias=AliasChoices("outer_params_info_array", "outerParamsInfoArray"),
        serialization_alias="outerParamsInfoArray",
    )
    target_info_list: list[str] | None = Field(
        None,
        validation_alias=AliasChoices("target_info_list", "targetInfoList"),
        serialization_alias="targetInfoList",
    )


# --- Response schemas ---
class OuterParamsBaseResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    outer_params_info_map: dict[str, list[str]] | None = Field(
        None,
        validation_alias=AliasChoices("outer_params_info_map", "outerParamsInfoMap"),
        serialization_alias="outerParamsInfoMap",
    )
    outer_params_info_base_map: dict[str, OuterParamsInfoDTO] | None = Field(
        None,
        validation_alias=AliasChoices(
            "outer_params_info_base_map", "outerParamsInfoBaseMap"
        ),
        serialization_alias="outerParamsInfoBaseMap",
    )
