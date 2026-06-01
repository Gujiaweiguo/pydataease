# Capability: datasource-view-only-guard

## REQUIREMENTS
1. When a user has only "view" permission (weight=1) on a datasource, they MUST NOT be able to create new datasets based on that datasource.
2. When a user has only "view" permission on a datasource, they MUST NOT be able to edit existing datasets that depend on that datasource.
3. The enforcement MUST happen at the backend service layer, not just frontend UI.
4. The system MUST return a clear error message: "权限不足，无法操作" or equivalent.

## ACCEPTANCE CRITERIA
- User with view-only datasource permission receives 403 when attempting to create dataset from that datasource
- User with view-only datasource permission receives 403 when attempting to edit dataset linked to that datasource
- User with manage permission on datasource can create and edit datasets normally
- Admin user bypasses all restrictions
