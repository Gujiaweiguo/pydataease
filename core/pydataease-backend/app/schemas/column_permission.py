from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ColumnPermissionCreateRequest(BaseModel):
    dataset_id: int
    field_id: int
    target_type: str = Field(min_length=1, max_length=20)
    target_id: int
    action: str = Field(min_length=1, max_length=20)
    enabled: bool = True


class ColumnPermissionUpdateRequest(BaseModel):
    id: int
    action: str | None = None
    enabled: bool | None = None


class ColumnPermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    field_id: int
    target_type: str
    target_id: int
    action: str
    enabled: bool
    create_time: int | None = None
    update_time: int | None = None


class ColumnPermissionListRequest(BaseModel):
    dataset_id: int
