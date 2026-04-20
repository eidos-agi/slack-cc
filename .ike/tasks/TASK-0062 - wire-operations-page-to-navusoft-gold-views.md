---
id: TASK-0062
title: Wire Operations page to Navusoft gold views
status: To Do
created: '2026-04-19'
priority: high
milestone: MS-0010
tags:
  - cerebro
  - navusoft
  - data
definition-of-done:
  - Operations page fetches from /api/operations
  - API route queries navusoft_gold views
  - Mock fallback preserved
  - LIVE badge on page
blocked_reason: Navusoft API server setup in progress (approved Apr 19-20 weekend)
---
Replace OPERATIONS, FLEET, RM_COSTS, REVENUE mock arrays. Operations is the core Navusoft page — route counts, service metrics, fleet utilization. Requires: navusoft bronze→silver→gold pipeline.
