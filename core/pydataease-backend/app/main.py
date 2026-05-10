from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.middleware.auth import AuthMiddleware
from app.middleware.response_wrapper import ResultMessageMiddleware
from app.routers.chart import router as chart_router
from app.routers.datasource import router as datasource_router
from app.routers.dataset import router as dataset_router
from app.routers.engine import router as engine_router
from app.routers.visualization import router as visualization_router
from app.routers.export import router as export_router
from app.routers.login import router as login_router
from app.routers.share import router as share_router
from app.routers.system import router as system_router
from app.routers.task import router as task_router
from app.routers.bootstrap import router as bootstrap_router
from app.routers.websocket import router as websocket_router
from app.schemas.response import ResultMessage
from app.settings.config import get_settings
from app.tasks import configure_scheduler, shutdown_scheduler

settings = get_settings()



@asynccontextmanager
async def lifespan(app: FastAPI):
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
api_router.include_router(chart_router)
api_router.include_router(visualization_router)
api_router.include_router(export_router)
api_router.include_router(task_router)
api_router.include_router(share_router)
api_router.include_router(system_router)
api_router.include_router(bootstrap_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ResultMessage(code=exc.status_code, data=None, msg=str(exc.detail)).model_dump(),
    )


app.add_middleware(AuthMiddleware)
app.add_middleware(ResultMessageMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.include_router(websocket_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
