from __future__ import annotations

import contextvars
import logging
import sys

from pythonjsonlogger import json as json_logger

from app.settings.config import get_settings

request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")


class RequestIdFilter(logging.Filter):
    """Inject the current request_id (from ContextVar) into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get("")  # type: ignore[attr-defined]
        return True


def setup_logging() -> None:
    """Configure root logger for structured JSON output.

    Called once at application startup (inside the lifespan handler).
    """
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    formatter = json_logger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger",
        },
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root = logging.root
    root.handlers = [handler]
    root.setLevel(log_level)

    # Configure uvicorn loggers to use the same handler
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(logger_name)
        uv_logger.handlers = [handler]
        uv_logger.propagate = False
        uv_logger.setLevel(log_level)
