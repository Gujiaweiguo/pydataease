from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ApiKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    access_key: str = Field(serialization_alias="accessKey")
    access_secret: str = Field(serialization_alias="accessSecret")
    enable: bool = True
    create_time: int | None = Field(None, serialization_alias="createTime")


class ApiKeyEnableEditor(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    enable: bool = True
