# PyDataEase — Python/FastAPI backend
# Multi-stage build: uv sync + slim runtime
# TODO: Replace ghcr.io/astral-sh/uv image with self-hosted registry

FROM python:3.12-slim AS builder

ARG VERSION=dev

WORKDIR /app
# TODO: Replace ghcr.io mirror with self-hosted registry
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

COPY core/pydataease-backend/pyproject.toml core/pydataease-backend/uv.lock ./
RUN uv sync --locked --no-install-project --no-editable

COPY core/pydataease-backend/ .
RUN uv sync --locked --no-editable

FROM python:3.12-slim AS runtime

WORKDIR /app

ARG VERSION=dev

RUN mkdir -p /app/logs /app/static

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PATH=/app/.venv/bin:$PATH \
    DE_PORT=8000

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app
COPY --from=builder /app/alembic /app/alembic
COPY --from=builder /app/alembic.ini /app/alembic.ini
COPY --from=builder /app/scripts /app/scripts
COPY --from=builder /app/pyproject.toml /app/pyproject.toml
COPY --from=builder /app/uv.lock /app/uv.lock

RUN chmod +x /app/scripts/entrypoint.sh

RUN echo "$VERSION" > /app/VERSION

EXPOSE 8100

HEALTHCHECK --interval=15s --timeout=5s --retries=5 --start-period=20s CMD ["python", "scripts/healthcheck.py"]

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
