from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class StaticResourceUploadRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    content: str


class StaticResourceFindRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    resource_id: str = Field(
        validation_alias=AliasChoices("resourceId", "resource_id")
    )
