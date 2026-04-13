---
id: TASK-0022
title: Write superseding migration to drop and recreate sage_bronze
status: Done
created: '2026-04-10'
priority: high
milestone: 'M-02: Sage Bronze Reality-Aligned'
tags:
  - sage
  - bronze
  - cleanup
dependencies:
  - 'M-02: Dump warp-speed SQLite schema for all bronze_sage_intacct_* tables'
acceptance-criteria:
  - Old migration file deleted
  - No references to the old schema in cerebro-migrations
  - Rebuild branch created
updated: '2026-04-10'
---
The original plan said "delete the old migration file." That violates Supabase migration discipline — old migrations that have been applied to staging/production must stay in place. Instead, write a NEW migration at a later timestamp that drops sage_bronze CASCADE and recreates it with the correct structure derived from warp-speed observations. The old migration files become effectively superseded but remain in git as historical record. This approach: (1) maintains migration history, (2) applies cleanly to staging which has the old schema, (3) is safe on production which has mock data. Do NOT delete the 20260308000100_sage_bronze.sql, 20260308000300_row_hash.sql, or 20260308000400_entity_check_memphis.sql files.

**Completion notes:** Superseded rather than deleted. New migration 20260410060000_sage_bronze_rewrite.sql drops sage_bronze CASCADE and recreates from observed reality. Old migrations (20260308000100, 20260308000300, 20260308000400) kept in git history per Supabase discipline.
