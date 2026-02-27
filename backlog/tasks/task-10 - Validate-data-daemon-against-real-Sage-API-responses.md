---
id: TASK-10
title: Validate data-daemon against real Sage API responses
status: To Do
assignee:
  - Daniel
created_date: '2026-02-26 21:39'
labels:
  - mvp
  - data-daemon
  - sage
milestone: MVP
dependencies: []
references:
  - infra/decisions/ADR-2026-01.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
data-daemon v1.4 has 82 tests but all against synthetic data. Real Sage Intacct API responses will have pagination quirks, rate limits, schema surprises, and edge cases that synthetic data doesn't surface. Once Alex provisions credentials, run the pipeline against real Sage and fix everything that breaks. This is where the gap between "tests pass" and "data lands correctly" gets closed. Blocked on: Alex provisioning Sage credentials.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 data-daemon successfully extracts at least 3 Sage endpoints with real data
- [ ] #2 Pagination, rate limiting, and error handling validated against real API
- [ ] #3 Bronze tables populated with real Sage data, not synthetic
<!-- AC:END -->
