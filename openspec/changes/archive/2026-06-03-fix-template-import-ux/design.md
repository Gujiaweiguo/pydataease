## Context

The current template workflow is functionally complete but fragmented across multiple frontend surfaces. Users can export reusable `.DET2` files, import `.DET2` and `.DET2APP` files, browse local templates in the template market, and apply local templates later, but those actions live in different pages and dialogs with weak navigation between them.

The main implementation surfaces are all in the frontend: template management (`views/template/`), template market (`views/template-market/`), and resource creation dialogs (`DeResourceCreateOpt*`). Existing backend endpoints for template save, export, and local-market queries already support the required data flow, so the main design problem is how to make the workflow discoverable without breaking the existing file-compatible round trip.

## Goals / Non-Goals

**Goals:**
- Make template import reachable from the main template workflow without relying on hidden pages or tribal knowledge.
- Make the export-to-import-to-reuse path understandable from the user interface.
- Reuse existing backend endpoints and file formats wherever possible.
- Keep local template market behavior consistent with imported templates and existing seeded templates.
- Verify the change primarily with existing frontend gates, only expanding to backend verification if implementation changes backend behavior.

**Non-Goals:**
- Do not redesign the underlying `.DET2` or `.DET2APP` file formats.
- Do not replace the existing template market or template management data model.
- Do not add a new server-side file upload protocol if the current client-side import flow remains sufficient.
- Do not implement direct save-to-template-library in this change; that is covered by a separate change.

## Decisions

### Decision: Treat this as a frontend workflow alignment change first
The existing backend already supports template export, template save, and local template browsing. The design will therefore prioritize visible entry points, navigation, and guidance in the frontend before considering backend changes.

Alternative considered: introduce a new backend import-oriented endpoint for this change.

Why not: the current import flow already reads files client-side and persists parsed template data through existing save APIs. Adding a new backend import surface would increase scope without solving the root discoverability problem.

### Decision: Use one canonical import experience and link to it from other template surfaces
The product currently has multiple places where template-related actions occur. This change will converge on one import experience and make other template surfaces either expose that same import action directly or clearly route users to it.

Alternative considered: duplicate full import UIs independently in template management, template market, and resource creation.

Why not: duplicating import implementations would create drift in accepted file types, validation behavior, and user guidance.

### Decision: Add workflow guidance near existing export and local-template actions
Users are confused less by missing backend support and more by not knowing what to do after exporting a file. The design will place concise guidance close to export/import actions so users can connect `.DET2` reuse with the local template system.

Alternative considered: rely only on documentation or release notes.

Why not: this problem appears inside the active UI workflow, so the product must explain itself at the point of action rather than expecting users to leave the page.

### Decision: Preserve `.DET2` round-trip compatibility as a hard constraint
The existing export/import chain already works and is now part of the defined contract. The UX change must not break the ability to export a template, import it again, and reuse it in the local template market.

Alternative considered: narrow import to one file type or reinterpret `.DET2APP` behavior in this change.

Why not: changing file semantics would turn a workflow-fix change into a compatibility and migration change.

### Decision: Keep verification aligned with implementation scope
This change should primarily require L0 frontend verification (`npm run ts:check`, `npm run lint`, `npm run lint:stylelint`). If routing or packaged behavior changes materially, add frontend build verification. Only if implementation touches backend contracts should L0 backend + L1 backend be added.

Alternative considered: require full backend verification by default.

Why not: this change is expected to stay mostly in the frontend workflow layer, and the repo guidance favors path-scoped verification over full-suite defaults.

## Risks / Trade-offs

- [Too many import entry points remain confusing] → Mitigation: choose one canonical import experience and make other surfaces route into it consistently.
- [UX text becomes verbose or inconsistent across pages] → Mitigation: centralize wording for `.DET2` / `.DET2APP` guidance and reuse it across template surfaces.
- [A frontend-only change exposes hidden backend assumptions] → Mitigation: if implementation reveals contract gaps, explicitly expand scope and verification to backend endpoints rather than patching around mismatches.
- [Users expect direct save-to-template-library from this work] → Mitigation: keep this change narrowly focused on discoverability and route users toward the separate direct-save change for new capability work.

## Migration Plan

No schema or file-format migration is expected. Deployment should be a normal frontend rollout, with rollback handled by reverting the frontend workflow changes if navigation or guidance regresses. If implementation touches route structure or backend response usage, verify those paths before rollout with existing frontend gates and the minimum backend gates required by the affected files.

## Open Questions

- Which existing screen should become the canonical import experience: template management, template market, or resource creation?
- Should template market expose an inline import action, or should it link users into template management for import?
- How much `.DET2` versus `.DET2APP` explanation is necessary before the UI becomes too noisy?
