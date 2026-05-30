## Plan Reference

- PLAN_ID = `pydataease-dataease-capabilities-plan-v1`
- Execution order: 3rd of 6
- Prerequisites: `pyde-admin-config-foundation`
- Subsequent changes: `pyde-multidimensional-embedding`

## Why

System variables, system parameters, outer params, and embedding context each carry runtime values that flow into queries, watermarks, filters, and (eventually) data filing submissions. Today there is no unified resolution contract. Each subsystem resolves parameters its own way, with undocumented priority rules, no conflict strategy, and no shared error handling. This means embedding context can silently override system variables, or a required parameter can resolve to null without any error feedback.

A canonical parameter resolution contract is the connective tissue between Change 2 (watermark variable placeholders), Change 5 (embedding parameter injection), and Change 6 (data filing context). Without it, each of those changes would invent its own resolution logic, creating inconsistencies that are expensive to fix later.

## What Changes

- Define a single canonical parameter resolution contract covering: source identification, precedence ordering, normalization, injection, and audit trail.
- Unify resolution rules for system variables, outer params, embedding context, default values, template placeholders, and future data filing context.
- Clarify the boundary between system variables (runtime context, data filtering, placeholder resolution) and system parameters (global configuration), ensuring they share a resolution chain but not storage semantics.
- Define variable governance: naming conventions, type classification, dataset field binding, value management, resolution visibility, and future write-path usability.
- Link variable CRUD operations to the parameter contract so that variable creation, editing, and deletion respect consistent validation rules.

## Capabilities

### New Capabilities

- `parameter-resolution`: A single canonical parameter resolution contract that defines source priority, conflict resolution, null handling, required-field enforcement, default-value override rules, and error feedback for all parameter sources (system variables, outer params, embedding context, template placeholders, and data filing context).
- `variable-governance`: System variable governance rules covering naming, typing, dataset binding, value management, resolution visibility, permission enforcement, and future write-path readiness.

### Modified Capabilities

- `backend-contract-compatibility`: Extended contracts so variable and parameter resolution endpoints participate in the unified resolution chain with consistent `ResultMessage` wrapping and auth enforcement.

## Impact

- Affected backend code: `app/routers/outer_params.py`, `app/services/outer_params_service.py`, `app/routers/sys_variable.py`, `app/services/sys_variable_service.py`, `app/models/sys_variable.py`, and related tests.
- The parameter resolution contract itself is a shared specification document consumed by Changes 3, 5, and 6. It doesn't create a single implementation file but constrains how each subsystem resolves parameters.
- System variables retain their independent storage model. System parameters retain their independent storage model. The resolution chain unifies how values are read, not how they are stored.
- Watermark text placeholders (Change 2) will use the parameter resolution contract to resolve variable values at runtime.
- Embedding parameter injection (Change 5) will use the same contract for outer params resolution.

## Non-goals

- Will not implement multi-source identity login in this change.
- Will not deliver the data filing submission flow in this change.
- Will not allow different pages to define their own parameter priority rules independently.
- Will not merge system parameter storage into system variable storage or vice versa.
- Will not let variable resolution bypass permission checks or dataset binding validation.

## Gate Layer

- L0: `cd core/pydataease-backend && uv run ruff check .`
- L1: `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
