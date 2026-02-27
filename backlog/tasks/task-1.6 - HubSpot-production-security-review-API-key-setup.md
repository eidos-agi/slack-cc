---
id: TASK-1.6
title: HubSpot production security review + API key setup
status: In Progress
assignee:
  - Daniel
created_date: '2026-02-24 21:58'
updated_date: '2026-02-26 08:41'
labels:
  - hubspot
  - blocker
  - admin
dependencies: []
references:
  - notes/2026-02-24_155759_0399.md
parent_task_id: TASK-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Daniel now has admin access to production HubSpot (granted by Michael, Feb 25). Before enabling any API key that reads CRM data, run a security review: verify scopes are read-only, audit what the key can touch, confirm no write access. Then create the production Private App with minimal scopes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Daniel's HubSpot user has CRM Objects read scope available on PAK page
- [ ] #2 PAK regenerated with CRM Objects, Custom Objects, and HubDB scopes enabled
- [ ] #3 CLI commands like `hs custom-object list-schemas` succeed without scope errors
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Feb 26: Michael granted Daniel admin access to production HubSpot. Daniel prioritizing security review in the morning before enabling any API reads. Sandbox work (36 scopes mapped, REST API patterns proven) de-risks this — we know exactly what's needed.
<!-- SECTION:NOTES:END -->
