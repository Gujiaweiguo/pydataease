## Context

The current product already knows how to serialize an existing dashboard or screen into reusable template-compatible data. That logic is used today for file export (`.DET2` / `.DET2APP`) and for local template persistence, but users must bridge the two manually by downloading a file and importing it again.

This change crosses frontend workflow, existing template APIs, and template-market visibility. The affected surfaces include visualization preview/toolbars, template management, and local template market behavior. The key design question is whether direct save should be implemented as a new backend concept or as a new frontend workflow that reuses the current template persistence contract.

## Goals / Non-Goals

**Goals:**
- Let users save an existing dashboard or screen directly into the local template library.
- Reuse existing template data structures so directly saved templates behave like imported and seeded templates.
- Collect the minimum metadata needed for reuse, especially template name and destination category.
- Preserve the current file-based export/import workflow for portable template files.
- Ensure directly saved templates appear in template management and template market and can be applied through the existing local-template flow.

**Non-Goals:**
- Do not remove or deprecate `.DET2` / `.DET2APP` export.
- Do not redesign template storage tables unless implementation reveals a real persistence gap.
- Do not change the semantics of local template apply.
- Do not combine this work with the separate import-UX change beyond shared wording where useful.

## Decisions

### Decision: Reuse the existing template save contract instead of inventing a new template model
The design will keep `visualization_template` as the persistence target and will construct a normal template-save payload from the current visualization state, then persist it through the existing template save API shape.

Alternative considered: introduce a separate direct-save backend model or a distinct persistence path just for visualization-origin templates.

Why not: directly saved templates are still ordinary local templates after creation. A separate model would increase maintenance cost and create unnecessary divergence in listing, applying, exporting, and managing templates.

### Decision: Add a dedicated direct-save user action in visualization surfaces
The product should expose a distinct "save to template library" action from existing dashboard and screen visualization flows, rather than forcing users to reinterpret file export as a library action.

Alternative considered: overload the current export UI so users choose between download and local save from the same action without a new explicit affordance.

Why not: file export and local library save have different user intent. Mixing them under one ambiguous action would repeat the workflow confusion that already exists elsewhere in the template experience.

### Decision: Reuse existing serialization logic where possible
The frontend already knows how to gather snapshot, canvas style, component data, dynamic data, and related visualization content for export. The direct-save flow should reuse that serialization path as much as possible, then send the resulting data to template persistence instead of writing it to disk.

Alternative considered: implement a second independent serialization path specifically for direct save.

Why not: duplicate serialization logic would increase the risk of drift between exported templates and directly saved templates.

### Decision: Collect template metadata before save in the frontend flow
The direct-save flow should prompt for template name and destination category before persistence. This allows the saved template to enter the local library in a user-controlled state rather than requiring a later management cleanup step.

Alternative considered: save immediately with a generated name and default category, then require the user to edit it later.

Why not: that would create low-quality library entries and make the "direct" flow feel incomplete.

### Decision: Keep verification cross-layer but scoped
Because this change touches UI behavior and backend-backed template persistence, verification should include L0 frontend plus L0 backend and L1 backend. L2 should only be required if implementation introduces schema changes or other integration-sensitive behavior.

Alternative considered: verify as frontend-only because the main user action begins in the UI.

Why not: the value of this change depends on successful persistence, local-market visibility, and apply behavior, all of which depend on backend-backed template records.

## Risks / Trade-offs

- [Existing export serialization is too file-oriented to reuse cleanly] → Mitigation: extract shared template-payload construction logic so file export and direct save call the same core path with different destinations.
- [Metadata prompt introduces extra friction] → Mitigation: keep the required fields minimal and prefill sensible defaults from the current visualization name and known categories.
- [Direct-save templates appear inconsistent with imported templates] → Mitigation: persist through the same template schema and verify listing/apply behavior through existing local template flows.
- [Implementation uncovers missing backend API support] → Mitigation: extend the existing template save path minimally instead of creating a parallel template system.

## Migration Plan

No data migration is planned if the existing template tables and save schema are sufficient. Rollout should occur as a normal application change: deploy UI and backend updates together, verify direct save creates a local template record, confirm the template appears in management and market views, and confirm apply behavior still works. If schema changes become necessary during implementation, expand verification to include the repository's L2 migration checks before rollout.

## Open Questions

- Should the direct-save action live in the preview toolbar, editor toolbar, or both?
- Can the current template save endpoint accept all needed fields as-is, or does it need a small contract extension for metadata or snapshot handling?
- Should destination category selection be limited to existing categories, or can the direct-save flow also create a category inline?
