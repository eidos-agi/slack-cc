---
id: TASK-76
title: Decommission Greenmark data from AIC Supabase
status: To Do
assignee: []
created_date: '2026-02-27 20:34'
labels:
  - infra
  - supabase-migration
  - cleanup
dependencies:
  - TASK-73
  - TASK-74
  - TASK-75
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After all services are confirmed running on the new Greenmark Supabase, clean up the old AIC instance (zbscgmkkictwxoridyui). Soft-delete or archive any Greenmark-specific tables/data. Revoke any Greenmark-specific API keys. Document what was removed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All Greenmark services confirmed on new Supabase for 1+ week
- [ ] #2 Greenmark data soft-deleted or archived from AIC instance
- [ ] #3 Greenmark API keys revoked from AIC Supabase
- [ ] #4 Cleanup documented in infra repo
<!-- AC:END -->
