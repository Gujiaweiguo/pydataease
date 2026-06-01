# Capability: permission-config-ui (modified)

## REQUIREMENTS
1. The v-permission directive MUST accept capability strings in the format 'resourceType:capability' (e.g., 'dataset:export', 'panel:manage').
2. Valid capabilities: view, manage, authorize, export for each resource type.
3. The interactiveStore MUST expose per-resource capability flags derived from the resource ACL weight.
4. Weight mapping: 1=view, 2=use, 4=export, 7=manage, 9=authorize. Higher weights imply all lower capabilities.

## ACCEPTANCE CRITERIA
- v-permission="['dataset:export']" hides element when user lacks export capability
- v-permission="['panel:manage']" hides element when user lacks manage capability
- Existing v-permission="['panel']" syntax continues to work (backward compatible, checks manage)
- InteractiveStore correctly derives capabilities from weight values
