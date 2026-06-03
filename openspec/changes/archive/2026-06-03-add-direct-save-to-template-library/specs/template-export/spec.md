## MODIFIED Requirements

### Requirement: Exported file is re-importable
The `.DET2` file produced by the export endpoint SHALL be importable via the existing template import functionality in `DeTemplateImport.vue` without modification, and the file-based export/import workflow SHALL remain available alongside the new direct-save-to-template-library workflow.

#### Scenario: Round-trip export then import
- **WHEN** a template is exported to `.DET2` file and then the file is imported via the template import dialog
- **THEN** the imported template preserves the original name, snapshot, style data, component data, and dynamic data (with a new unique ID assigned)

#### Scenario: Direct save does not replace file export
- **WHEN** the product adds a direct-save-to-template-library action for existing visualizations
- **THEN** users can still export reusable `.DET2` files without any change to file compatibility or import expectations
