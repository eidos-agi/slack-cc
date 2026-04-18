---
id: MS-0006
title: 'M-06: Sage Live on Staging Cerebro'
status: closed
created: '2026-04-10'
---
Update cerebro/lib/data/financial.ts (or create it) to query gold.sage_*. Update Financial and Executive Summary dashboards. Remove mock fallbacks. Ship via develop → PR → main. Michael's staging dashboard shows real Sage numbers.

**Closed:** Done since session 26. Financial + Executive dashboards deployed to staging + production 2026-04-13. Live data via PostgREST with mock fallback removed for entities with real data. LIVE badge shows on Financial page.
