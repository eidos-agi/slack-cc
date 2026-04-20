---
id: TASK-0067
title: Wire Alerts page to cross-system thresholds
status: To Do
created: '2026-04-19'
priority: low
milestone: MS-0010
tags:
  - cerebro
  - data
  - cross-system
dependencies:
  - TASK-0061
  - TASK-0062
---
Replace hardcoded ALERTS array with real threshold-based alerts from gold views. E.g., margin below target, fleet utilization drop, AR aging spikes. Downstream of having multiple live data sources.
