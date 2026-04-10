---
id: TASK-0024
title: Deploy new sage_bronze migration to staging Supabase
status: To Do
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
---
Run migrations against staging Supabase. Verify schema exists, tables are empty, all indexes created, grants correct. Do NOT run against production Supabase yet.
