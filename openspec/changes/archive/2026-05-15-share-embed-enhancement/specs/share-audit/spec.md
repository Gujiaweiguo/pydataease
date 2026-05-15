## Requirements

### R1: Ticket access time tracking
When a share access involves a ticket (via `CoreShareTicket`), the system MUST update the `access_time` field to the current timestamp on each access.

### R2: Access event recording
The system MUST record access events for non-ticket share access, including: share UUID, timestamp, and client IP address. These records MUST be queryable by share UUID for audit purposes.

### R3: Access count
The system MUST maintain an access count per share, incrementing on each successful resolution. This count MUST be visible in the share detail response.

### R4: Non-blocking audit
Audit recording MUST NOT block or delay the share resolution response. Audit failures (e.g., DB write errors) MUST be logged but MUST NOT cause the share access to fail.
