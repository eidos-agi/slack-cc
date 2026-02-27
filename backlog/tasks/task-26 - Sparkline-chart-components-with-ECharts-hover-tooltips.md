---
id: TASK-26
title: Sparkline chart components with ECharts hover tooltips
status: Done
assignee: []
created_date: '2026-02-27 00:28'
labels:
  - cerebro
  - components
  - charts
milestone: Cerebro — Prospect Map
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Created reusable SparkLineCard and SparkColumnCard components for 12-month trailing trend visualization. Initially built with raw SVG, then migrated to ECharts for hover tooltip support. Used on the prospect map page for Accounts, By Brand, Active Pipeline (stacked columns by deal stage), and Customers.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created `components/charts/spark-card.tsx` with SparkLineCard (multi-line support, area fill) and SparkColumnCard (stacked bars). Uses ECharts via dynamic import with cerebro theme for consistent dark tooltip styling. Supports `formatTooltip` prop for custom value formatting. 12-month trailing mock data added to map page (TRAILING constant).
<!-- SECTION:FINAL_SUMMARY:END -->
