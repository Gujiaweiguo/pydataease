from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field, AliasChoices


JSONDict: TypeAlias = dict[str, object]


class DatasourceBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=50)
    configuration: JSONDict
    description: str | None = None
    pid: int | None = 0
    edit_type: str | None = None
    enable_data_fill: bool | None = None


class DatasourceCreate(DatasourceBase):
    id: int | None = None


class DatasourceUpdate(BaseModel):
    id: int
    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: str | None = Field(default=None, min_length=1, max_length=50)
    configuration: JSONDict | None = None
    description: str | None = None
    pid: int | None = None
    edit_type: str | None = None
    enable_data_fill: bool | None = None


class DatasourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    configuration: JSONDict
    description: str | None = None
    pid: int | None = None
    edit_type: str | None = None
    create_time: int
    update_time: int
    update_by: int | None = None
    create_by: str | None = None
    status: str | None = None
    qrtz_instance: str | None = None
    task_status: str | None = None
    enable_data_fill: bool | None = None


class DatasourceValidateRequest(DatasourceBase):
    id: int | None = None


class DatasourceValidateResponse(BaseModel):
    success: bool
    message: str
    datasource_type: str


class DatasourceTableResponse(BaseModel):
    name: str
    schema_name: str = Field(serialization_alias="schema")
    type: str = "TABLE"


class DatasourceFieldResponse(BaseModel):
    name: str
    data_type: str
    nullable: bool


class EngineInfoResponse(BaseModel):
    configured: bool
    type: str | None = None
    status: str | None = None
    name: str | None = None


class DatasourceMoveRequest(BaseModel):
    id: int
    pid: int


class DatasourceRenameRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str = Field(min_length=1, max_length=128)


class DatasourceFolderRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    pid: int = 0


class DatasourceTablesRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    datasource_id: int = Field(validation_alias=AliasChoices("datasourceId", "datasource_id"))


class DatasourceSimpleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str | None = None
    type: str | None = None
    description: str | None = None
