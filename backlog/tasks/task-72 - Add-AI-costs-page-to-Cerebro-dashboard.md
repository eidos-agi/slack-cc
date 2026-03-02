---
id: TASK-72
title: Add AI costs page to Cerebro dashboard
status: To Do
assignee: []
created_date: '2026-02-27 08:35'
labels:
  - frontend
  - cerebro
  - dashboard
milestone: m-1
dependencies:
  - TASK-62
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build a /dashboard/ai-costs page in the Cerebro Next.js app that queries ai.usage_log directly. Shows cost trends, per-app breakdown, model comparison, and budget alerts. Complements the built-in dashboard on the gateway itself.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 New page at /dashboard/ai-costs in Cerebro
- [ ] #2 Charts: cost over time, by app, by model
- [ ] #3 Table of recent requests with drill-down
- [ ] #4 Budget alert when monthly cost exceeds threshold
<!-- AC:END -->
