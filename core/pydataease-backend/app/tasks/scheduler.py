from __future__ import annotations

import asyncio
import importlib
import os
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.dependencies.database import async_session
from app.tasks.cleanup import cleanup_expired_shares, cleanup_old_export_tasks
from app.tasks.export_worker import ExportTaskWorker

_scheduler: Any | None = None
_task_worker: ExportTaskWorker | None = None


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def register_jobs(
    scheduler: Any,
    worker: ExportTaskWorker,
    *,
    cleanup_interval_minutes: int,
    export_poll_interval_seconds: int,
) -> None:
    scheduler.add_job(
        worker.run_pending_exports,
        trigger="interval",
        seconds=export_poll_interval_seconds,
        id="export-task-poller",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        cleanup_old_export_tasks,
        trigger="interval",
        minutes=cleanup_interval_minutes,
        id="cleanup-old-export-tasks",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        cleanup_expired_shares,
        trigger="interval",
        minutes=cleanup_interval_minutes,
        id="cleanup-expired-shares",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )


def configure_scheduler(
    *,
    session_factory: async_sessionmaker[AsyncSession] = async_session,
    scheduler_factory: Callable[[], Any] | None = None,
    cleanup_interval_minutes: int | None = None,
    export_poll_interval_seconds: int | None = None,
    worker: ExportTaskWorker | None = None,
) -> tuple[Any, ExportTaskWorker]:
    global _scheduler, _task_worker
    if _scheduler is not None and _task_worker is not None:
        return _scheduler, _task_worker

    if scheduler_factory is None:
        scheduler_class = getattr(
            importlib.import_module("apscheduler.schedulers.asyncio"),
            "AsyncIOScheduler",
            None,
        )
        if scheduler_class is None:
            raise RuntimeError("apscheduler is required to configure the task scheduler")
        scheduler_factory = scheduler_class
    assert scheduler_factory is not None
    resolved_scheduler_factory = scheduler_factory

    cleanup_minutes = cleanup_interval_minutes or _env_int("DE_TASK_CLEANUP_INTERVAL_MINUTES", 60)
    poll_seconds = export_poll_interval_seconds or _env_int("DE_EXPORT_POLL_INTERVAL_SECONDS", 30)
    _task_worker = worker or ExportTaskWorker(session_factory)
    _scheduler = resolved_scheduler_factory()
    register_jobs(
        _scheduler,
        _task_worker,
        cleanup_interval_minutes=cleanup_minutes,
        export_poll_interval_seconds=poll_seconds,
    )
    return _scheduler, _task_worker


async def start_scheduler(request: Request | None = None) -> Any:
    scheduler, worker = configure_scheduler()
    if request is not None:
        request.app.state.task_scheduler = scheduler
        request.app.state.task_worker = worker
    if not scheduler.running:
        scheduler.start()
    return scheduler


async def shutdown_scheduler(timeout_seconds: float = 5.0) -> None:
    global _scheduler, _task_worker
    if _scheduler is None:
        return
    scheduler = _scheduler
    await asyncio.wait_for(
        asyncio.to_thread(scheduler.shutdown, wait=True),
        timeout=timeout_seconds,
    )
    _scheduler = None
    _task_worker = None


def get_scheduler(request: Request) -> Any:
    scheduler = getattr(request.app.state, "task_scheduler", None)
    if scheduler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task scheduler not initialized",
        )
    return scheduler


def get_task_worker(request: Request) -> ExportTaskWorker:
    worker = getattr(request.app.state, "task_worker", None)
    if worker is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task worker not initialized",
        )
    return worker
