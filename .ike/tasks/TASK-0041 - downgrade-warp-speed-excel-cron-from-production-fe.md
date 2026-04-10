---
id: TASK-0041
title: Downgrade warp-speed Excel cron from production feed to validation-only
status: To Do
created: '2026-04-10'
priority: medium
milestone: 'M-07: Excel Retired as Infrastructure'
tags:
  - sage
  - excel
  - retirement
dependencies:
  - 'M-06: Ship to staging via develop → PR → main pipeline'
acceptance-criteria:
  - 'warp-speed README explicitly states: this is a validation oracle, not a production
  feed'
  - Any automated run also invokes sage_excel_parity.py
  - Alex still receives the workbook as a weekly/monthly report (unchanged UX)
  - No downstream system reads from warp-speed's SQLite as a data source
---
If/when warp-speed has a scheduled run, change its identity: it is no longer the source of data for any downstream consumer. It runs daily to generate a fresh workbook for Alex AND to re-run the parity validation against Postgres gold. Its failure is a signal that Postgres drifted, not that Excel is broken. Document this in warp-speed's README.
