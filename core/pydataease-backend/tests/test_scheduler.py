from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest

from app.tasks.base import generate_task_id, with_retry
from typing import Any

from app.tasks.export_worker import ExportTaskWorker
from app.tasks.scheduler import configure_scheduler, register_jobs, shutdown_scheduler


class FakeScheduler:
    def __init__(self) -> None:
        self.jobs: list[dict[str, object]] = []
        self.running = False
        self.shutdown_called = False

    def add_job(self, func, trigger: str, **kwargs: object) -> None:
        self.jobs.append({"func": func, "trigger": trigger, **kwargs})

    def start(self) -> None:
        self.running = True

    def shutdown(self, wait: bool = True) -> None:
        self.shutdown_called = wait
        self.running = False


class DummyWorker:
    async def run_pending_exports(self) -> None:
        return None


@pytest.fixture(autouse=True)
async def reset_scheduler_singleton() -> AsyncGenerator[None, None]:
    await shutdown_scheduler()
    yield
    await shutdown_scheduler()


def test_generate_task_id_returns_unique_hex() -> None:
    left = generate_task_id()
    right = generate_task_id()
    assert left != right
    assert len(left) == 32
    assert len(right) == 32


@pytest.mark.asyncio
async def test_with_retry_retries_until_success() -> None:
    attempts = {"count": 0}

    @with_retry(max_retries=2, backoff_base=0)
    async def flaky() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("boom")
        return "ok"

    assert await flaky() == "ok"
    assert attempts["count"] == 3


def test_register_jobs_adds_expected_jobs() -> None:
    scheduler = FakeScheduler()
    worker = DummyWorker()
    register_jobs(
        scheduler,
        worker,  # type: ignore[arg-type]
        cleanup_interval_minutes=60,
        export_poll_interval_seconds=30,
    )
    assert len(scheduler.jobs) == 3
    job_ids = {job["id"] for job in scheduler.jobs}
    assert job_ids == {
        "export-task-poller",
        "cleanup-old-export-tasks",
        "cleanup-expired-shares",
    }


def test_configure_scheduler_returns_singleton() -> None:
    fake_scheduler = FakeScheduler()
    scheduler, worker = configure_scheduler(
        scheduler_factory=lambda: fake_scheduler,
        worker=ExportTaskWorker.__new__(ExportTaskWorker),
        cleanup_interval_minutes=5,
        export_poll_interval_seconds=2,
    )
    scheduler2, worker2 = configure_scheduler()
    assert scheduler is scheduler2
    assert worker is worker2


@pytest.mark.asyncio
async def test_shutdown_scheduler_resets_singleton() -> None:
    fake_scheduler = FakeScheduler()
    _scheduler, _worker = configure_scheduler(
        scheduler_factory=lambda: fake_scheduler,
        worker=ExportTaskWorker.__new__(ExportTaskWorker),
        cleanup_interval_minutes=5,
        export_poll_interval_seconds=2,
    )
    await shutdown_scheduler()
    assert fake_scheduler.shutdown_called is True
