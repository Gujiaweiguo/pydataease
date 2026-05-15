from __future__ import annotations

import asyncio
import functools
import uuid
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.export_repo import ExportTaskRepository

P = ParamSpec("P")
T = TypeVar("T")

TERMINAL_TASK_STATUSES = {"RUNNING", "SUCCESS"}


def generate_task_id() -> str:
    return uuid.uuid4().hex


def with_retry(
    max_retries: int = 3,
    backoff_base: float = 0.25,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    attempt += 1
                    if attempt > max_retries:
                        raise
                    await asyncio.sleep(backoff_base * (2 ** (attempt - 1)))

        return wrapper

    return decorator


async def idempotent_task_check(task_id: str, session: AsyncSession) -> bool:
    task = await ExportTaskRepository(session).get_by_id(task_id)
    if task is None:
        return False
    return task.export_status not in TERMINAL_TASK_STATUSES
