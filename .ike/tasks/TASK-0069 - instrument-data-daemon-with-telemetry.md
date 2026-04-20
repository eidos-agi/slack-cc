---
id: TASK-0069
title: Instrument data-daemon with telemetry
status: To Do
created: '2026-04-19'
priority: high
milestone: MS-0011
tags:
  - data-daemon
  - telemetry
  - observability
definition-of-done:
  - data-daemon emits telemetry events on every extraction run
  - 'Events include: source, table, row_count, duration_ms, status'
  - Events visible in cerebro-telemetry /query
---
data-daemon is the most critical pipeline and emits zero telemetry events. Add the Python telemetry client to emit extraction start/complete/error, gold refresh timing, and row counts.
