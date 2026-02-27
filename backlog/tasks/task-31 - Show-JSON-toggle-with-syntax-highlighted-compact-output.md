---
id: TASK-31
title: Show JSON toggle with syntax-highlighted compact output
status: Done
assignee: []
created_date: '2026-02-27 00:28'
labels:
  - cerebro
  - prospect-map
  - ai-readable
milestone: Cerebro — Prospect Map
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Added a JSON toggle button (Code icon) in the filter bar. When active, renders compact syntax-highlighted JSON right below the filters for quick AI scraping. No whitespace indentation, wraps to screen width like flowing text. Colors work in both light and dark mode.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added `showJson` boolean to MapFilterState. Code icon button in filter bar toggles it. ColoredJson component does regex-based syntax highlighting (keys=blue, strings=green, numbers=amber, booleans=red). CSS classes in globals.css with separate light/dark oklch color sets. Compact JSON with `break-words` wrapping, positioned right below filters for AI visibility.
<!-- SECTION:FINAL_SUMMARY:END -->
