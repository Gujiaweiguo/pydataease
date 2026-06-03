## ADDED Requirements

### Requirement: Users can save an existing visualization directly to the local template library
The system SHALL allow a user to save an existing dashboard or screen directly into the local template library without first downloading and re-importing a `.DET2` or `.DET2APP` file.

#### Scenario: Save dashboard directly as reusable template
- **WHEN** a user chooses the direct-save template action from an existing dashboard
- **THEN** the system creates a local template record that can be reused later through the local template workflow

#### Scenario: Save screen directly as reusable template
- **WHEN** a user chooses the direct-save template action from an existing screen
- **THEN** the system creates a local template record that can be reused later through the local template workflow

### Requirement: Direct-save flow captures reusable template metadata
The system SHALL collect the metadata required to store and later identify the template in the local template library, including at minimum a template name and destination category.

#### Scenario: User chooses template name and category
- **WHEN** a user starts the direct-save template flow
- **THEN** the flow prompts for the template name and the local template category before saving

#### Scenario: Saved template retains reusable preview information
- **WHEN** the direct-save flow completes successfully
- **THEN** the resulting local template stores the snapshot and visualization content needed for later preview and reuse
