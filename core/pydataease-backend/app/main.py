from contextlib import asynccontextmanager
import os

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import HTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.core.limiter import limiter
from app.core.logging import setup_logging
from app.middleware.auth import AuthMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.bigint_json import BigIntJSONResponse
from app.middleware.response_wrapper import ResultMessageMiddleware
from app.routers.chart import router as chart_router
from app.routers.datasource import router as datasource_router
from app.routers.dataset import router as dataset_router
from app.routers.engine import router as engine_router
from app.routers.visualization import router as visualization_router
from app.routers.export import router as export_router
from app.routers.login import router as login_router
from app.routers.org import router as org_router
from app.routers.share import router as share_router
from app.routers.system import router as system_router
from app.routers.task import router as task_router
from app.routers.bootstrap import router as bootstrap_router
from app.routers.websocket import router as websocket_router
from app.schemas.response import ResultMessage
from app.settings.config import get_settings
from app.tasks import configure_scheduler, shutdown_scheduler

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
api_router.include_router(engine_router)
api_router.include_router(login_router)
api_router.include_router(org_router)
api_router.include_router(chart_router)
api_router.include_router(visualization_router)
api_router.include_router(export_router)
api_router.include_router(task_router)
api_router.include_router(share_router)
api_router.include_router(system_router)
api_router.include_router(bootstrap_router)


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
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestIDMiddleware)
app.include_router(api_router)
app.include_router(websocket_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
