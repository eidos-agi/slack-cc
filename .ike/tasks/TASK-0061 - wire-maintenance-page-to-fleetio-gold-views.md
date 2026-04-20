---
id: TASK-0061
title: Wire Maintenance page to Fleetio gold views
status: To Do
created: '2026-04-19'
priority: high
milestone: MS-0010
tags:
  - cerebro
  - fleetio
  - data
definition-of-done:
  - Maintenance page fetches from /api/maintenance
  - API route queries fleetio_gold views
  - Mock fallback preserved for dev
  - LIVE badge on page
blocked_reason: Fleetio bronze→gold pipeline not yet built in data-daemon
---
Replace WORK_ORDERS and RM_COSTS mock arrays with API calls to fleetio_gold views. Fleetio approved by Michael Apr 17. Requires: fleetio bronze→silver→gold pipeline in data-daemon, PostgREST API route in cerebro.
