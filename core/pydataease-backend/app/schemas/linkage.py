from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class LinkageFieldVO(BaseModel):
    """Mirrors VisualizationLinkageFieldVO — a linkage field mapping."""

    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    linkage_id: int | None = Field(default=None, validation_alias=AliasChoices("linkageId", "linkage_id"), serialization_alias="linkageId")
    source_field: int | None = Field(default=None, validation_alias=AliasChoices("sourceField", "source_field"), serialization_alias="sourceField")
    target_field: int | None = Field(default=None, validation_alias=AliasChoices("targetField", "target_field"), serialization_alias="targetField")
    update_time: int | None = Field(default=None, validation_alias=AliasChoices("updateTime", "update_time"), serialization_alias="updateTime")
    copy_from: int | None = Field(default=None, validation_alias=AliasChoices("copyFrom", "copy_from"), serialization_alias="copyFrom")
    copy_id: int | None = Field(default=None, validation_alias=AliasChoices("copyId", "copy_id"), serialization_alias="copyId")


class DatasetTableFieldDTO(BaseModel):
    """Mirrors DatasetTableFieldDTO for target view fields."""

    model_config = ConfigDict(populate_by_name=True)

    id: int | None = None
    dataset_table_id: int | None = Field(default=None, validation_alias=AliasChoices("datasetTableId", "dataset_table_id"), serialization_alias="datasetTableId")
    origin_name: str | None = Field(default=None, validation_alias=AliasChoices("originName", "origin_name"), serialization_alias="originName")
    name: str | None = None
    de_type: int | None = Field(default=None, validation_alias=AliasChoices("deType", "de_type"), serialization_alias="deType")


class VisualizationLinkageDTO(BaseModel):
    """Mirrors VisualizationLinkageDTO — linkage info per target view."""

    model_config = ConfigDict(populate_by_name=True)

    target_view_id: int | None = Field(default=None, validation_alias=AliasChoices("targetViewId", "target_view_id"), serialization_alias="targetViewId")
    target_view_name: str | None = Field(default=None, validation_alias=AliasChoices("targetViewName", "target_view_name"), serialization_alias="targetViewName")
    target_view_type: str | None = Field(default=None, validation_alias=AliasChoices("targetViewType", "target_view_type"), serialization_alias="targetViewType")
    source_view_id: int | None = Field(default=None, validation_alias=AliasChoices("sourceViewId", "source_view_id"), serialization_alias="sourceViewId")
    linkage_active: bool | None = Field(default=None, validation_alias=AliasChoices("linkageActive", "linkage_active"), serialization_alias="linkageActive")
    table_id: int | None = Field(default=None, validation_alias=AliasChoices("tableId", "table_id"), serialization_alias="tableId")
    linkage_fields: list[LinkageFieldVO] = Field(default_factory=list, validation_alias=AliasChoices("linkageFields", "linkage_fields"), serialization_alias="linkageFields")
    target_view_fields: list[DatasetTableFieldDTO] = Field(default_factory=list, validation_alias=AliasChoices("targetViewFields", "target_view_fields"), serialization_alias="targetViewFields")


class LinkageInfoDTO(BaseModel):
    """Mirrors LinkageInfoDTO — source->target linkage info for getVisualizationAllLinkageInfo."""

    model_config = ConfigDict(populate_by_name=True)

    source_info: str = Field(validation_alias=AliasChoices("sourceInfo", "source_info"), serialization_alias="sourceInfo")
    target_info_list: list[str] = Field(default_factory=list, validation_alias=AliasChoices("targetInfoList", "target_info_list"), serialization_alias="targetInfoList")


class LinkageSaveRequest(BaseModel):
    """Request body for saveLinkage — mirrors VisualizationLinkageRequest fields used in saveLinkage."""

    model_config = ConfigDict(populate_by_name=True)

    dv_id: int = Field(validation_alias=AliasChoices("dvId", "dv_id"), serialization_alias="dvId")
    source_view_id: int = Field(validation_alias=AliasChoices("sourceViewId", "source_view_id"), serialization_alias="sourceViewId")
    target_view_ids: list[str] | None = Field(default=None, validation_alias=AliasChoices("targetViewIds", "target_view_ids"), serialization_alias="targetViewIds")
    resource_table: str = Field(default="core", validation_alias=AliasChoices("resourceTable", "resource_table"), serialization_alias="resourceTable")
    linkage_info: list[VisualizationLinkageDTO] = Field(default_factory=list, validation_alias=AliasChoices("linkageInfo", "linkage_info"), serialization_alias="linkageInfo")


class LinkageUpdateActiveRequest(BaseModel):
    """Request body for updateLinkageActive."""

    model_config = ConfigDict(populate_by_name=True)

    dv_id: int = Field(validation_alias=AliasChoices("dvId", "dv_id"), serialization_alias="dvId")
    source_view_id: int = Field(validation_alias=AliasChoices("sourceViewId", "source_view_id"), serialization_alias="sourceViewId")
    active_status: bool = Field(default=True, validation_alias=AliasChoices("activeStatus", "active_status"), serialization_alias="activeStatus")


class LinkageRemoveRequest(BaseModel):
    """Request body for removeLinkage."""

    model_config = ConfigDict(populate_by_name=True)

    dv_id: int = Field(validation_alias=AliasChoices("dvId", "dv_id"), serialization_alias="dvId")
    source_view_id: int = Field(validation_alias=AliasChoices("sourceViewId", "source_view_id"), serialization_alias="sourceViewId")


class LinkageGatherRequest(BaseModel):
    """Request body for getViewLinkageGather / getViewLinkageGatherArray."""

    model_config = ConfigDict(populate_by_name=True)

    dv_id: int = Field(validation_alias=AliasChoices("dvId", "dv_id"), serialization_alias="dvId")
    source_view_id: int = Field(validation_alias=AliasChoices("sourceViewId", "source_view_id"), serialization_alias="sourceViewId")
    target_view_ids: list[str] = Field(default_factory=list, validation_alias=AliasChoices("targetViewIds", "target_view_ids"), serialization_alias="targetViewIds")
    resource_table: str = Field(default="core", validation_alias=AliasChoices("resourceTable", "resource_table"), serialization_alias="resourceTable")
