---
id: TASK-27
title: Layout-level detail panel — slide-in sidebar that compresses content
status: Done
assignee: []
created_date: '2026-02-27 00:28'
labels:
  - cerebro
  - layout
  - ux
milestone: Cerebro — UX Polish
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replaced the overlay Sheet (Radix Dialog) with a layout-level slide-in detail panel. When opened, main content compresses to make room. Any page in Cerebro can use `useDetailPanel()` context to open/close it. First consumer: prospect map company detail.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created `components/detail-panel.tsx` with DetailPanelProvider context and DetailPanel component. Modified `app/dashboard/layout.tsx` to wrap content in provider and render panel alongside main. Panel is 380px, transitions with `transition-[width]`, has sticky header with close button and scrollable content area. Map page migrated from Sheet to useDetailPanel().
<!-- SECTION:FINAL_SUMMARY:END -->
