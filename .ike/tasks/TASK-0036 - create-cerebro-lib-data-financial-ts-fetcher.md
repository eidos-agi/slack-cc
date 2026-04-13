---
id: TASK-0036
title: Create cerebro/lib/data/financial.ts fetcher
status: done
created: '2026-04-10'
priority: high
milestone: 'M-06: Sage Live on Staging Cerebro'
tags:
  - sage
  - cerebro
  - ui
dependencies:
  - 'M-05: Run validation and fix until 100% parity'
acceptance-criteria:
  - financial.ts exists with typed interfaces
  - Fetches all 4 gold.sage_* tables in parallel
  - Handles deleted_at IS NULL filter
  - Exports toCsv() and toMarkdown() converters
  - Returns typed data for dashboard components
updated: '2026-04-13'
---
New file (or update existing) in cerebro that queries gold.sage_* tables via PostgREST. Mirrors the pattern in cerebro/lib/data/sales.ts. Parallel queries to sage_revenue_by_period, sage_pnl_by_entity, sage_ar_aging, sage_gl_balances. Filter by deleted_at IS NULL. Export typed converters (salesToCsv-style).

PR #16 on cerebro. financial.ts fetcher + API route + page wired with live/mock fallback.
