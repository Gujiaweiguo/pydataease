# Capability: sysvar-row-permission

## REQUIREMENTS
1. DataPermissionService.collect_row_filters() MUST resolve "sysvar" target_type rules by substituting the current user's system variable values into the filter_sql.
2. If a user has no value assigned for a referenced system variable, the rule MUST evaluate to default deny (1=0).
3. Sysvar rules have lower priority than user-level rules but higher priority than org-level rules: user > sysvar > role > org.
4. System variables are resolved from the CoreSysVariableUserValue table (or equivalent) filtered by user_id and variable name.

## ACCEPTANCE CRITERIA
- User with sysvar rule "region = ${region}" and assigned variable region='east' sees only eastern region rows
- User with sysvar rule but no assigned variable value gets default deny (no rows visible)
- User-level row rules take precedence over sysvar rules
- Existing user/role/org row permission rules continue to work unchanged
