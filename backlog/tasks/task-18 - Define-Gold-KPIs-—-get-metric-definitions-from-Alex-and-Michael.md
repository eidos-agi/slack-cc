---
id: TASK-18
title: Define Gold KPIs — get metric definitions from Alex and Michael
status: To Do
assignee:
  - Daniel
created_date: '2026-02-26 21:40'
labels:
  - mvp
  - architecture
  - stakeholder
milestone: MVP
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Gold schema is supposed to contain "business metrics" but nobody has defined which metrics. Alex's financial view (P&L, cost per route, revenue per customer) is different from Michael's ops view (fleet utilization, route efficiency, driver performance). The Gold layer requires domain knowledge that only lives in their heads. Schedule a working session to extract and document the top 10 KPIs for MVP.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Top 10 KPIs documented with exact definitions (formula, source system, entity scope)
- [ ] #2 Alex confirmed financial KPI definitions
- [ ] #3 Michael confirmed operational KPI definitions
- [ ] #4 KPIs mapped to source vendor fields
<!-- AC:END -->
