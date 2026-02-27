---
id: TASK-12
title: Add pipeline heartbeat and failure alerting — Day 1 monitoring
status: To Do
assignee:
  - Daniel
created_date: '2026-02-26 21:39'
labels:
  - mvp
  - monitoring
  - data-daemon
milestone: MVP
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
QA Monitoring is Phase 2 but pipeline failures are Day 1. If the Sage sync breaks at 2am, nobody knows — the dashboard shows stale data silently. Need at minimum: last successful sync timestamp visible in Cerebro, basic failure alerting (email or Slack), and a data freshness indicator on each dashboard widget so users know if they're looking at today's data or last week's.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Last successful sync timestamp stored and queryable per vendor
- [ ] #2 Failure alerting sends notification when a sync fails
- [ ] #3 Cerebro dashboard shows data freshness indicator per data source
<!-- AC:END -->
