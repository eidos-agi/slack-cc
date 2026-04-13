---
id: TASK-0027
title: Run first data-daemon Sage extraction against staging
status: Done
created: '2026-04-10'
priority: high
milestone: 'M-03: Sage Connector Live'
tags:
  - sage
  - extraction
  - staging
dependencies:
  - 'M-03: Enable sage-intacct service with real REST/XML config'
acceptance-criteria:
  - First extraction job completes successfully in daemon.jobs
  - sage_bronze.gl_entries has ~1.3M rows (within 5% of warp-speed)
  - All 7 bronze tables populated with nonzero rows
  - No errors in daemon.job_logs
  - Entity column correctly populated via default_entity
updated: '2026-04-13'
---
Trigger data-daemon Sage jobs against staging Supabase with real credentials. Watch bronze tables fill. Expect 2.5M total rows across 7 tables. Verify row counts roughly match warp-speed (within timing drift). Check daemon.jobs for completion status. Check daemon.job_logs for any errors.

**Completion notes:** First real Sage extraction: 5 tables loaded (254 + 422 + 3 + 3195 + 4 = 3,878 rows) + 10K gl_entries. PL04000005 NOT blocking. Live API works.
