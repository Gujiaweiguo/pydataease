## ADDED Requirements

### Requirement: Template market cards expose download action
Each template card in the template market page (`full` view mode) SHALL display a download (export) button in the hover area alongside existing preview and apply buttons. Clicking the download button SHALL call `GET /templateManage/export/{id}` and save the returned JSON as a `.DET2` file using FileSaver.

#### Scenario: Download a template from market card
- **WHEN** user hovers over a template card in the market `full` view and clicks the download icon button
- **THEN** the system calls the export API with the template's `id`, receives JSON data, and triggers a browser file download named `{templateName}-TEMPLATE.DET2`

#### Scenario: Download button visible on hover
- **WHEN** user hovers over a template card in the market `full` view
- **THEN** the hover area shows preview, apply, and download buttons

### Requirement: Template market cards expose delete action
Each template card in the template market page (`full` view mode) SHALL display a delete button in the hover area. Clicking delete SHALL show a confirmation dialog before calling `POST /templateManage/delete/{id}/{categoryId}`.

#### Scenario: Delete a template from market card
- **WHEN** user clicks the delete icon button on a template card
- **THEN** a confirmation dialog appears asking the user to confirm deletion

#### Scenario: Confirm template deletion
- **WHEN** user confirms the deletion dialog
- **THEN** the system calls `POST /templateManage/delete/{templateId}/{categoryId}` and refreshes the template list upon success, preserving current filter and category selection

#### Scenario: Cancel template deletion
- **WHEN** user cancels the deletion dialog
- **THEN** no action is taken and the template list remains unchanged

### Requirement: Template market toolbar provides upload button
The template market page (`full` view mode) toolbar SHALL provide an upload (import) button that opens the `DeTemplateImport` dialog for `.DET2`/`.DET2APP` file import.

#### Scenario: Upload button replaces import entry link
- **WHEN** user views the template market page in `full` mode
- **THEN** the toolbar shows an "Upload Template" button in place of the previous "Open Import Entry" navigation button

#### Scenario: Upload opens import dialog
- **WHEN** user clicks the upload button
- **THEN** the `DeTemplateImport` dialog opens, allowing the user to select a `.DET2` or `.DET2APP` file for import

#### Scenario: Successful import refreshes list
- **WHEN** user completes a template import via the dialog
- **THEN** the template market list refreshes to show the newly imported template, preserving current filter and category selection

### Requirement: CRUD actions only appear in full view mode
Upload, download, and delete actions SHALL only be available in the template market `full` view mode. The `marketPreview` and `createPreview` view modes SHALL NOT display these management actions.

#### Scenario: No CRUD in market preview mode
- **WHEN** user is in `marketPreview` view mode
- **THEN** template cards and toolbar do not show upload, download, or delete buttons

#### Scenario: No CRUD in create preview mode
- **WHEN** user is in `createPreview` view mode
- **THEN** the view does not show upload, download, or delete buttons
