from __future__ import annotations

from typing import TypeAlias

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

JSONDict: TypeAlias = dict[str, object]


class ExportTaskCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    export_from: int | None = Field(
        default=None,
        validation_alias=AliasChoices("exportFrom", "export_from"),
    )
    export_from_type: str | None = Field(
        default=None,
        validation_alias=AliasChoices("exportFromType", "export_from_type"),
    )
    file_name: str | None = Field(
        default=None,
        validation_alias=AliasChoices("fileName", "file_name"),
    )
    params: JSONDict = {}


class ExportTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    user_id: int = Field(serialization_alias="userId")
    file_name: str | None = Field(default=None, serialization_alias="fileName")
    file_size: float | None = Field(default=None, serialization_alias="fileSize")
    file_size_unit: str | None = Field(default=None, serialization_alias="fileSizeUnit")
    export_from: int | None = Field(default=None, serialization_alias="exportFrom")
    export_status: str | None = Field(default=None, serialization_alias="exportStatus")
    export_from_type: str | None = Field(default=None, serialization_alias="exportFromType")
    export_time: int | None = Field(default=None, serialization_alias="exportTime")
    export_progress: str | None = Field(default=None, serialization_alias="exportProgress")
    export_machine_name: str | None = Field(
        default=None, serialization_alias="exportMachineName"
    )
    params: JSONDict
    msg: str | None = None
