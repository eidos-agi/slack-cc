---
id: TASK-1.15
title: Create custom properties matching Greenmark's waste industry needs
status: To Do
assignee:
  - Daniel
created_date: '2026-02-24 22:30'
updated_date: '2026-02-25 07:17'
labels:
  - hubspot
  - data-integration
  - architecture
dependencies:
  - TASK-1.12
parent_task_id: TASK-1
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
HubSpot's default properties are generic B2B/SaaS-oriented. Greenmark is a waste management company with industry-specific data needs. Create custom properties on the test account that would be useful for a waste hauler's CRM:\n\nCompany custom properties:\n- Service type (commercial, residential, construction, municipal)\n- Container type (front-load dumpster, rolloff, compactor, cart)\n- Service frequency (daily, 2x/week, weekly, on-call)\n- Service territory (NTX, Hometown/Indiana, Memphis)\n- Navusoft customer ID (for cross-referencing)\n\nDeal custom properties:\n- Contract type (monthly recurring, project-based, bid)\n- Service start date\n- Container count\n- Estimated monthly revenue\n\nContact custom properties:\n- Role type (site manager, billing, procurement, owner)\n\nThis shapes what data-daemon will eventually extract and maps to bronze table design.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Custom company properties created for waste industry fields
- [ ] #2 Custom deal properties created for contract types and service details
- [ ] #3 Custom contact properties created for role classification
- [ ] #4 Properties documented in EXPLORATION.md
- [ ] #5 Verified queryable via hs-api.sh properties command
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-25: Added dependency on TASK-1.12. Creating custom properties via API requires write scopes.
<!-- SECTION:NOTES:END -->
