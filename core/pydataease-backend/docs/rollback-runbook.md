# Python Backend Rollback Runbook

## Rollback target
Return traffic from the Python/PostgreSQL stack to the previously healthy Java backend.

## Rollback objective
- Restore customer traffic in **< 5 minutes** once rollback is declared.
- Preserve evidence needed for later root-cause analysis.

## Rollback triggers
Declare rollback if any of the following occur after cutover:
- `/health` fails or flaps on the Python backend
- protected API smoke tests fail repeatedly
- datasource/dataset/chart/visualization/share/export/task/system checks fail in a user-impacting way
- PostgreSQL connectivity or migration issues block normal operation
- WebSocket endpoint cannot connect
- sustained elevated 5xx rate, restart loop, or severe latency regression
- data written after cutover cannot be trusted

## Immediate actions
1. Announce rollback decision in the release channel.
2. Freeze further operator changes until rollback stabilizes.
3. Capture timestamps, failing checks, and impacted domains.

## Rollback procedure
1. **Switch traffic back to Java**
   - Revert proxy/load balancer/DNS to the last-known-good Java backend target.
   - Prefer proxy flip over DNS if both are available because it converges faster.
2. **Verify Java backend availability**
   - Confirm Java instances/processes are running.
   - Verify Java health endpoint/application landing checks are green.
   - Confirm requests are reaching Java again.
3. **Block or stop Python writes**
   - Drain or stop the Python backend to avoid split-brain writes.
   - Preserve Python logs and container state for analysis.
4. **Run focused smoke checks on Java**
   - login/auth
   - core CRUD path used by customers
   - share/export path if affected
5. **Data consistency check**
   - Determine whether any writes landed in PostgreSQL after cutover.
   - Record impacted tables, approximate counts, and affected users/time window.
   - Do not attempt ad-hoc back-sync during the incident unless explicitly approved by DBA + release lead.
6. **Monitor after rollback**
   - Observe Java stack for at least 30 minutes.
   - Confirm customer-facing errors return to baseline.

## Data handling after rollback
- If **no writes** reached PostgreSQL, mark the Python database state as disposable for the next rehearsal.
- If **writes did reach PostgreSQL**, record:
  - table names
  - primary key ranges or timestamps
  - whether data must be replayed into MySQL later
- Any replay or reconciliation must happen in a separate approved recovery task.

## Exit criteria
- Java backend is serving all traffic.
- Customer smoke checks pass on Java.
- Python backend is drained/stopped.
- Release lead, DBA, and QA agree the incident is stabilized.

## Evidence to retain
- failing Python health/smoke outputs
- proxy/DNS rollback record
- Java validation outputs after rollback
- summary of PostgreSQL writes during rollback window
- incident timeline with start, rollback declaration, and stabilization time
