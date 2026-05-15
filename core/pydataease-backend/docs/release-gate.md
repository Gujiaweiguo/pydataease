# Python Backend Release Gate

Use this gate before any Java -> Python backend cutover. Every item is PASS/FAIL. Any FAIL blocks release.

## Test and quality gate
- [ ] **Implementation tests**: all existing implementation tests pass (`83+` expected; contract stub failures are excluded from this gate)
- [ ] **Integration test**: `uv run pytest tests/test_integration.py -v` passes
- [ ] **Health endpoint**: `GET /health` returns HTTP 200 and `{"status": "ok"}`
- [ ] **Auth middleware**: invalid or missing tokens are blocked with HTTP 401 on protected endpoints
- [ ] **API domain coverage**: datasource, dataset, chart, visualization, share, export, system, and task endpoints have working CRUD/read paths in implementation tests
- [ ] **WebSocket**: `/websocket` route exists and accepts a connection
- [ ] **Scheduler**: APScheduler startup path is verified and expected jobs are registered
- [ ] **Deployment validation**: `python scripts/validate_deployment.py ...` passes against the release candidate environment

## Build and packaging gate
- [ ] **Dockerfile**: image builds successfully from `core/pydataease-backend/`
- [ ] **Compose**: production compose starts both `pydataease-app` and `pydataease-pg`
- [ ] **Entrypoint/healthcheck**: container starts cleanly and healthcheck succeeds
- [ ] **Migrations**: Alembic upgrade path completes without manual intervention

## Code safety gate
- [ ] **LSP diagnostics**: no Python errors in implementation/documentation helper files changed for this release
- [ ] **No hardcoded secrets**: docs/scripts/examples contain placeholders only
- [ ] **Environment documentation**: `.env.example` documents required runtime variables (`DE_ENV`, `DE_DATABASE_URL`, `DE_SECRET_KEY`, `DE_SHARE_SECRET_KEY`, scheduler knobs)
- [ ] **Operational docs**: cutover runbook and rollback runbook are reviewed by engineering + ops

## Operational pass criteria
Release is approved only if all of the following are true:
1. Required tests are green.
2. Validation confirms health, auth, core API domains, WebSocket, and DB reachability.
3. Observability dashboards and rollback commands are prepared before the change window.
4. DBA, release lead, and QA explicitly sign off.

## Fail criteria
Release is blocked if any of the following occur:
- any implementation or integration test failure
- health/auth/WebSocket/scheduler regression
- Docker or compose startup failure
- unresolved Python diagnostics
- missing env var documentation or presence of real credentials in artifacts
