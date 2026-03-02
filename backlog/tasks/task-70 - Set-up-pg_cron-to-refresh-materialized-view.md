---
id: TASK-70
title: Set up pg_cron to refresh materialized view
status: To Do
assignee: []
created_date: '2026-02-27 08:35'
labels:
  - database
  - performance
milestone: m-1
dependencies:
  - TASK-63
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Configure Supabase pg_cron to run REFRESH MATERIALIZED VIEW ai.usage_analytics_hourly every 15 minutes. This keeps the dashboard analytics fast without querying raw usage_log for aggregates.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 pg_cron job created in Supabase
- [ ] #2 Refreshes every 15 minutes
- [ ] #3 Dashboard queries use the materialized view
- [ ] #4 No manual refresh needed
<!-- AC:END -->
