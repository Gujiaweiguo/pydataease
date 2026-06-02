"""Pydantic schemas for MySQLBot advanced assistant callback API."""

from __future__ import annotations

from pydantic import BaseModel


class MysqlBotField(BaseModel):
    id: int | None = None
    name: str | None = None
    type: str | None = None
    comment: str | None = None


class MysqlBotTable(BaseModel):
    id: int | None = None
    name: str | None = None
    comment: str | None = None
    rule: str | None = None
    sql: str | None = None
    fields: list[MysqlBotField] | None = None


class MysqlBotDatasource(BaseModel):
    """A datasource returned to MySQLBot — matches AssistantOutDsSchema.

    MySQLBot's advanced assistant calls one endpoint to get a list of datasources
    with connection credentials. It then connects directly to the databases.
    """

    model_config = {"populate_by_name": True}

    id: int | str | None = None
    name: str
    type: str | None = None
    type_name: str | None = None
    comment: str | None = None
    description: str | None = None
    configuration: str | None = None
    host: str | None = None
    port: int | str | None = None
    dataBase: str | None = None
    user: str | None = None
    password: str | None = None
    db_schema: str | None = None
    extraParams: str | None = None
    mode: str | None = None
    tables: list[MysqlBotTable] | None = None


class MysqlBotQueryRequest(BaseModel):
    sql: str


class MysqlBotQueryResponse(BaseModel):
    fields: list[str]
    data: list[list[object]]
    total: int
