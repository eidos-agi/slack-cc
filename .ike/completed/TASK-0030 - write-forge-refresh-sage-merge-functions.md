---
id: TASK-0030
title: Write forge.refresh_sage_* MERGE functions
status: Done
created: '2026-04-10'
priority: high
milestone: 'M-04: Sage Medallion Complete'
tags:
  - sage
  - gold
  - refresh
  - migration
dependencies:
  - 'M-04: Write sage_gold tables (4 initial metrics)'
acceptance-criteria:
  - 4 refresh functions exist in forge schema
  - All are SECURITY DEFINER
  - All use pg_advisory_lock/unlock
  - All use MERGE (not TRUNCATE+INSERT)
  - All soft-delete missing rows
  - All abort on empty source
  - svc_etl_runner has EXECUTE grant on all four
  - Calling refresh function populates gold table from silver
updated: '2026-04-13'
---
Four refresh functions, one per gold table. Each: SECURITY DEFINER, pg_advisory_lock, temp staging table, COUNT-based empty check, MERGE upsert, soft-delete rows no longer in staging, pg_advisory_unlock. Follow forge.refresh_pipeline_summary() pattern exactly. Grant EXECUTE to svc_etl_runner.

**Completion notes:** sage_gold.refresh_all() created in the silver/gold migration. Refreshes all 7 materialized views concurrently.
