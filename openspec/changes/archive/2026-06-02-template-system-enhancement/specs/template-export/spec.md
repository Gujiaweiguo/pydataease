## ADDED Requirements

### Requirement: Export endpoint returns .DET2-compatible JSON
The system SHALL provide `GET /templateManage/export/{template_id}` that returns the specified template's data in `.DET2` file format. The response SHALL be a JSON object with fields compatible with the existing import logic in `DeTemplateImport.vue`.

#### Scenario: Export existing template
- **WHEN** `GET /templateManage/export/{id}` is called with a valid template ID
- **THEN** the response is a JSON object containing: `name`, `dvType` (from `dv_type`), `nodeType` (from `node_type`), `snapshot`, `canvasStyleData` (from `template_style`), `componentData` (from `template_data`), `dynamicData` (from `dynamic_data`), `version` (set to `3`)

#### Scenario: Export non-existent template
- **WHEN** `GET /templateManage/export/{id}` is called with a non-existent template ID
- **THEN** the response has status 404 with an error message

### Requirement: Template management page has export button
The template management page (`views/template/`) SHALL display an "导出" (Export) button for each template. Clicking the button SHALL download a `.DET2` file containing the template's full data.

#### Scenario: Export button downloads .DET2 file
- **WHEN** user clicks the "导出" button on a template in the template management list
- **THEN** a file named `{template_name}-TEMPLATE.DET2` is downloaded containing the template's JSON data

#### Scenario: Export button not shown for category nodes
- **WHEN** the selected item in the template list is a category (folder) node, not a template
- **THEN** no export button is shown (export applies only to template leaf nodes)

### Requirement: Exported file is re-importable
The `.DET2` file produced by the export endpoint SHALL be importable via the existing template import functionality in `DeTemplateImport.vue` without modification.

#### Scenario: Round-trip export then import
- **WHEN** a template is exported to `.DET2` file and then the file is imported via the template import dialog
- **THEN** the imported template preserves the original name, snapshot, style data, component data, and dynamic data (with a new unique ID assigned)
