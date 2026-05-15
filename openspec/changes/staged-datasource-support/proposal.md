## Why

The rewrite has validated core runtime, auth, routing, and frontend compatibility, but datasource support is still too broad to implement safely without an explicit MVP boundary. We need a staged plan now so the team can prove the end-to-end BI flow with a small set of high-value SQL datasources before taking on heavier connectors, non-SQL semantics, and long-tail driver burden.

## What Changes

- Define a first-wave datasource MVP centered on PostgreSQL and MySQL for external SQL connectivity.
- Allow Excel/CSV as an optional first-wave add-on only if demo or import workflows require it, rather than making it a mandatory scope item.
- Standardize the first-wave datasource contract around create connection, test connection, metadata introspection, and read-only query preview.
- Require first-wave datasources to support downstream dataset consumption by chart and dashboard flows, so success is measured on the full BI path rather than connection-only demos.
- Explicitly defer Oracle, SQL Server, ClickHouse, Trino/Presto, Hive, Spark, MongoDB, Elasticsearch, Redis, API datasources, and cloud-warehouse long-tail connectors until after the SQL-first contract is proven.
- Treat datasource-specific advanced capabilities such as write-back, engine-tuned SQL behavior, and connector-specific UX as out of scope for the MVP.

## Capabilities

### New Capabilities
- `sql-datasource-mvp`: Supports the first-wave external datasource contract for PostgreSQL and MySQL, with optional Excel/CSV only when demo/import workflows require it.

### Modified Capabilities
- `sql-execution-engine`: Extend read-only SQL execution requirements so query preview can run against configured external SQL datasources instead of only the current internal execution path.

## Impact

- Affects backend datasource connection management, metadata discovery, and query-preview APIs in `core/pydataease-backend/`.
- Likely affects frontend datasource and dataset flows in `core/core-frontend/` to align UI behavior with the SQL-first MVP boundary.
- Introduces additional driver/runtime responsibility for MySQL alongside existing PostgreSQL-oriented infrastructure; optional Excel/CSV support should only be included if it is required for first-wave demos.
- Defers high-friction connectors that would otherwise expand packaging, dependency, testing, and operational burden before the datasource abstraction is stable.
- Expected verification layers for implementation work: **L0 backend** + **L1 backend** for core logic and API coverage, and **L2 backend** because datasource work touches database/integration/external-service behavior. Release-sensitive rollout should also call out Docker or runnable-environment validation if new drivers or packaging changes are introduced.
