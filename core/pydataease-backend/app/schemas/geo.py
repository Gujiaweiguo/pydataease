from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class GeoSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str | None = None
    geo_json: dict | None = Field(
        None, validation_alias=AliasChoices("geoJson", "geo_json")
    )


class GeoMappingRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mapping: dict[str, str] | None = None
