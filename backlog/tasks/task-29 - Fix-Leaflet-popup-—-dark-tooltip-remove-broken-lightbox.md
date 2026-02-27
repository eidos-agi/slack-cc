---
id: TASK-29
title: 'Fix Leaflet popup — dark tooltip, remove broken lightbox'
status: Done
assignee: []
created_date: '2026-02-27 00:28'
labels:
  - cerebro
  - prospect-map
  - bugfix
milestone: Cerebro — Prospect Map
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replaced the broken Leaflet Popup (white box in dark mode, conflicting with detail panel click) with a dark-styled Leaflet Tooltip for hover. Added global CSS for `.leaflet-tooltip` matching cerebro dark theme. Clicking markers now only opens the detail panel.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed Popup from prospect-map.tsx, replaced with Tooltip (hover, direction top). Added dark tooltip CSS to globals.css matching cerebro theme (dark bg, blur, rounded). Tooltip shows company name, city/state, annual value, and stage.
<!-- SECTION:FINAL_SUMMARY:END -->
