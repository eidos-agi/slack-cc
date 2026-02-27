---
id: TASK-30
title: Interactive legend with click/alt+click filtering
status: Done
assignee: []
created_date: '2026-02-27 00:28'
labels:
  - cerebro
  - prospect-map
  - ux
milestone: Cerebro — Prospect Map
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Made the prospect map legend interactive. Click a stage to single-select (isolate), click again to show all. Alt+click to multi-select (toggle individual stages). Dimmed items show filtered-out stages. Customer row clears all stage filters.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Legend items are now buttons with handleLegendClick handler. Click = isolate one stage (or clear if already isolated). Alt/Meta+click = toggle multi-select. Opacity dims filtered-out stages. Hint text "click / ⌥+click" shown under Legend title. Wired to existing filters.stages state.
<!-- SECTION:FINAL_SUMMARY:END -->
