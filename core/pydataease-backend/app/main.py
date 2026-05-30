from contextlib import asynccontextmanager
import os
from typing import cast

# pyright: reportMissingImports=false

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import HTTPException
from starlette.types import ASGIApp
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.core.limiter import limiter  # pyright: ignore[reportImplicitRelativeImport]
from app.core.logging import setup_logging  # pyright: ignore[reportImplicitRelativeImport]
from app.middleware.auth import AuthMiddleware  # pyright: ignore[reportImplicitRelativeImport]
from app.middleware.request_id import RequestIDMiddleware  # pyright: ignore[reportImplicitRelativeImport]
from app.middleware.bigint_json import BigIntJSONResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.middleware.response_wrapper import ResultMessageMiddleware  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.chart import router as chart_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.column_permission import router as column_permission_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.custom_geo import router as custom_geo_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.dataset_sql_log import router as dataset_sql_log_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.datasource import router as datasource_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.dataset import router as dataset_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.dataset_field import router as dataset_field_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.engine import router as engine_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.geo import router as geo_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.static_resource import router as static_resource_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.sync import router as sync_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.sys_variable import router as sys_variable_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.visualization import router as visualization_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.export import router as export_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.login import router as login_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.log import router as log_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.api_key import router as api_key_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.auth import router as auth_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.auth_provider import router as auth_provider_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.embed_control import router as embed_control_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.org import router as org_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.role import router as role_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.relation import router as relation_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.row_permission import router as row_permission_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.share import router as share_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.template import router as template_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.system import router as system_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.task import router as task_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.user import router as user_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.bootstrap import router as bootstrap_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.link_jump import router as link_jump_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.outer_params import router as outer_params_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.visualization_bg import router as visualization_bg_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.visualization_subject import router as visualization_subject_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.watermark import router as watermark_router  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.websocket import router as websocket_router  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.response import ResultMessage  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.config import get_settings  # pyright: ignore[reportImplicitRelativeImport]
from app.settings.seed import seed_defaults  # pyright: ignore[reportImplicitRelativeImport]
from app.tasks import configure_scheduler, shutdown_scheduler  # pyright: ignore[reportImplicitRelativeImport]

settings = get_settings()

# Parse CORS origins from comma-separated string
_cors_origins_str = settings.cors_origins.strip()
cors_origins: list[str] = ["*"] if _cors_origins_str == "*" else [o.strip() for o in _cors_origins_str.split(",") if o.strip()]

# Sync RSA key path to os.environ so rsa_utils can read it via os.environ.get().
# Pydantic Settings loads .env values into model fields but not into os.environ.
if settings.rsa_private_key_path and not os.environ.get("DE_RSA_PRIVATE_KEY_PATH"):
    os.environ["DE_RSA_PRIVATE_KEY_PATH"] = settings.rsa_private_key_path



@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await seed_defaults()
    scheduler, worker = configure_scheduler()
    app.state.task_scheduler = scheduler
    app.state.task_worker = worker
    if not scheduler.running:
        scheduler.start()
    try:
        yield
    finally:
        await shutdown_scheduler()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
api_router = APIRouter(prefix=settings.api_prefix)
api_router.include_router(datasource_router)
api_router.include_router(dataset_router)
api_router.include_router(dataset_field_router)
api_router.include_router(engine_router)
api_router.include_router(login_router)
api_router.include_router(org_router)
api_router.include_router(user_router)
api_router.include_router(role_router)
api_router.include_router(relation_router)
api_router.include_router(row_permission_router)
api_router.include_router(column_permission_router)
api_router.include_router(chart_router)
api_router.include_router(link_jump_router)
api_router.include_router(outer_params_router)
api_router.include_router(template_router)
api_router.include_router(watermark_router)
api_router.include_router(visualization_router)
api_router.include_router(export_router)
api_router.include_router(task_router)
api_router.include_router(share_router)
api_router.include_router(system_router)
api_router.include_router(log_router)
api_router.include_router(api_key_router)
api_router.include_router(bootstrap_router)
api_router.include_router(visualization_bg_router)
api_router.include_router(visualization_subject_router)
api_router.include_router(custom_geo_router)
api_router.include_router(dataset_sql_log_router)
api_router.include_router(geo_router)
api_router.include_router(auth_router)
api_router.include_router(auth_provider_router)
api_router.include_router(embed_control_router)
api_router.include_router(static_resource_router)
api_router.include_router(sys_variable_router)
api_router.include_router(sync_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> BigIntJSONResponse:
    return BigIntJSONResponse(
        status_code=exc.status_code,
        content=ResultMessage(code=exc.status_code, data=None, msg=str(exc.detail)).model_dump(),
    )


app.add_middleware(AuthMiddleware)
app.add_middleware(ResultMessageMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, cast(ASGIApp, _rate_limit_exceeded_handler))  # pyright: ignore[reportArgumentType]
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestIDMiddleware)
app.include_router(api_router)
app.include_router(websocket_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
