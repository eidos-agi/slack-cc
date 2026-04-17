---
id: TASK-0032
title: Export warp-speed gold tables as golden fixtures
status: Done
created: '2026-04-10'
priority: high
milestone: 'M-05: Excel Parity Proven'
tags:
  - sage
  - validation
  - fixtures
dependencies:
  - 'M-04: Wire sage refresh functions into data-daemon executor'
acceptance-criteria:
  - JSON fixtures exist for every gold_sage_* table in warp-speed
  - Fixtures committed to cerebro-migrations/validation/fixtures/sage/
  - Manifest file records source commit hash and extraction date
  - Fixtures are non-empty (verify row counts match warp-speed SQLite)
updated: '2026-04-17'
---
Run warp-speed's SPA export to generate JSON snapshots of every gold_sage_* table. Copy the resulting files to cerebro-migrations/validation/fixtures/sage/. These are immutable snapshots of proven reality. Sign them with the date and warp-speed commit hash so we know what version of the workbook they came from.

PR cerebro-migrations#21. 72 entity_pnl, 696 gl_summary, 18 ap_aging rows. Manifest with source commit hash.

**Completion notes:** Done — fixtures in cerebro-migrations/validation/fixtures/sage/ (entity_pnl.json, gl_summary.json, ap_aging.json, manifest.json).
