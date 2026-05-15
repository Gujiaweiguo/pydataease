## Context

The FastAPI rewrite already has working auth, routing, dataset-adjacent flows, and frontend compatibility, but external datasource support is still at the point where scope decisions matter more than connector count. The change needs to prove that the rewritten stack can support the core BI path for external data without inheriting the full connector surface area, driver burden, or datasource-specific behavior of the legacy platform on day one.

This change is intentionally SQL-first. PostgreSQL and MySQL are the first-wave targets because they cover the most common relational BI workflows while keeping the Python runtime, packaging, and metadata/query abstractions manageable. Optional Excel/CSV is treated as a demo/import convenience, not as a required architecture anchor.

## Goals / Non-Goals

**Goals:**
- Define a single first-wave datasource contract that covers create connection, test connection, metadata introspection, and read-only query preview.
- Keep the first-wave implementation constrained to PostgreSQL and MySQL, with one shared relational flow rather than datasource-specific UX or API branches.
- Reuse the existing SQL preview safety model so dataset authoring and preview stay read-only.
- Make success depend on downstream dataset consumption by chart and dashboard flows, not just connection validation.
- Keep implementation verifiable with the repository’s existing backend gate layers: L0 backend, L1 backend, and L2 backend for integration-sensitive datasource work.

**Non-Goals:**
- Oracle, SQL Server, ClickHouse, Trino/Presto, Hive, Spark, MongoDB, Elasticsearch, Redis, API datasources, and cloud-warehouse long-tail connectors.
- Datasource-specific advanced features such as write-back, query acceleration knobs, engine-specific SQL rewrites, or per-connector frontend specialization.
- Treating Excel/CSV as a mandatory first-wave requirement.
- Full release validation at this stage; Docker packaging and runnable-environment validation remain release-sensitive follow-on checks, not proposal/design completion gates.

## Decisions

### 1. Use a SQL-first datasource abstraction rather than a universal connector abstraction
The first wave will model datasource support around a relational contract: connection config, connectivity validation, metadata browsing, and read-only SQL preview.

**Why:** PostgreSQL and MySQL share enough metadata and query behavior to validate the rewrite with one abstraction. Starting with SQL reduces architectural risk and avoids prematurely designing around document, search, or API-shaped datasources.

**Alternatives considered:**
- **Universal datasource abstraction from day one:** rejected because it would force the MVP to account for non-SQL semantics before the core BI path is proven.
- **Connector-by-connector custom flows:** rejected because it creates frontend and backend branching too early.

### 2. Keep PostgreSQL and MySQL as the only required first-wave external datasources
The MVP requires PostgreSQL and MySQL support, and treats all other connectors as deferred until the SQL-first contract is stable.

**Why:** These two cover the most common external SQL workflows while keeping the Python dependency surface, query semantics, and metadata discovery logic relatively predictable.

**Alternatives considered:**
- **Add Oracle or SQL Server in wave one:** rejected because driver/runtime friction and dialect differences would expand scope before the contract is validated.
- **PostgreSQL-only MVP:** rejected because MySQL coverage is important enough that excluding it would undercut first-wave business value.

### 3. Make Excel/CSV optional and implementation-dependent
Excel/CSV may be included in the first wave only if demo or import workflows require it, but the architecture must not depend on file datasources to prove the external datasource contract.

**Why:** File-based flows are useful for demos, but they are not necessary to validate the relational datasource abstraction. Making them optional prevents a demo-friendly path from distorting the SQL-first architecture.

**Alternatives considered:**
- **Require Excel/CSV in the MVP:** rejected because it adds file ingestion scope that is independent from relational connectivity.

### 4. Route query preview through datasource-aware execution instead of assuming the internal runtime database
The existing SQL execution engine remains read-only, but it must become datasource-aware so preview requests are executed against the selected configured datasource.

**Why:** Query preview is part of the datasource authoring loop. A connection model that can browse metadata but cannot preview SQL against the chosen datasource would not prove the BI path.

**Alternatives considered:**
- **Keep a datasource-agnostic preview layer backed by the internal runtime DB:** rejected because it would create false validation and fail to prove external connectivity.
- **Allow direct unrestricted SQL execution:** rejected because it would bypass the existing read-only safety model.

### 5. Define completion in terms of downstream dataset consumption
Implementation is not complete when connections work; it is complete when datasets sourced from PostgreSQL/MySQL can be consumed by existing chart and dashboard flows.

**Why:** The product value is BI consumption, not datasource registration. This prevents the team from declaring success on half-integrated backend APIs.

**Alternatives considered:**
- **Connection-only MVP:** rejected because it does not prove that the rewrite can support real user workflows.

### 6. Use existing verification layers rather than inventing new release gates
Implementation work for this change should target L0 backend + L1 backend as the default minimum, with L2 backend required because datasource work touches database/integration/runtime behavior. L3 remains release-sensitive and should only be required when a runnable environment is part of the rollout decision.

**Why:** The repository already has gate definitions that match the current codebase. Reusing them keeps the change consistent with existing verification expectations.

## Risks / Trade-offs

- **[Risk] PostgreSQL and MySQL still diverge in metadata and driver behavior** → **Mitigation:** keep the first-wave contract minimal and normalize only the fields needed for datasource browsing and query preview.
- **[Risk] Optional Excel/CSV creates ambiguity about whether it belongs in the first implementation slice** → **Mitigation:** treat it as a separate scoping decision during tasks planning; do not block the SQL-first path on file ingestion.
- **[Risk] Query preview against external datasources may expose latency, connectivity, or permission failures not seen in the internal DB path** → **Mitigation:** preserve explicit connection test flows and make preview failures visible rather than silently falling back.
- **[Risk] Stakeholders may push to add one more datasource once the abstraction exists** → **Mitigation:** keep deferred connectors explicitly documented as out of scope until first-wave acceptance criteria are satisfied.
- **[Risk] Packaging and runtime dependencies may become more complex once MySQL drivers are added** → **Mitigation:** require L2 validation for implementation work that changes integration/runtime behavior, and defer release-sensitive packaging validation to the release workflow.

## Migration Plan

1. Implement the datasource contract for PostgreSQL and MySQL only.
2. Wire datasource-aware metadata and query-preview behavior into the existing dataset authoring flow.
3. Verify with L0 + L1 + L2 gates for implementation changes, including integration-sensitive checks when drivers/runtime setup change.
4. Confirm at least one full BI path works end-to-end: connection → metadata browse → query preview → dataset → chart/dashboard consumption.
5. Hold deferred datasource types outside the rollout until first-wave failure modes and abstraction gaps are understood.

Rollback is straightforward at this stage because the change is additive: if a connector path is unstable, the rollout can be limited back to already-supported internal flows while datasource work remains behind the change boundary.

## Open Questions

- Should Excel/CSV be included in the first task breakdown, or explicitly deferred to a follow-up change after PostgreSQL/MySQL are stable?
- What is the minimum metadata shape the frontend requires to keep one generic SQL datasource flow across PostgreSQL and MySQL?
- Do release-phase packaging checks need additional system libraries or container changes for the chosen MySQL driver?
