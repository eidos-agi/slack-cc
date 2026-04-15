---
id: TASK-0051
title: Verify Financial page shows LIVE badge with correct revenue
status: To Do
created: '2026-04-13'
priority: high
milestone: 'M-08: cerebro-verifier — Learning QA System'
tags:
  - verifier
  - sage
  - validation
dependencies:
  - Prove auth flow works end-to-end in browser
acceptance-criteria:
  - Financial page opens in browser after auth
  - LIVE badge visible (not MOCK DATA)
  - Revenue KPI extracted from rendered page
  - Revenue matches sage_gold.entity_pnl to within 1%
  - Screenshot saved as evidence
---
The thing we should have done in session 26. Open the Financial dashboard in a real browser, confirm LIVE badge shows (not MOCK), extract the revenue KPI, compare against sage_gold ground truth. Screenshot as evidence.
