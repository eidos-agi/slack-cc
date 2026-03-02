---
id: TASK-58
title: Built-in analytics dashboard
status: Done
assignee: []
created_date: '2026-02-27 08:22'
updated_date: '2026-02-27 08:29'
labels:
  - frontend
  - dashboard
milestone: m-1
dependencies:
  - TASK-2
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build /dashboard with HTMX + Tailwind CDN + Chart.js. Sections: KPI summary cards, usage-over-time chart, by-app and by-task pie charts, model health panel, API key usage table, recent requests live table. HTMX widgets auto-refresh. Materialized view for fast analytics queries.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 GET /dashboard serves HTML dashboard
- [ ] #2 KPI cards show requests today, cost today, avg latency, error rate
- [ ] #3 Charts render usage over time, by app, by task
- [ ] #4 Model health panel shows loaded models + memory
- [ ] #5 Recent requests table auto-refreshes via HTMX
- [ ] #6 Dashboard is protected by auth
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Built /dashboard with HTMX + Tailwind CDN + Chart.js. KPI cards (requests today, cost, avg latency, error rate), usage-over-time line chart, by-app and by-task doughnut charts, model health panel with memory/CPU, API key usage table, recent requests table (auto-refreshes every 5s via HTMX). Period selector (7/30/90 days).
<!-- SECTION:FINAL_SUMMARY:END -->
