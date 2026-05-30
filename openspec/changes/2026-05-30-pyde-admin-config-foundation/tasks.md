## 1. Capability Parity Matrix

- [x] T01. Build capability parity matrix
  - Produce an 8-domain capability matrix mapping each domain to its current status (exists / partial / stub / missing) across the pydataease codebase.
  - Document the mapping from 8 unique capability domains to 6 OpenSpec changes, including the rationale for why 9 changes was rejected.
  - Define "target parity surface" and "non-target scope" for each capability domain.
  - **Must NOT**: copy official brand/marketing copy; equate documentation titles with implementation boundaries.

## 2. Admin Permission Inventory

- [x] T02. Inventory admin permission boundaries
  - Catalog admin menus, resources, roles, ACL, row-column permissions, and org isolation boundaries needed across all 6 changes.
  - For each change, define management permissions, read-only permissions, public access permissions, and disabled-state behavior.
  - Classify which endpoints must remain public (bootstrap, watermark query) vs. admin-only (settings write, feature flag toggle).
  - Produce a capability-to-permission-point-to-route/menu exposure mapping table.
  - **Must NOT**: rewrite the existing permission framework; merge share/embed public access into standard login permissions.

## 3. Persistent Settings Backbone

- [x] T03. Harden persistent settings backbone
  - Design the migration of `_online_maps`, `_system_params`, and other in-memory admin configurations to persistent `CoreSysSetting` contracts.
  - Define unified key namespace conventions, default values, type classification, compatibility keys, and migration strategy.
  - Set priority for contract-layer and persistence-layer changes to `/sysParameter/*`, `/engine/*`, `/setting/authentication/status`.
  - Define read/write consistency rules for shared configurations (engine config, default login method, system parameters).
  - **Must NOT**: alter existing global token semantics; force structured domains (watermark, sys_variable) back into `CoreSysSetting`.

## 4. Feature Flag Registry

- [x] T04. Define feature-flag and rollback registry
  - Define capability flags for all 6 changes: default state, rollout rules, disabled-state behavior, and rollback impact surface.
  - Establish the minimum rollback principle: "turn off the flag to stop the bleed"; rollback must not require reverting shared token/header semantics.
  - Document dormant schema, compatibility responses, old-config compatibility windows, and deprecation periods.
  - Output a capability registry: key, meaning, applicable change, dependencies, expected behavior when disabled.
  - **Must NOT**: use database rollback as a substitute for capability disablement; require deletion of historical audit or submission records during rollback.

## 5. Verification

- [x] V1. `cd core/pydataease-backend && uv run ruff check .`
- [x] V2. `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py`
- [x] V3. `cd core/pydataease-backend && uv run python -c "from app.main import app; print(app.title)"`
