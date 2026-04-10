---
id: TASK-0023
title: Write new sage_bronze Postgres DDL from observed SQLite shape
status: To Do
created: '2026-04-10'
priority: high
milestone: 'M-02: Sage Bronze Reality-Aligned'
tags:
  - sage
  - bronze
  - migration
dependencies:
  - 'M-02: Delete old sage_bronze migration from cerebro-migrations'
acceptance-criteria:
  - All 7 tables defined with standard columns
  - Partial unique indexes on (source_id, entity)
  - Watermark indexes on incremental tables
  - Schema matches warp-speed observed structure (no hypothetical fields)
  - Migration applies cleanly to a fresh Postgres instance
---
New migration file in cerebro-migrations. Create sage_bronze schema. Create 7 tables matching observed warp-speed structure: gl_accounts, gl_batches, gl_entries, ap_bills, ar_invoices, vendors, customers. Every table has the elt-forge standard columns (id BIGSERIAL, source_id, source_system, entity, raw_data JSONB, row_hash, _job_id, synced_at, created_at, updated_at, deleted_at). Partial unique index on (source_id, entity) WHERE deleted_at IS NULL. Watermark index for incremental tables. Follow HubSpot bronze pattern in 20260308000700_hubspot_bronze.sql.
