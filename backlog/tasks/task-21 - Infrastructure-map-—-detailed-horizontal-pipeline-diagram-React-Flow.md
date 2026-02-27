---
id: TASK-21
title: Infrastructure map — detailed horizontal pipeline diagram (React Flow)
status: Done
completed_date: '2026-02-27'
assignee: []
created_date: '2026-02-27 00:27'
labels:
  - cerebro
  - infrastructure
  - react-flow
milestone: Cerebro — Infrastructure
dependencies: []
references:
  - .claude/plans/reflective-inventing-crab.md
  - cerebro/lib/data-sources.json
  - cerebro/app/dashboard/infrastructure/page.tsx
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace the current static infrastructure page with an interactive React Flow diagram showing the full data pipeline. More detail than the current version — similar to the rhea-diagrams created earlier but rendered as a horizontal pipeline in Cerebro.

Layout: 15 vendor source nodes (left) → medallion warehouse layers (center) → 6 output types (right). Each node is clickable and opens the detail panel with full system spec (API details, data fields, stakeholder).

Existing plan file: `.claude/plans/reflective-inventing-crab.md` has the full implementation spec.

Key additions vs plan:
- More intermediate steps/nodes in the pipeline (not just source → warehouse → output)
- Show data transformation stages
- Show entity routing (which data goes to which entity view)
- Animated edges showing data flow direction
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 React Flow installed and rendering
- [ ] #2 15 vendor source nodes with custom styling
- [ ] #3 Medallion warehouse node with Bronze/Silver/Gold layers
- [ ] #4 6 output type nodes
- [ ] #5 Clickable nodes open detail panel with full spec
- [ ] #6 Phase filter pills (All/P1/P2/P3) dim nodes by priority
- [ ] #7 Animated edges with status-based styling
- [ ] #8 MiniMap and zoom controls
- [ ] #9 Horizontal pipeline layout matching rhea-diagram detail level
- [ ] #10 Build passes clean
<!-- AC:END -->
