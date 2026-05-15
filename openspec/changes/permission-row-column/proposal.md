## Why

This is the most complex and highest-risk layer. Row and column permissions affect the query execution engine itself: row-level filtering injects WHERE clauses, column-level masking hides or desensitizes fields in query results. This change must not be started until the object-level permission model is stable and the dataset/metadata layer is finalized.

## What Changes

- Add row-permission model: rules that filter dataset rows based on org/role/user/system-variable conditions.
- Add column-permission model: rules that disable, mask, or desensitize dataset fields based on org/role/user.
- Implement query-time injection: when a user queries a dataset, row filters are applied as WHERE clauses and column rules control field visibility.
- Add whitelist support: specific users can be exempted from row/column rules.
- Handle priority: user-level rules override role-level, which overrides org-level.

## Plan Context

- **Plan ID**: `pydataease-system-management-roadmap-v1`
- **Plan file**: `.sisyphus/plans/pydataease-system-management-roadmap-v1.md`
- **Depends on**: `permission-menu-resource`
- **Followed by**: none (final change in roadmap)
- **Phase in plan**: Phase F — task T8

## Capabilities

### New Capabilities
- `row-permission`: Dataset row-level filtering based on org/role/user/system-variable conditions.
- `column-permission`: Dataset field-level visibility control (disable, desensitize, mask).

### Modified Capabilities
- `sql-execution-engine`: Query execution must inject row filters and apply column transformations before returning results.

## Impact

- Adds row-permission and column-permission tables via migration.
- Modifies the SQL execution engine to inject WHERE clauses for row filtering.
- Modifies result processing to apply column masking/hiding.
- Depends heavily on dataset field metadata stability.
- Verification: L0 backend + L1 backend + L2 backend (query execution, external datasource integration).
