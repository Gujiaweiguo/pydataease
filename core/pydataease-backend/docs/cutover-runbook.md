# Python Backend Cutover Runbook

## Scope
- Service: `core/pydataease-backend`
- Migration: Java backend -> Python backend
- Runtime target: PostgreSQL + Python app behind the existing `8100` entrypoint/proxy
- Watch window: 30 minutes after traffic cutover

## Roles
- Cutover lead: coordinates go/no-go and timestamps each checkpoint
- App operator: stops Java backend, starts Python backend
- DBA: confirms backups, PostgreSQL migrations, write safety
- QA/SME: executes smoke checks
- Observability owner: watches logs, metrics, error rate

## Preconditions
1. Latest Java/MySQL backup completed and restore tested.
2. PostgreSQL target is reachable and sized for production traffic.
3. Python image/artifact is the approved release candidate.
4. `alembic upgrade head` was validated for the release build.
5. `.env`/secrets for `DE_DATABASE_URL`, `DE_SECRET_KEY`, `DE_SHARE_SECRET_KEY`, scheduler settings, and proxy settings are prepared.
6. Proxy or DNS TTL lowered ahead of the change window.
7. Rollback owner and rollback communication channel confirmed.
8. Release gate in `release-gate.md` is fully PASS before starting.

## Pre-cutover checks
1. Announce cutover start in the release channel.
2. Freeze non-essential admin changes and bulk exports.
3. Confirm MySQL backup timestamp and PostgreSQL snapshot timestamp.
4. Confirm Java backend health is green before shutdown.
5. Confirm Python deployment artifacts are present:
   - application image/container
   - compose/env files
   - Alembic migration files
   - `scripts/validate_deployment.py`
6. Confirm DNS/proxy rollback command is ready.
7. Confirm the team is present for the full watch window.

## Cutover procedure
1. **Start timer and declare go**
   - Record T0.
   - Confirm no blockers from DBA/QA/ops.
2. **Stop writes to the Java stack**
   - Enable maintenance mode or drain traffic at the proxy if available.
   - Stop the Java backend process/container.
   - Verify Java instances are no longer accepting new requests.
3. **Run PostgreSQL migrations**
   - From `core/pydataease-backend/` run the approved Alembic command for the release artifact.
   - Expected result: migration completes without downgrade/retry.
   - Stop and rollback immediately if migration fails.
4. **Run data migration rehearsal/approved data sync step**
   - Use `scripts/migrate_data.py --dry-run` as the operator checklist/reference.
   - Execute the separately approved data load procedure if production data needs a final sync.
   - Confirm row-count spot checks for critical tables before traffic enablement.
5. **Start the Python backend**
   - Start the Python container/process with production environment variables.
   - Confirm app startup logs include scheduler initialization and no fatal import/database errors.
6. **Verify local health**
   - `GET /health` must return HTTP 200 with `{"status": "ok"}`.
   - Confirm database connectivity through startup logs and smoke checks.
7. **Verify auth flow**
   - Confirm protected API without token returns HTTP 401.
   - Confirm valid token or approved login flow can access a protected endpoint.
8. **Smoke test key API domains**
   - Datasource: query/save/validate
   - Dataset: tree/create/details
   - Chart: save/getData
   - Visualization: tree/save/linkage/jump/outer params
   - Share: save/detail/ticket
   - Export/task: create export task + query task status
   - System: menu query
   - WebSocket: connect to `/websocket`
   - Recommended: run `python scripts/validate_deployment.py --base-url <url> ...`
9. **Cut traffic to Python**
   - Update reverse proxy, load balancer, or DNS to point at the Python backend.
   - Confirm only Python instances receive new traffic.
10. **Post-cutover watch window (30 min)**
   - Watch error rate, latency, container restarts, DB connections, and scheduler activity.
   - Re-run targeted smoke tests at 5, 15, and 30 minutes.
   - Track any user-facing issues in the release channel.

## Go / no-go checkpoints
- **Go** if all of the following are true:
  - migrations succeeded
  - Python backend started cleanly
  - `/health` is green
  - auth and protected API checks pass
  - smoke checks pass across all required domains
  - no sustained error spike during first 5 minutes
- **No-go / rollback** if any of the following occur:
  - migration failure
  - app fails to start or connect to PostgreSQL
  - 401/500 regressions on critical endpoints
  - WebSocket endpoint unavailable
  - scheduler fails to initialize
  - data validation shows incorrect or missing critical rows

## Success criteria
- Proxy/DNS points only to Python backend.
- Health, auth, CRUD smoke checks, and WebSocket validation all pass.
- No Sev1/Sev2 incident during the 30-minute watch window.
- Release lead records cutover completion time and signs off with DBA + QA.

## Evidence to capture
- migration command output
- deployment validation script output
- health/auth smoke responses
- proxy or DNS change record
- 30-minute monitoring screenshots/log extracts
