---
id: TASK-0068
title: Promote cerebro-telemetry to production
status: To Do
created: '2026-04-19'
priority: high
milestone: MS-0011
tags:
  - infra
  - telemetry
  - railway
definition-of-done:
  - cerebro-telemetry-production.up.railway.app/healthz returns 200
  - Volume attached
  - TELEMETRY_TOKEN set
---
Only develop exists. Create production service via railguey so cerebro-mcp and data-daemon can write to a prod endpoint. 5-minute job.
