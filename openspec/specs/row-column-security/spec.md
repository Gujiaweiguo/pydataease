# Capability: row-column-security (modified)

## REQUIREMENTS
1. Column permission rules MUST support custom mask range parameters: mask_start (int) and mask_end (int).
2. When mask_start and mask_end are set, the masking function replaces characters from position mask_start to mask_end with '*'.
3. Default mask behavior (mask_start=0, mask_end=-1) preserves existing first/last character masking.
4. Frontend MUST provide inputs for mask_start and mask_end when action is "mask".

## ACCEPTANCE CRITERIA
- Column rule with mask_start=3, mask_end=7 on "1234567890" produces "123****890"
- Column rule with default mask preserves existing behavior
- Frontend mask configuration dialog shows start/end position inputs
- Existing disable and desensitize actions continue to work unchanged
