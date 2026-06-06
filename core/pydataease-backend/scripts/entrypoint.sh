#!/bin/bash
set -e

term_handler() {
  if [ -n "${child_pid:-}" ] && kill -0 "$child_pid" 2>/dev/null; then
    kill -TERM "$child_pid" 2>/dev/null || true
    wait "$child_pid"
  fi
}

trap term_handler TERM INT

# 注意：数据库迁移（alembic upgrade head）已由 install.sh / upgrade.sh
# 在独立的一次性容器中执行，不再由 entrypoint 自动运行。
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port "${DE_PORT:-8000}" &
child_pid=$!
wait "$child_pid"
