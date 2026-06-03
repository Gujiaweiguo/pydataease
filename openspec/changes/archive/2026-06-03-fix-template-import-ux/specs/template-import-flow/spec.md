## ADDED Requirements

### Requirement: Users can reach template import from the template workflow
The system SHALL provide a user-visible import path for existing `.DET2` and `.DET2APP` files from the template workflow without requiring hidden or indirect navigation.

#### Scenario: Import entry is reachable from template management
- **WHEN** a user opens the template management experience to manage reusable templates
- **THEN** the UI exposes a visible import action for supported template files

#### Scenario: Import path is understandable from template center context
- **WHEN** a user is browsing templates from the template center or template market context
- **THEN** the UI provides a clear path to the import experience or guidance that tells the user where to import template files

### Requirement: The workflow explains export file usage
The system SHALL explain how exported template files are reused so users can distinguish when to use `.DET2` and when to use `.DET2APP`.

#### Scenario: Export guidance is shown for reusable templates
- **WHEN** a user encounters template import or export actions in the template workflow
- **THEN** the UI explains which file type is intended for reusable template import and which file type is intended for application-style export

#### Scenario: Guidance does not imply missing capability
- **WHEN** the user follows the export-to-import workflow
- **THEN** the UI makes it clear that the imported result becomes part of the reusable local template flow rather than appearing as an unrelated file operation
