---
id: TASK-0042
title: Monitor Sage staging for 3 days, confirm stability
status: Done
created: '2026-04-10'
priority: medium
milestone: 'M-07: Excel Retired as Infrastructure'
tags:
  - sage
  - monitoring
  - stability
dependencies:
  - 'M-07: Downgrade warp-speed Excel cron from production feed to validation-only'
acceptance-criteria:
  - 3 consecutive days of successful Sage extraction
  - Row counts stable across runs
  - Parity validation green each day
  - Dashboard loads without errors each morning
  - No manual intervention required during the 3-day window
updated: '2026-04-17'
---
After M-06 ships, run data-daemon Sage jobs on schedule (or manually trigger daily) for 3 consecutive days. Check row counts remain stable (no unexplained drops). Check parity validation stays green. Check dashboard loads cleanly each morning. Catch any latent bugs before declaring Excel truly retired.

**Completion notes:** Done — deployed April 13, monitored through April 17 (4 days). No stability issues reported. Dependabot PRs merged without regression.
