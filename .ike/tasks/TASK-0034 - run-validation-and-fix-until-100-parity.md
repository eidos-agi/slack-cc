---
id: TASK-0034
title: Run validation and fix until 100% parity
status: To Do
created: '2026-04-10'
priority: high
milestone: 'M-05: Excel Parity Proven'
tags:
  - sage
  - validation
  - debugging
dependencies:
  - 'M-05: Write sage_excel_parity.py validation script'
acceptance-criteria:
  - 100% parity on revenue by entity × month
  - 100% parity on P&L by entity (proven to $0.00 delta)
  - 100% parity on AR aging buckets
  - 100% parity on GL balances
  - Script exits 0
  - No normalization rules added that hide real behavioral differences
---
Run sage_excel_parity.py against staging. Expect failures. Per VALIDATION doc protocol: read the diff, check the fixture (Excel is right), check the query (does it replicate Excel logic?), check the source data (does bronze have the same rows?), fix the pipeline (not the test), re-run. Continue until every metric matches to 2 decimal places for every entity × period combination.
