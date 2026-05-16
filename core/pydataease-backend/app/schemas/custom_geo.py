from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class CustomGeoAreaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str | None = None
    create_by: str | None = Field(None, serialization_alias="createBy")
    create_time: int | None = Field(None, serialization_alias="createTime")
    update_by: str | None = Field(None, serialization_alias="updateBy")
    update_time: int | None = Field(None, serialization_alias="updateTime")


class CustomGeoAreaCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = None
    name: str


class CustomGeoSubAreaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    geo_area_id: str | None = Field(None, serialization_alias="geoAreaId")
    name: str | None = None
    geo_json: dict | None = Field(None, serialization_alias="geoJson")


class CustomGeoSubAreaCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    geo_area_id: str = Field(validation_alias=AliasChoices("geoAreaId", "geo_area_id"))
    name: str
    geo_json: dict | None = Field(None, validation_alias=AliasChoices("geoJson", "geo_json"))
