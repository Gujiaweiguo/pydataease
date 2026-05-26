#!/usr/bin/env bash
# dev.sh — Local development environment launcher
# Usage: ./scripts/dev.sh [backend|frontend|all]
# Default: all
#
# Requires: Docker containers postgres16 & mysql8 running,
#           uv (backend), npm (frontend)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$ROOT/core/pydataease-backend"
FRONTEND_DIR="$ROOT/core/core-frontend"
SESSION="dev"

cleanup() {
    echo "Stopping dev environment..."
    tmux kill-session -t "$SESSION" 2>/dev/null || true
}
trap cleanup EXIT

start_backend() {
    echo "Starting backend on port ${DE_PORT:-8000}..."
    tmux new-session  -d -s "$SESSION" -c "$BACKEND_DIR" -n backend
    tmux send-keys -t "$SESSION:backend" "uv run uvicorn app.main:app --host 0.0.0.0 --port ${DE_PORT:-8000} 2>&1" Enter
}

start_frontend() {
    echo "Starting frontend on port 8080..."
    # If backend already created the session, just make a new window; otherwise create session
    if ! tmux has-session -t "$SESSION" 2>/dev/null; then
        tmux new-session  -d -s "$SESSION" -c "$FRONTEND_DIR" -n frontend
    else
        tmux new-window  -t "$SESSION" -c "$FRONTEND_DIR" -n frontend
    fi
    tmux send-keys -t "$SESSION:frontend" "npm run dev 2>&1" Enter
}

ensure_dbs() {
    local need_start=()
    for c in postgres16 mysql8; do
        if ! docker ps --format '{{.Names}}' | grep -qx "$c"; then
            need_start+=("$c")
        fi
    done
    if [ ${#need_start[@]} -gt 0 ]; then
        echo "Starting containers: ${need_start[*]}"
        docker start "${need_start[@]}"
        sleep 2
    fi
}

ensure_dbs

target="${1:-all}"
case "$target" in
    backend)  start_backend ;;
    frontend) start_frontend ;;
    all)      start_backend; sleep 3; start_frontend ;;
    *)        echo "Usage: $0 [backend|frontend|all]"; exit 1 ;;
esac

echo ""
echo "Dev environment ready. Attach with:  tmux attach -t $SESSION"
echo "  Backend window:  tmux select-window -t $SESSION:backend"
echo "  Frontend window: tmux select-window -t $SESSION:frontend"
echo "Press Ctrl+C to stop everything."
echo ""

# Keep script alive so trap works
wait
