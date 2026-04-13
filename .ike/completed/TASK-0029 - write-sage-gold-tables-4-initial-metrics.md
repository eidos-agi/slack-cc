---
id: TASK-0029
title: Write sage_gold tables (4 initial metrics)
status: Done
created: '2026-04-10'
priority: high
milestone: 'M-04: Sage Medallion Complete'
tags:
  - sage
  - gold
  - migration
dependencies:
  - 'M-04: Write sage_silver materialized views'
acceptance-criteria:
  - All 4 gold tables created in gold schema
  - Regular tables, not views
  - RLS enabled with entity_id filter policy
  - _last_job_id, _refreshed_at, deleted_at columns present
  - Unique constraints on natural keys
  - 'Grants: authenticated SELECT, svc_etl_runner INSERT/UPDATE'
updated: '2026-04-13'
---
New migration in cerebro-migrations. Create 4 gold tables as regular TABLES (not materialized views) following ADR-2026-04: gold.sage_revenue_by_period, gold.sage_pnl_by_entity, gold.sage_ar_aging, gold.sage_gl_balances. Each with entity_id, _last_job_id, _refreshed_at, deleted_at columns. RLS enabled. Unique constraint on natural keys. Follow hubspot gold.pipeline_summary pattern.

**Completion notes:** sage_gold: gl_summary, entity_pnl, ap_aging. Real P&L numbers showing. Refresh function created. PR #19.
