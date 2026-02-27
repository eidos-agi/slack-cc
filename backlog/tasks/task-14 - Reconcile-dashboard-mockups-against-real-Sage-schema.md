---
id: TASK-14
title: Reconcile dashboard mockups against real Sage schema
status: To Do
assignee:
  - Daniel
created_date: '2026-02-26 21:39'
labels:
  - mvp
  - cerebro
  - dashboard
milestone: MVP
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Cerebro dashboard mockups were built with hardcoded Dec 2025 fake numbers. When real Sage data arrives, the schemas may not match. The mockup feedback loop happened against fiction. Once real Bronze data lands, compare actual Sage fields/values against what the mockups assume and identify every chart that needs rewriting. Depends on: real Sage data in Bronze tables.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every mockup chart mapped to real Sage fields (or flagged as unavailable)
- [ ] #2 Charts that need rewriting identified with specific schema gaps
- [ ] #3 At least Financial dashboard updated to use real Sage field names
<!-- AC:END -->
