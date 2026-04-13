---
id: TASK-0018
title: Archive infra/vendors/sage-intacct/ and create pointer README
status: Done
created: '2026-04-10'
priority: high
milestone: 'M-01: Session 21 Cleanup'
tags:
  - cleanup
  - infra
  - sage
acceptance-criteria:
  - archive/ subdirectory created with all 5 historical files
  - 'README.md written with last_verified: 2026-04-10'
  - README points to data-daemon, cerebro-migrations, warp-speed-excel
  - PR opened against infra main, CI passing, merged
updated: '2026-04-13'
---
Per Rhea Round 3 ruling: the stale Sage connection-spec is demo-grade documentation in an authoritative location. Create infra/vendors/sage-intacct/archive/ and move the old connection-spec.yaml, CHECKLIST.md, discovery-log.md, api-data-model.md, email-draft-jordan-permissions.md into it. Write a pointer README at the top level with last_verified date, pointing to data-daemon (pipeline), cerebro-migrations (schema), warp-speed-excel (semantic layer). Ship via PR to infra main.

**Completion notes:** Archived in session 22. PR #16 merged to infra.
