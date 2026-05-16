from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class WatermarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str | None = Field(None, serialization_alias="id")
    version: str | None = Field(
        None,
        validation_alias=AliasChoices("version", "version"),
        serialization_alias="version",
    )
    setting_content: str | None = Field(
        None,
        validation_alias=AliasChoices("settingContent", "setting_content"),
        serialization_alias="settingContent",
    )
    create_by: str | None = Field(
        None,
        validation_alias=AliasChoices("createBy", "create_by"),
        serialization_alias="createBy",
    )
    create_time: int | None = Field(
        None,
        validation_alias=AliasChoices("createTime", "create_time"),
        serialization_alias="createTime",
    )


class WatermarkSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    version: str | None = Field(
        None,
        validation_alias=AliasChoices("version", "version"),
    )
    setting_content: str | None = Field(
        None,
        validation_alias=AliasChoices("settingContent", "setting_content"),
    )
