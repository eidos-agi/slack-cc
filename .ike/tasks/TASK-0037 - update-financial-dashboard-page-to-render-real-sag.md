---
id: TASK-0037
title: Update Financial dashboard page to render real Sage data
status: done
created: '2026-04-10'
priority: high
milestone: 'M-06: Sage Live on Staging Cerebro'
tags:
  - sage
  - cerebro
  - ui
dependencies:
  - 'M-06: Create cerebro/lib/data/financial.ts fetcher'
acceptance-criteria:
  - Page renders without errors
  - All 4 Sage metrics visible
  - No mock data in the render path
  - 'RLS working: unauthenticated access redirects to login'
  - Entity filter functional
updated: '2026-04-13'
---
app/dashboard/financial/page.tsx reads from /api/financial which calls fetchFinancialData from lib/data/financial.ts. Remove any mock data or placeholders. Render: revenue by entity (bar chart), P&L trend (line chart), AR aging (bucket chart), GL balances table. Use the same styling conventions as sales/page.tsx.

Done in same PR #16 — Financial page now fetches from /api/financial with mock fallback and LIVE/MOCK badge.
