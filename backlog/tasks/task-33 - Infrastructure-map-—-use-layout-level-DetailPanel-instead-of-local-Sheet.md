---
id: TASK-33
title: Infrastructure map — use layout-level DetailPanel instead of local Sheet
status: Done
completed_date: '2026-02-27'
assignee: []
created_date: '2026-02-27 00:31'
labels:
  - cerebro
  - infrastructure
  - consistency
dependencies: []
references:
  - cerebro/components/detail-panel.tsx
  - cerebro/app/dashboard/infrastructure/page.tsx
  - cerebro/app/dashboard/map/page.tsx
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The infrastructure map page (app/dashboard/infrastructure/page.tsx) currently uses a shadcn Sheet for node details. It should use the same DetailPanel context/component that the prospect map uses — the layout-level slide-in sidebar defined in components/detail-panel.tsx. When a node is clicked, call useDetailPanel().open() to show specs in the shared panel. This keeps the drawer behavior consistent across all Cerebro pages.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Infrastructure map uses useDetailPanel().open() for node click details
- [ ] #2 Remove local Sheet import from infrastructure page
- [ ] #3 Detail panel slides in from right, compressing main content (same as prospect map)
- [ ] #4 Source, warehouse, and output node specs all render correctly in the shared panel
<!-- AC:END -->
