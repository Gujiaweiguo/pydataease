## Why

Users can already export an existing dashboard or screen as a `.DET2` or `.DET2APP` file, but they must manually download and re-import that file to turn it into a reusable library template. This creates unnecessary friction for a common workflow and makes existing visualizations feel disconnected from the local template library.

## What Changes

- Add a direct user flow to save an existing dashboard or screen into the local template library without requiring a file download and re-import step.
- Support choosing template metadata needed for reuse, including template name and destination category.
- Ensure newly saved templates appear in the local template market and template management views with reusable metadata and snapshot support.
- Preserve the existing file-based export/import flow for users who still need portable `.DET2` and `.DET2APP` artifacts.
- Verify that direct-save templates can be applied later through the same local template reuse flow as seeded or imported templates.

## Capabilities

### New Capabilities
- `direct-save-to-template-library`: Allow an existing dashboard or screen to be saved directly into the local template library as a reusable template asset.

### Modified Capabilities
- `template-local-market`: Locally saved templates must become visible and reusable through the template market and template management flows.
- `template-export`: Existing export behavior must remain available alongside the new direct-save workflow without changing file compatibility.

## Impact

- Affected frontend code in visualization preview/toolbars, template management, and template market entry points.
- Likely affected backend template save/query paths in `core/pydataease-backend/app/routers/template.py`, related services, repositories, and schemas.
- Expected verification layers are L0 frontend plus L0 backend and L1 backend because this change crosses UI, API, and persistence behavior; L2 is only needed if database schema or release-sensitive packaging changes are introduced.
- If the final implementation adds new persistence fields, migration or integration validation may be required; otherwise this should remain within existing template tables and APIs.
