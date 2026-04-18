---
id: TASK-0051
title: Verify Financial page shows LIVE badge with correct revenue
status: In Progress
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
updated: '2026-04-17'
---
The thing we should have done in session 26. Open the Financial dashboard in a real browser, confirm LIVE badge shows (not MOCK), extract the revenue KPI, compare against sage_gold ground truth. Screenshot as evidence.


**Session 32 ground truth verification (2026-04-18):**

Queried sage_gold.entity_pnl directly via PostgREST (no browser needed):

Dec 2025 parity check — MATCHES Alex's Greenmark_Metrics:
- Hometown: $872,850.23 ✅
- NTX: $75,246.02 ✅

Data flows through Mar 2026:
- Mar 2026: HTN $917,594.75, NTX $104,909.37
- Feb 2026: HTN $834,644.17, NTX $66,389.47
- Jan 2026: HTN $897,679.09, NTX $61,063.95

Ground truth is LIVE and correct. Remaining: verify the rendered dashboard page shows these numbers (needs browser auth) and shows LIVE badge (not MOCK).
