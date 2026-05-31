# Capability: organization-model (modified)

## REQUIREMENTS
1. Non-admin users' organization tree MUST only show the organization they belong to, NOT ancestor or descendant organizations.
2. Admin users (user_id=1) continue to see the full organization tree.
3. Resource access boundaries remain org-scoped (existing CoreResourceAcl.oid filtering preserved).

## ACCEPTANCE CRITERIA
- Non-admin user in org X sees only org X in the org tree (no parent, no children)
- Admin user sees all organizations
- Existing role-user bindings and resource ACLs remain functional within the user's org
