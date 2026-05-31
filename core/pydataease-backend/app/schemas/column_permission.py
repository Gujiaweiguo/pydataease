from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ColumnPermissionCreateRequest(BaseModel):
    dataset_id: int
    field_id: int
    target_type: str = Field(min_length=1, max_length=20)
    target_id: int
    action: str = Field(min_length=1, max_length=20)
    mask_start: int | None = Field(default=None, ge=0)
    mask_end: int | None = Field(default=None, ge=0)
    enabled: bool = True


class ColumnPermissionUpdateRequest(BaseModel):
    id: int
    action: str | None = None
    mask_start: int | None = Field(default=None, ge=0)
    mask_end: int | None = Field(default=None, ge=0)
    enabled: bool | None = None


class ColumnPermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    field_id: int
    target_type: str
    target_id: int
    action: str
    mask_start: int | None = None
    mask_end: int | None = None
    enabled: bool
    create_time: int | None = None
    update_time: int | None = None


class ColumnPermissionListRequest(BaseModel):
    dataset_id: int
