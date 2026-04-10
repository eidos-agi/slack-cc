---
id: MS-0007
title: 'M-07: Excel Retired as Infrastructure'
status: open
created: '2026-04-10'
---
warp-speed keeps its identity as a validation oracle and Alex-deliverable. Its cron becomes a daily validation run, not a production feed. All downstream consumption flows through Postgres gold. Excel is a report, not a pipeline.
