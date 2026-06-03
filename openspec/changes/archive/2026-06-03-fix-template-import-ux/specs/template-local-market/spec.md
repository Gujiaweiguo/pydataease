## MODIFIED Requirements

### Requirement: Template apply uses local template ID
When a user clicks "应用" on a template with `source=manage`, the system SHALL use `newFrom=new_inner_template` and the template's `id` as `templateId`, and the surrounding template workflow SHALL make import and reuse actions understandable and reachable for local templates.

#### Scenario: Apply a local template
- **WHEN** user clicks "应用" on a template card from the local market
- **THEN** the system opens the dashboard/screen editor with `createType=template` and `templateId` set to the template's database ID

#### Scenario: Local template workflow exposes import path
- **WHEN** a user is in the local template market experience and wants to reuse a previously exported template file
- **THEN** the product exposes a clear path to import that file into the local template system instead of forcing the user to discover a separate hidden page
