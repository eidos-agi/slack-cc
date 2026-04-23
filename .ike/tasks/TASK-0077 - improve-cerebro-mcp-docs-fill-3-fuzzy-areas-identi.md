---
id: TASK-0077
title: Improve cerebro-mcp docs — fill 3 fuzzy areas identified by claude.ai
status: To Do
created: '2026-04-23'
priority: medium
tags:
  - cerebro-mcp
  - docs
  - developer-experience
acceptance-criteria:
  - claude.ai can explain the medallion pipeline shape when asked
  - qualityCheck evaluation method is documented and surfaceable
  - OAuth consent flow is documented end-to-end with sequence diagram or step list
---
claude.ai got a strong mental model from cerebro-mcp docs but identified 3 fuzzy areas that need better documentation:

1. **dbt/medallion shape upstream of sage_gold** — How bronze → silver → gold pipeline works, what the materialized views are, refresh cadence
2. **qualityCheck anomaly thresholds** — How they get evaluated (registry-only? separate checker?), what triggers alerts
3. **OAuth consent-page handoff sequence** — The full redirect → authorization_id → approve → bounce back flow beyond the basics

These are gaps in the cerebro-mcp docs tool's knowledge base. Fix by adding or updating docs that the docs tool can surface.
