from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class SysVariableQueryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    keyword: str | None = None
    name: str | None = None
    type: str | None = None


class SysVariableCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=255)
    alias: str | None = None
    type: str | None = None
    remark: str | None = None
    dataset_group_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("datasetGroupId", "dataset_group_id"),
        serialization_alias="datasetGroupId",
    )
    dataset_table_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("datasetTableId", "dataset_table_id"),
        serialization_alias="datasetTableId",
    )


class SysVariableEditRequest(SysVariableCreateRequest):
    id: int


class SysVariableValuePageRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    variable_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("variableId", "variable_id", "sysVariableId", "sys_variable_id"),
        serialization_alias="variableId",
    )
    keyword: str | None = None


class SysVariableValueCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    variable_id: int = Field(
        validation_alias=AliasChoices("variableId", "variable_id", "sysVariableId", "sys_variable_id"),
        serialization_alias="variableId",
    )
    user_id: int | None = Field(
        default=None,
        validation_alias=AliasChoices("userId", "user_id"),
        serialization_alias="userId",
    )
    value: str = Field(min_length=1)
    name: str | None = None
    remark: str | None = None


class SysVariableValueEditRequest(SysVariableValueCreateRequest):
    id: int


class SysVariableValueBatchDeleteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ids: list[int] = Field(default_factory=list)


class SysVariableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    alias: str | None = None
    type: str | None = None
    remark: str | None = None
    dataset_group_id: int | None = Field(default=None, serialization_alias="datasetGroupId")
    dataset_table_id: int | None = Field(default=None, serialization_alias="datasetTableId")
    create_time: int | None = Field(default=None, serialization_alias="createTime")
    update_time: int | None = Field(default=None, serialization_alias="updateTime")
    create_by: int | None = Field(default=None, serialization_alias="createBy")


class SysVariableValueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    variable_id: int = Field(serialization_alias="variableId")
    user_id: int | None = Field(default=None, serialization_alias="userId")
    value: str
    name: str | None = None
    remark: str | None = None
    create_time: int | None = Field(default=None, serialization_alias="createTime")
    update_time: int | None = Field(default=None, serialization_alias="updateTime")


class SysVariableValuePageResponse(BaseModel):
    records: list[SysVariableValueResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = Field(default=10, serialization_alias="pageSize")
