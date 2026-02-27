---
id: TASK-43
title: Get FleetIO production API key from Robert Heath
status: To Do
assignee:
  - Robert Heath
created_date: '2026-02-27 03:11'
labels:
  - fleetio
  - blocker
  - waiting-on-robert
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Sandbox has no real data. Robert owns the FleetIO account and needs to generate a production API key (read-only) so we can pull work orders, vehicles, and parts inventory into the warehouse. This blocks R&M cost category mapping (m-fleet-3).

MC mission: m-fleet-2 | Initiative: init-fleet (Connect FleetIO)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Read-only production API key generated in FleetIO
- [ ] #2 Key securely shared and stored in Knox
- [ ] #3 Test API call confirms access to work orders and vehicles
<!-- AC:END -->
