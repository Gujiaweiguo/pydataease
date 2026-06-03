## MODIFIED Requirements

### Requirement: Exported file is re-importable
The `.DET2` file produced by the export endpoint SHALL be importable via the existing template import functionality in `DeTemplateImport.vue` without modification, and the product workflow SHALL expose a discoverable user path from export to import.

#### Scenario: Round-trip export then import
- **WHEN** a template is exported to `.DET2` file and then the file is imported via the template import dialog
- **THEN** the imported template preserves the original name, snapshot, style data, component data, and dynamic data (with a new unique ID assigned)

#### Scenario: Export workflow points to import path
- **WHEN** a user exports a reusable `.DET2` template file from an existing visualization or from template management
- **THEN** the product presents or links to a user-visible import path so the exported file can be returned to the local template library without hidden navigation
