## MODIFIED Requirements

### Requirement: Template market reads from local database
The `TemplateMarketService` SHALL query the `visualization_template` table to populate template market content. All returned content items SHALL have `source=manage`, including templates created by the new direct-save-to-template-library workflow.

#### Scenario: Search returns local templates
- **WHEN** `GET /templateMarket/search` is called
- **THEN** the response contains `contents` array where each item is mapped from `visualization_template` records with fields: `id`, `title` (from `name`), `thumbnail` (from `snapshot`), `templateType` (from `dv_type`), `source="manage"`, `classify`, `categoryNames`, and `metas`

#### Scenario: Search with no templates in database
- **WHEN** `GET /templateMarket/search` is called and `visualization_template` has no `node_type=template` records
- **THEN** the response contains `contents: []` and `categories: []`

#### Scenario: Recommend returns latest templates
- **WHEN** `GET /templateMarket/searchRecommend` is called
- **THEN** the response contains at most 8 templates from `visualization_template` ordered by `create_time` descending

#### Scenario: Directly saved templates appear in local market
- **WHEN** a user saves a dashboard or screen through the direct-save-to-template-library workflow
- **THEN** the created template is returned through the same local template market queries as imported and seeded templates

### Requirement: Template apply uses local template ID
When a user clicks "应用" on a template with `source=manage`, the system SHALL use `newFrom=new_inner_template` and the template's `id` as `templateId`, including templates created by direct save.

#### Scenario: Apply a local template
- **WHEN** user clicks "应用" on a template card from the local market
- **THEN** the system opens the dashboard/screen editor with `createType=template` and `templateId` set to the template's database ID

#### Scenario: Apply a directly saved template
- **WHEN** user clicks "应用" on a template that was created through the direct-save-to-template-library workflow
- **THEN** the system opens the dashboard or screen editor through the same local-template apply flow used for seeded and imported templates
