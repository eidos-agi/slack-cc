---
id: TASK-3
title: Connect Sage Intacct — first live data source
status: To Do
assignee: []
created_date: '2026-02-26 08:41'
labels:
  - sage
  - data-integration
  - critical-path
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Alex delivered Sage Intacct Web Services credentials (email 1 of 2 + developer license credentials email 2 of 2) on Feb 25. Jordan Alexander (Controller) forwarded a one-time token the same evening. Daniel has emailed Alex to schedule 5 min to pull setup across finish line. Once API key is created: connect to data-daemon, validate against synthetic data patterns, pull first real financial data.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Read-only API key created in Sage Intacct
- [ ] #2 data-daemon Sage connector pulls live data successfully
- [ ] #3 First bronze table populated with real Greenmark financial data
- [ ] #4 API key stored securely (Knox, not in code)
<!-- AC:END -->
