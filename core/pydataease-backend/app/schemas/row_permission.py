from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RowPermissionCreateRequest(BaseModel):
    dataset_id: int
    target_type: str = Field(min_length=1, max_length=20)
    target_id: int
    filter_sql: str = Field(min_length=1)
    enabled: bool = True


class RowPermissionUpdateRequest(BaseModel):
    id: int
    filter_sql: str | None = None
    enabled: bool | None = None


class RowPermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    target_type: str
    target_id: int
    filter_sql: str
    enabled: bool
    create_time: int | None = None
    update_time: int | None = None


class RowPermissionListRequest(BaseModel):
    dataset_id: int
