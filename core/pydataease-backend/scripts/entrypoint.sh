#!/bin/bash
set -e

term_handler() {
  if [ -n "${child_pid:-}" ] && kill -0 "$child_pid" 2>/dev/null; then
    kill -TERM "$child_pid" 2>/dev/null || true
    wait "$child_pid"
  fi
}

trap term_handler TERM INT

echo "Running Alembic migrations..."
alembic upgrade head
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port "${DE_PORT:-8000}" &
child_pid=$!
wait "$child_pid"
