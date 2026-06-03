## Why

The template import and reuse workflow already exists in code, but users cannot easily discover where to import exported `.DET2` and `.DET2APP` files or how template management, template market, and resource creation entry points relate to each other. This creates support confusion around an existing capability and makes the current template workflow feel broken even when the underlying APIs work.

## What Changes

- Add clear, user-facing import entry points in the template workflow so exported template files can be found and imported without hidden navigation.
- Align template-center, template-management, and resource-creation entry points so users can understand where to import, browse, and reuse templates.
- Add explicit product guidance and UI states for the export→import→reuse flow, including when users should use `.DET2` versus `.DET2APP`.
- Remove ambiguous or disconnected template actions that make the current flow appear unavailable.
- Verify the updated UX against the existing local template market and template export behavior.

## Capabilities

### New Capabilities
- `template-import-flow`: Define the required user-visible import and guidance flow for `.DET2` and `.DET2APP` template reuse across template management, template center, and resource creation.

### Modified Capabilities
- `template-export`: Exported template files must remain round-trip importable and must be presented through a discoverable user workflow.
- `template-local-market`: Template market and related entry points must make import/reuse actions understandable and reachable for local templates.

## Impact

- Affected frontend code in `core/core-frontend/src/views/template/`, `src/views/template-market/`, and template/resource creation dialogs.
- Possible API contract validation against existing template save/export endpoints, but no new external dependency is expected.
- Primary verification layer is L0 frontend (`npm run ts:check`, `npm run lint`, `npm run lint:stylelint`); add frontend build verification if routing or packaging-visible behavior changes.
- If backend contract adjustments become necessary, the change would additionally require L0 backend + L1 backend verification, but the current goal is primarily UX and workflow alignment rather than new backend behavior.
