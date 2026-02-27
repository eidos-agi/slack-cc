---
id: TASK-25
title: Add Memphis as third entity across all Cerebro dashboards
status: Done
assignee: []
created_date: '2026-02-27 00:28'
labels:
  - cerebro
  - entity
  - memphis
milestone: Cerebro — Prospect Map
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Added Memphis (Greenmark's nascent Tennessee entity) to the entire Cerebro dashboard system — entity context, entity selector, mock prospect data (10 companies around Memphis TN), and all dashboard mock data (revenue, costs, fleet, operations). Updated all 9+ dashboard pages that index by entity.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added `memphis` to Entity type union, LABELS, header selector. Added 10 Memphis-area companies to mock-prospects.ts. Added Memphis data to all entity-keyed objects in mock-data.ts (REVENUE, REVENUE_BY_MONTH, DISPOSAL_COST, RM_COSTS, OPERATIONS, TOTAL_COSTS, COST_BREAKDOWN, FLEET). Updated entity-specific branches in operations, drivers, maintenance, people, and executive dashboard pages. All pages compile clean.
<!-- SECTION:FINAL_SUMMARY:END -->
