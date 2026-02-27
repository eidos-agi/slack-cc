---
id: TASK-17
title: Create credential provisioning runbooks to unblock Alex bottleneck
status: To Do
assignee:
  - Daniel
created_date: '2026-02-26 21:40'
labels:
  - mvp
  - process
  - credentials
milestone: MVP
dependencies: []
references:
  - infra/vendors/sage-intacct/api-data-model.md
  - infra/vendors/hubspot/api-data-model.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Alex is the single person who provisions Sage and HubSpot credentials. If Alex is traveling, busy, or on vacation, the entire pipeline stays blocked. Create step-by-step runbooks Alex can follow (or delegate) for provisioning read-only API keys. Include screenshots, exact permission scopes needed, and a "hand this to your IT person" version so it doesn't require Alex personally.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Runbook written for Sage Intacct API key provisioning (read-only scopes)
- [ ] #2 Runbook written for HubSpot Private App token provisioning
- [ ] #3 Runbooks are GitHub-rendered markdown that Alex or a delegate can follow
<!-- AC:END -->
