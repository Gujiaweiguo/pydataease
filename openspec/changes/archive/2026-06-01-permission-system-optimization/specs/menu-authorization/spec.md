# Capability: menu-authorization (modified)

## REQUIREMENTS
1. Menu permission resolution MUST only consider role-based grants (CoreRolePermission).
2. User-direct grants (CoreUserPermission) and org-level grants (CoreOrgPermission) with menu_id permission points MUST NOT affect menu visibility.
3. The CoreUserPermission and CoreOrgPermission tables are preserved for potential future use but are not read during menu resolution.

## ACCEPTANCE CRITERIA
- Menu visibility is determined solely by role permissions
- User with role granting menu X sees menu X regardless of any user-level denials
- Org-level menu grants have no effect on menu visibility
- Existing data in CoreUserPermission and CoreOrgPermission is preserved (not deleted)
