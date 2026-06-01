## Context

The sysvar system currently stores variable values globally in `core_sys_variable_value` — every user resolving `${store_name}` gets the same first value. The official DataEase v2 manual expects per-user variable assignment, where different users can have different variable values that feed into row-level permission filters.

The runtime resolution pipeline (`DataPermissionService._resolve_sysvar_rules()`) already receives a `user` parameter but explicitly discards it with `del user` (line 301). The `WatermarkService._system_variable_sources()` has the same gap.

A stub endpoint `GET /user/personSysVariableInfo/{uid}` exists in the backend router and frontend API client, returning `{}` — ready for implementation.

## Goals / Non-Goals

**Goals:**
- Allow assigning variable values to specific users (user-scoped values)
- Resolution priority: user-scoped value > global value (user_id IS NULL) > default deny
- Frontend UI for selecting users when creating/editing variable values
- Implement `personSysVariableInfo/{uid}` endpoint for viewing a user's resolved variables
- Maintain backward compatibility: existing global values (user_id IS NULL) continue to work

**Non-Goals:**
- Per-role or per-org variable values (only user-level for now)
- Variable value inheritance chains (e.g., org → role → user)
- Dataset-bound variable value resolution (already works via dataset binding on the variable itself)

## Decisions

### 1. Nullable user_id on existing table vs. separate join table

**Decision**: Add nullable `user_id` column to `core_sys_variable_value`.

**Rationale**: A separate join table would add complexity for a 1:N relationship (one value can belong to one user). A nullable column allows `user_id IS NULL` for global values and `user_id = <uid>` for user-scoped values. This is the simplest model that covers the official manual's behavior.

**Alternative considered**: A new `core_sys_variable_value_user` join table — rejected because it adds an extra table and JOINs for no additional capability.

### 2. Resolution priority: first-wins with user preference

**Decision**: Modify `_fetch_sysvar_values()` to query with `ORDER BY user_id IS NULL, sv.id ASC` — user-scoped values sort before global ones, then first-wins per variable name.

**Rationale**: This preserves the existing first-wins dedup logic while making user-scoped values take priority. Minimal change to the existing query pattern.

### 3. Frontend user selector pattern

**Decision**: Reuse the `el-select multiple` + `userOptionForRoleApi` pattern from the role management page. Add a user selector to the value create/edit dialog.

**Rationale**: Consistent UX with existing role-user assignment. No need for a new shared component — the pattern is well-established.

### 4. personSysVariableInfo endpoint

**Decision**: Implement `GET /user/personSysVariableInfo/{uid}` to return all variables with their resolved values for the given user, using the same resolution priority.

**Rationale**: The stub already exists. This provides a preview/debug view for admins to verify per-user variable resolution.

## Risks / Trade-offs

- **[Migration]** Adding nullable column is backward compatible → no data loss, no rollback complexity
- **[Performance]** The `ORDER BY user_id IS NULL` adds a sort, but sysvar resolution is per-request with small result sets → acceptable
- **[Ambiguity]** If multiple user-scoped values exist for the same variable + user → first-wins (by create_time ASC) → documented behavior, admin should configure carefully
- **[WatermarkService]** Same resolution pattern applies → consistent but adds a second code path to test
