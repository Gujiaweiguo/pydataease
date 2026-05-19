from __future__ import annotations

from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field, AliasChoices


JSONDict: TypeAlias = dict[str, object]
JSONList: TypeAlias = list[object]
JSONValue: TypeAlias = JSONDict | JSONList


class DatasourceBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    name: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=50)
    configuration: JSONValue | None = None
    description: str | None = None
    pid: int | None = 0
    edit_type: str | None = Field(default=None, validation_alias=AliasChoices("editType", "edit_type"))
    enable_data_fill: bool | None = Field(default=None, validation_alias=AliasChoices("enableDataFill", "enable_data_fill"))
    sync_setting: JSONDict | None = Field(default=None, validation_alias=AliasChoices("syncSetting", "sync_setting"))


class DatasourceCreate(DatasourceBase):
    id: int | None = None


class DatasourceUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: int
    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: str | None = Field(default=None, min_length=1, max_length=50)
    configuration: JSONValue | None = None
    description: str | None = None
    pid: int | None = None
    edit_type: str | None = Field(default=None, validation_alias=AliasChoices("editType", "edit_type"))
    enable_data_fill: bool | None = Field(default=None, validation_alias=AliasChoices("enableDataFill", "enable_data_fill"))
    sync_setting: JSONDict | None = Field(default=None, validation_alias=AliasChoices("syncSetting", "sync_setting"))


class DatasourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    configuration: JSONValue | None = None
    description: str | None = None
    pid: int | None = None
    edit_type: str | None = Field(None, serialization_alias="editType")
    create_time: int = Field(serialization_alias="createTime")
    update_time: int = Field(serialization_alias="updateTime")
    update_by: int | None = Field(None, serialization_alias="updateBy")
    create_by: str | None = Field(None, serialization_alias="createBy")
    status: str | None = None
    qrtz_instance: str | None = Field(None, serialization_alias="qrtzInstance")
    task_status: str | None = Field(None, serialization_alias="taskStatus")
    enable_data_fill: bool | None = Field(None, serialization_alias="enableDataFill")
    # Fields expected by frontend but not yet populated — return as null defaults
    creator: str | None = None
    sync_setting: dict[str, object] | None = Field(None, serialization_alias="syncSetting")
    api_configuration_str: str | None = Field(None, serialization_alias="apiConfigurationStr")
    params_str: str | None = Field(None, serialization_alias="paramsStr")
    file_name: str | None = Field(None, serialization_alias="fileName")
    size: int | None = None
    last_sync_time: int | None = Field(None, serialization_alias="lastSyncTime")


class DatasourceValidateRequest(DatasourceBase):
    id: int | None = None


class DatasourceValidateResponse(BaseModel):
    success: bool
    message: str
    datasource_type: str


class DatasourceTableResponse(BaseModel):
    name: str
    table_name: str | None = Field(default=None, serialization_alias="tableName")
    schema_name: str = Field(serialization_alias="schema")
    type: str = "TABLE"
    status: str | None = None
    last_update_time: int | None = Field(default=None, serialization_alias="lastUpdateTime")


class DatasourceFieldResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    origin_name: str = Field(serialization_alias="originName")
    data_type: str = Field(serialization_alias="fieldType")
    de_type: int = Field(default=0, serialization_alias="deType")
    type: str | None = Field(default=None, serialization_alias="type")
    nullable: bool = True


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
    create_time: int | None = Field(None, serialization_alias="createTime")
