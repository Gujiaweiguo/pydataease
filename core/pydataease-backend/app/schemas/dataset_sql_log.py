from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class SqlLogCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    table_id: str | None = Field(None, validation_alias=AliasChoices("tableId", "table_id"))
    sql_snapshot: str | None = Field(None, validation_alias=AliasChoices("sqlSnapshot", "sql_snapshot"))
    table_name: str | None = Field(None, validation_alias=AliasChoices("tableName", "table_name"))
    status: str | None = None
    error_msg: str | None = Field(None, validation_alias=AliasChoices("errorMsg", "error_msg"))


class SqlLogListRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    table_id: str | None = Field(None, validation_alias=AliasChoices("tableId", "table_id"))


class SqlLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    table_id: str | None = Field(None, serialization_alias="tableId")
    sql_snapshot: str | None = Field(None, serialization_alias="sqlSnapshot")
    table_name: str | None = Field(None, serialization_alias="tableName")
    create_time: int | None = Field(None, serialization_alias="createTime")
    create_by: str | None = Field(None, serialization_alias="createBy")
    status: str | None = None
    error_msg: str | None = Field(None, serialization_alias="errorMsg")
