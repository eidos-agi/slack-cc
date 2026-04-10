---
id: TASK-0033
title: Write sage_excel_parity.py validation script
status: To Do
created: '2026-04-10'
priority: high
milestone: 'M-05: Excel Parity Proven'
tags:
  - sage
  - validation
  - script
dependencies:
  - 'M-05: Export warp-speed gold tables as golden fixtures'
acceptance-criteria:
  - Script exists and is executable
  - Loads all fixtures
  - Queries Postgres for each gold metric
  - Rounds to 2 decimal places
  - Normalizes date/NULL differences
  - Prints diff on mismatch
  - Exits 0 on full parity, non-zero on any failure
  - Runs in under 30 seconds
---
Python script at cerebro-migrations/validation/sage_excel_parity.py. Connects to staging Supabase + loads golden fixtures. For each gold metric, queries Postgres, compares to fixture. Normalizes platform differences (date types, NULL vs empty string, float precision). Exits non-zero on any mismatch. Prints detailed diff on failure. See VALIDATION doc for normalization rules and pattern examples.
