---
id: TASK-22
title: Add lasso/polygon selection to Leaflet prospect map
status: To Do
assignee: []
created_date: '2026-02-27 00:27'
labels:
  - cerebro
  - prospect-map
  - leaflet
milestone: Cerebro — Prospect Map
dependencies: []
references:
  - cerebro/components/map/prospect-map.tsx
  - cerebro/components/map/lazy-prospect-map.tsx
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add the ability to draw a freeform loop/polygon on the Leaflet map to select all companies within the drawn area. This enables spatial filtering — "show me everything in this neighborhood."

Options:
- `leaflet-lasso` plugin — lightweight, draws a lasso path
- `leaflet-draw` plugin — full drawing toolbar (polygon, rectangle, circle)
- Custom implementation using Leaflet's drawing events

Selected companies should populate the detail panel or filter the company cards below. Alt+lasso could add to existing selection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 User can draw a freeform polygon on the map
- [ ] #2 All markers inside the polygon are selected
- [ ] #3 Selected companies are highlighted or filtered
- [ ] #4 Clear selection button to reset
- [ ] #5 Works with existing filter state
<!-- AC:END -->
