from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str | None = None
    type: str | None = None
    details: dict | None = None
    delete_flag: bool | None = Field(None, serialization_alias="deleteFlag")
    cover_url: str | None = Field(None, serialization_alias="coverUrl")
    create_num: int = 0
    create_time: int | None = Field(None, serialization_alias="createTime")
    create_by: str | None = Field(None, serialization_alias="createBy")
    update_time: int | None = Field(None, serialization_alias="updateTime")
    update_by: str | None = Field(None, serialization_alias="updateBy")


class SubjectQueryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str | None = None


class SubjectUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    name: str | None = None
    type: str | None = None
    details: dict | None = None
    cover_url: str | None = Field(
        None, validation_alias=AliasChoices("coverUrl", "cover_url")
    )
