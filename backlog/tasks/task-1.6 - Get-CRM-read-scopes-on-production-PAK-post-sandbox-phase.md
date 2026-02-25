---
id: TASK-1.6
title: Get CRM read scopes on production PAK (post-sandbox phase)
status: To Do
assignee:
  - Daniel
created_date: '2026-02-24 21:58'
updated_date: '2026-02-25 07:17'
labels:
  - hubspot
  - blocker
  - admin
dependencies: []
references:
  - notes/2026-02-24_155759_0399.md
parent_task_id: TASK-1
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Daniel's HubSpot Personal Access Key (PAK) only has 6 developer-oriented scopes: cms.domains.read, developer.projects.write, developer.secrets.read/write, developer.test_accounts.read/write. The CRM Object, Custom Object, HubDB, and other data scopes are disabled on his PAK settings page — he can't toggle them himself. A HubSpot super admin needs to expand his user permissions so these scopes become available. Michael Nguyen is likely the super admin on the Greenmark HubSpot account (ID 244562652).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Daniel's HubSpot user has CRM Objects read scope available on PAK page
- [ ] #2 PAK regenerated with CRM Objects, Custom Objects, and HubDB scopes enabled
- [ ] #3 CLI commands like `hs custom-object list-schemas` succeed without scope errors
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-02-24: Deprioritized — test account (Greenmark Dev, ID 245316113) has Enterprise tier with full CRM scopes. No need to expand production PAK scopes for exploration phase. Revisit only when promoting to production.

2026-02-25: Renamed to clarify this is production-only. Not needed until connector is proven in sandbox. Depends on Michael enabling permissions via hubspot-setup.md instructions.
<!-- SECTION:NOTES:END -->
