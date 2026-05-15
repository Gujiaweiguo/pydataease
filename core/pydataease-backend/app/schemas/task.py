from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.export import JSONDict


class TaskStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    user_id: int = Field(serialization_alias="userId")
    file_name: str | None = Field(default=None, serialization_alias="fileName")
    export_status: str | None = Field(default=None, serialization_alias="exportStatus")
    export_progress: str | None = Field(default=None, serialization_alias="exportProgress")
    export_from: int | None = Field(default=None, serialization_alias="exportFrom")
    export_from_type: str | None = Field(default=None, serialization_alias="exportFromType")
    export_time: int | None = Field(default=None, serialization_alias="exportTime")
    msg: str | None = None
    params: JSONDict = {}


class TaskRetryResponse(BaseModel):
    task_id: str = Field(serialization_alias="taskId")
    status: str
    msg: str = "success"
