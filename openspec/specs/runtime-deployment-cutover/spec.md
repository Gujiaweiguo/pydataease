## Capability: runtime-deployment-cutover (delta)

Delta spec for the `resolve-backend-deferrals` change. Extends the existing `runtime-deployment-cutover` capability with operational cleanup tasks.

### MODIFIED Requirements

#### Requirement: Cleanup tasks SHALL execute real database deletions
Scheduled cleanup tasks SHALL perform actual `DELETE` operations against the database, not just log messages.

##### Scenario: Expired shares cleanup runs
- **WHEN** `cleanup_expired_shares()` is called
- **THEN** all rows in `xpack_share` where `exp IS NOT NULL AND exp < current_epoch_millis` SHALL be deleted
- **AND** the count of deleted rows SHALL be logged at INFO level

##### Scenario: Old export tasks cleanup runs
- **WHEN** `cleanup_old_export_tasks()` is called
- **THEN** all rows in `core_export_task` where `export_status IN ('SUCCESS', 'FAILED') AND export_time < retention_threshold` SHALL be deleted
- **AND** the count of deleted rows SHALL be logged at INFO level

#### Requirement: Export task retention SHALL be configurable
The retention period for completed export tasks SHALL be controlled by the `DE_EXPORT_RETENTION_MS` environment variable.

##### Scenario: Default retention
- **WHEN** `DE_EXPORT_RETENTION_MS` is not set
- **THEN** completed export tasks older than 7 days (604,800,000 ms) SHALL be eligible for cleanup

##### Scenario: Custom retention
- **WHEN** `DE_EXPORT_RETENTION_MS=86400000` (1 day)
- **THEN** completed export tasks older than 1 day SHALL be eligible for cleanup

##### Scenario: Malformed retention value
- **WHEN** `DE_EXPORT_RETENTION_MS=not-a-number`
- **THEN** the default 7-day retention SHALL be used

#### Requirement: Share expiry SHALL compare against epoch milliseconds
Share cleanup SHALL compare the `exp` column (epoch millis) against the current time in epoch millis, and SHALL only delete rows where `exp IS NOT NULL`.

##### Scenario: Share with no expiration
- **WHEN** a share has `exp = NULL`
- **THEN** it SHALL NOT be deleted by the cleanup task

##### Scenario: Share with future expiration
- **WHEN** a share has `exp` greater than the current epoch millis
- **THEN** it SHALL NOT be deleted by the cleanup task

##### Scenario: Share with past expiration
- **WHEN** a share has `exp` less than the current epoch millis
- **THEN** it SHALL be deleted by the cleanup task
