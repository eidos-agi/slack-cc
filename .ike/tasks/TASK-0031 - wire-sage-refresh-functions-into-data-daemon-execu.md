---
id: TASK-0031
title: Wire sage refresh functions into data-daemon executor
status: done
created: '2026-04-10'
priority: high
milestone: 'M-04: Sage Medallion Complete'
tags:
  - sage
  - data-daemon
  - executor
dependencies:
  - 'M-04: Write forge.refresh_sage_* MERGE functions'
acceptance-criteria:
  - Executor calls silver REFRESH before gold refresh
  - Executor calls all 4 sage refresh functions
  - Order of calls is correct (bronze → silver → gold)
  - Errors in any step logged to daemon.job_logs
  - Full run end-to-end populates gold tables from fresh bronze
updated: '2026-04-13'
---
Update data-daemon/src/jobs/executor.py to call forge.refresh_sage_* functions after bronze load + silver refresh completes. Mirror how HubSpot refreshes are chained. Ensure order: bronze → silver refresh → gold refresh. Verify post-sync smoke tests run after gold refresh.

Already implemented — executor.py line 362-366, _GOLD_REFRESH_MAP["sage-intacct"] calls sage_gold.refresh_all(). Single function handles silver + gold atomically.
