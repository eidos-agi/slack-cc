---
id: TASK-1.16
title: Add create/write commands to hs-api.sh for seeding data
status: To Do
assignee:
  - Daniel
created_date: '2026-02-24 22:30'
updated_date: '2026-02-24 22:39'
labels:
  - hubspot
  - tooling
dependencies:
  - TASK-1.12
parent_task_id: TASK-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add create/write commands to hs-api.sh for seeding test data. Blocked until PAK scopes are expanded (TASK-1.12) since current scopes lack `crm.objects.{contacts,companies,deals}.write`.

Commands to add:
- `create <type> '<json>'` — create a single record
- `update <type> <id> '<json>'` — update a record
- `batch-create <type> '<json-array>'` — batch create up to 100 records
- `associate <from-type> <from-id> <to-type> <to-id> <type>` — create associations

**Verified:** Batch read works (`POST /crm/v3/objects/{type}/batch/read`), so batch create should follow same pattern once scopes allow it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 create command works for contacts, companies, deals
- [ ] #2 create-batch command works for bulk seeding
- [ ] #3 associate command links records together
- [ ] #4 create-property command creates custom properties
- [ ] #5 Safety check: warns if default account is production
<!-- AC:END -->
