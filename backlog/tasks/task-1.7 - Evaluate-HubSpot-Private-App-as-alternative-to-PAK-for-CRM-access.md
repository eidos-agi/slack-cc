---
id: TASK-1.7
title: Evaluate HubSpot Private App as alternative to PAK for CRM access
status: To Do
assignee:
  - Daniel
created_date: '2026-02-24 21:58'
updated_date: '2026-02-24 22:40'
labels:
  - hubspot
  - architecture
dependencies: []
references:
  - notes/2026-02-24_155759_0399.md
parent_task_id: TASK-1
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Evaluate creating a HubSpot Private App as an alternative to PAK for API access.

**Why this matters now:** Pipeline endpoint (`/crm/v3/pipelines/deals`) returns 403 with PAK — error says 'User level OAuth token is not allowed for this endpoint.' Private App tokens are app-level and may unlock this.

**Private App advantages:**
- App-level auth (not user-level)
- May unlock pipeline endpoint
- Granular scope control
- No 30-min token expiry (long-lived tokens)

**Private App disadvantages:**
- Requires HubSpot Super Admin access
- More setup overhead
- Different auth flow

**Decision:** Defer until after PAK scope expansion (TASK-1.12). If expanded PAK still can't read pipelines, then Private App becomes necessary.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Determined whether Daniel can create a Private App with current permissions
- [ ] #2 Documented: Private App scopes available vs PAK scopes available
- [ ] #3 Decision: PAK expansion vs Private App for data-daemon integration
- [ ] #4 If Private App chosen: app created and tested with CRM read access
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-24: Confirmed pipeline endpoint explicitly rejects user-level tokens. Deal stage names cannot be resolved without pipeline access. Private App is the only path to pipeline data.
<!-- SECTION:NOTES:END -->
