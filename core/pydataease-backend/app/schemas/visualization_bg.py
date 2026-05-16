from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class BackgroundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str | None = None
    classification: str
    content: str | None = None
    remark: str | None = None
    sort: int | None = None
    upload_time: int | None = Field(None, serialization_alias="uploadTime")
    base_url: str | None = Field(None, serialization_alias="baseUrl")
    url: str | None = None
