---
id: TASK-0024
title: Deploy new sage_bronze migration to staging Supabase
status: Done
created: '2026-04-10'
priority: high
milestone: 'M-02: Sage Bronze Reality-Aligned'
tags:
  - sage
  - bronze
  - deploy
  - staging
dependencies:
  - 'M-02: Write new sage_bronze Postgres DDL from observed SQLite shape'
acceptance-criteria:
  - sage_bronze schema exists in staging Supabase
  - All 7 tables created and empty
  - Indexes verified via pg_indexes query
  - svc_etl_runner has INSERT/UPDATE on all tables
updated: '2026-04-10'
---
Run migrations against staging Supabase. Verify schema exists, tables are empty, all indexes created, grants correct. Do NOT run against production Supabase yet.

**Completion notes:** Applied via cerebro-migrations PR #4 (feat/auto-deploy-staging → develop merged 2026-04-10). Deploy-staging.yml auto-deploy fired, ran supabase db push --db-url against staging pooler, applied sage_bronze_rewrite migration successfully. Post-apply RBAC contract: 19/19 passed. Post-apply schema smoke: 16/16 passed ("Safe to promote"). Workflow reported job failure due to cosmetic Summary step bug (backticks in commit message got executed as bash command substitution) — this is being fixed in PR #5. The actual migration is live: sage_bronze schema + 7 tables (gl_accounts, gl_batches, gl_entries, ap_bills, ar_invoices, vendors, customers) with correct structure derived from warp-speed observed reality.</notes>
</invoke>
