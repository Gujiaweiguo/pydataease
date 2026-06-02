"""Router for MySQLBot advanced assistant callback API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.limiter import limiter  # pyright: ignore[reportImplicitRelativeImport]
from app.dependencies.mysqlbot_auth import verify_mysqlbot_apikey  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.mysqlbot import (  # pyright: ignore[reportImplicitRelativeImport]
    MysqlBotDatasource,
    MysqlBotField,
    MysqlBotQueryRequest,
    MysqlBotQueryResponse,
    MysqlBotTable,
)
from app.services.mysqlbot_service import MysqlBotService, get_mysqlbot_service  # pyright: ignore[reportImplicitRelativeImport]

router = APIRouter(prefix="/mysqlbot/api", tags=["mysqlbot"])


@router.get("/datasources", response_model=list[MysqlBotDatasource])
@limiter.limit("30/minute")
async def list_datasources(
    request: Request,
    _: str = Depends(verify_mysqlbot_apikey),
    service: MysqlBotService = Depends(get_mysqlbot_service),
) -> list[MysqlBotDatasource]:
    """Return all datasources available in the system."""
    return await service.list_datasources()


@router.get("/datasources/{datasource_id}/tables", response_model=list[MysqlBotTable])
@limiter.limit("30/minute")
async def list_tables(
    request: Request,
    datasource_id: int,
    _: str = Depends(verify_mysqlbot_apikey),
    service: MysqlBotService = Depends(get_mysqlbot_service),
) -> list[MysqlBotTable]:
    """Return all tables in the specified datasource."""
    try:
        return await service.list_tables(datasource_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/datasources/{datasource_id}/tables/{table_name}/fields",
    response_model=list[MysqlBotField],
)
@limiter.limit("30/minute")
async def list_fields(
    request: Request,
    datasource_id: int,
    table_name: str,
    _: str = Depends(verify_mysqlbot_apikey),
    service: MysqlBotService = Depends(get_mysqlbot_service),
) -> list[MysqlBotField]:
    """Return column metadata for the specified table."""
    try:
        return await service.list_fields(datasource_id, table_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/datasources/{datasource_id}/query", response_model=MysqlBotQueryResponse)
@limiter.limit("30/minute")
async def execute_query(
    request: Request,
    datasource_id: int,
    payload: MysqlBotQueryRequest,
    _: str = Depends(verify_mysqlbot_apikey),
    service: MysqlBotService = Depends(get_mysqlbot_service),
) -> MysqlBotQueryResponse:
    """Execute a read-only SQL query on the specified datasource."""
    if not payload.sql or not payload.sql.strip():
        raise HTTPException(status_code=422, detail="SQL query is required")
    try:
        return await service.execute_query(datasource_id, payload.sql)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
